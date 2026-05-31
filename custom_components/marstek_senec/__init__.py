from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_AUTO_SCRIPT,
    CONF_CHARGE_THRESHOLD,
    CONF_CHECK_INTERVAL,
    CONF_MANUAL_SCRIPT,
    CONF_MODE_SENSOR,
    CONF_POWER_SENSOR,
    CONF_SOC_EMPTY_THRESHOLD,
    CONF_SOC_FULL_THRESHOLD,
    CONF_SOC_SENSOR,
    DEFAULT_CHARGE_THRESHOLD,
    DEFAULT_CHECK_INTERVAL,
    DEFAULT_SOC_EMPTY_THRESHOLD,
    DEFAULT_SOC_FULL_THRESHOLD,
    DOMAIN,
    INVALID_STATES,
    MODE_AUTO,
    MODE_MANUAL,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = ["sensor", "button"]

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    controller = MarstekSenecController(hass, entry)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = controller
    await controller.async_start()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    controller: MarstekSenecController | None = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    if controller:
        controller.async_stop()
    return unload_ok

async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)

class MarstekSenecController:
    """Simple controller that switches Marstek AUTO/MANUAL from reference battery state."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self._unsub_interval = None
        self.last_decision: str | None = None
        self.last_reason: str | None = None
        self.last_error: str | None = None
        self.last_power: float | None = None
        self.last_soc: float | None = None
        self.last_mode: str | None = None
        self.last_action_called: str | None = None
        self._listeners: list = []

    @property
    def options(self) -> dict:
        return {**self.entry.data, **self.entry.options}

    async def async_start(self) -> None:
        interval = int(self.options.get(CONF_CHECK_INTERVAL, DEFAULT_CHECK_INTERVAL))
        self._unsub_interval = async_track_time_interval(
            self.hass, self._async_interval_update, timedelta(seconds=interval)
        )
        await self.async_evaluate()

    def async_stop(self) -> None:
        if self._unsub_interval:
            self._unsub_interval()
            self._unsub_interval = None

    @callback
    def _async_interval_update(self, now) -> None:
        self.hass.async_create_task(self.async_evaluate())

    def _read_float(self, entity_id: str) -> float | None:
        state = self.hass.states.get(entity_id)
        if state is None or str(state.state).lower() in INVALID_STATES:
            return None
        try:
            return float(state.state)
        except (TypeError, ValueError):
            return None

    def _read_text(self, entity_id: str) -> str | None:
        state = self.hass.states.get(entity_id)
        if state is None or str(state.state).lower() in INVALID_STATES:
            return None
        return str(state.state).strip()

    async def async_evaluate(self) -> None:
        opts = self.options
        power_sensor = opts[CONF_POWER_SENSOR]
        soc_sensor = opts[CONF_SOC_SENSOR]
        mode_sensor = opts[CONF_MODE_SENSOR]

        power = self._read_float(power_sensor)
        soc = self._read_float(soc_sensor)
        current_mode = self._read_text(mode_sensor)

        self.last_power = power
        self.last_soc = soc
        self.last_mode = current_mode
        self.last_error = None
        self.last_action_called = None

        if power is None or soc is None or current_mode is None:
            self.last_decision = None
            self.last_reason = "Skipped: one or more sensor values are unknown or unavailable."
            self.last_error = self.last_reason
            _LOGGER.debug("Skipping evaluation because a sensor value is invalid")
            self._notify_entities()
            return

        charge_threshold = float(opts.get(CONF_CHARGE_THRESHOLD, DEFAULT_CHARGE_THRESHOLD))
        soc_empty = float(opts.get(CONF_SOC_EMPTY_THRESHOLD, DEFAULT_SOC_EMPTY_THRESHOLD))
        soc_full = float(opts.get(CONF_SOC_FULL_THRESHOLD, DEFAULT_SOC_FULL_THRESHOLD))

        reasons: list[str] = []
        desired = MODE_MANUAL
        if power > charge_threshold:
            desired = MODE_AUTO
            reasons.append(f"charging power {power:.0f} W > {charge_threshold:.0f} W")
        if soc >= soc_full:
            desired = MODE_AUTO
            reasons.append(f"SOC {soc:.1f}% >= {soc_full:.1f}%")
        if soc < soc_empty:
            desired = MODE_AUTO
            reasons.append(f"SOC {soc:.1f}% < {soc_empty:.1f}%")

        if not reasons:
            reasons.append("no AUTO condition is active")

        self.last_decision = desired
        self.last_reason = "; ".join(reasons)

        if current_mode.lower() == desired:
            _LOGGER.debug("Marstek already in desired mode %s", desired)
            self._notify_entities()
            return

        script_entity = opts[CONF_AUTO_SCRIPT] if desired == MODE_AUTO else opts[CONF_MANUAL_SCRIPT]
        try:
            await self._async_call_script(script_entity)
            self.last_action_called = script_entity
            _LOGGER.info("Called %s because %s", script_entity, self.last_reason)
        except Exception as err:  # noqa: BLE001
            self.last_error = f"Failed to call {script_entity}: {err}"
            _LOGGER.exception("Failed to call script %s", script_entity)
        self._notify_entities()

    async def async_force_mode(self, mode: str) -> None:
        opts = self.options
        script_entity = opts[CONF_AUTO_SCRIPT] if mode == MODE_AUTO else opts[CONF_MANUAL_SCRIPT]
        await self._async_call_script(script_entity)
        self.last_decision = mode
        self.last_reason = "Manual force button pressed"
        self.last_action_called = script_entity
        self.last_error = None
        self._notify_entities()

    async def _async_call_script(self, entity_id: str) -> None:
        domain, service = entity_id.split(".", 1)
        await self.hass.services.async_call(
            domain,
            service,
            {},
            blocking=True
        )

    def add_listener(self, update_callback) -> None:
        self._listeners.append(update_callback)

    def remove_listener(self, update_callback) -> None:
        if update_callback in self._listeners:
            self._listeners.remove(update_callback)

    def _notify_entities(self) -> None:
        for update_callback in list(self._listeners):
            update_callback()
