from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

SENSORS = [
    ("decision", "Decision"),
    ("reason", "Reason"),
    ("error", "Last error"),
]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    controller = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MarstekSenecSensor(entry, controller, key, name) for key, name in SENSORS])

class MarstekSenecSensor(SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, entry: ConfigEntry, controller, key: str, name: str) -> None:
        self.entry = entry
        self.controller = controller
        self.key = key
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{key}"

    async def async_added_to_hass(self) -> None:
        self.controller.add_listener(self._handle_controller_update)

    async def async_will_remove_from_hass(self) -> None:
        self.controller.remove_listener(self._handle_controller_update)

    @callback
    def _handle_controller_update(self) -> None:
        self.async_write_ha_state()

    @property
    def native_value(self):
        if self.key == "decision":
            return self.controller.last_decision
        if self.key == "reason":
            return self.controller.last_reason
        if self.key == "error":
            return self.controller.last_error
        return None

    @property
    def extra_state_attributes(self):
        return {
            "last_power_w": self.controller.last_power,
            "last_soc_percent": self.controller.last_soc,
            "last_mode": self.controller.last_mode,
            "last_action_called": self.controller.last_action_called,
        }
