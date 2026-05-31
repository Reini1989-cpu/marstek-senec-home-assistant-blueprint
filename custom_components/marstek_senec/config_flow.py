from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import selector

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
)


def _schema(user_input: dict | None = None) -> vol.Schema:
    user_input = user_input or {}
    return vol.Schema(
        {
            vol.Required(CONF_POWER_SENSOR, default=user_input.get(CONF_POWER_SENSOR)): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor")
            ),
            vol.Required(CONF_SOC_SENSOR, default=user_input.get(CONF_SOC_SENSOR)): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor")
            ),
            vol.Required(CONF_MODE_SENSOR, default=user_input.get(CONF_MODE_SENSOR)): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor")
            ),
            vol.Required(CONF_AUTO_SCRIPT, default=user_input.get(CONF_AUTO_SCRIPT)): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="script")
            ),
            vol.Required(CONF_MANUAL_SCRIPT, default=user_input.get(CONF_MANUAL_SCRIPT)): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="script")
            ),
            vol.Optional(
                CONF_CHARGE_THRESHOLD,
                default=user_input.get(CONF_CHARGE_THRESHOLD, DEFAULT_CHARGE_THRESHOLD),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(min=0, max=10000, step=50, unit_of_measurement="W")
            ),
            vol.Optional(
                CONF_SOC_EMPTY_THRESHOLD,
                default=user_input.get(CONF_SOC_EMPTY_THRESHOLD, DEFAULT_SOC_EMPTY_THRESHOLD),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(min=0, max=100, step=1, unit_of_measurement="%")
            ),
            vol.Optional(
                CONF_SOC_FULL_THRESHOLD,
                default=user_input.get(CONF_SOC_FULL_THRESHOLD, DEFAULT_SOC_FULL_THRESHOLD),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(min=0, max=100, step=1, unit_of_measurement="%")
            ),
            vol.Optional(
                CONF_CHECK_INTERVAL,
                default=user_input.get(CONF_CHECK_INTERVAL, DEFAULT_CHECK_INTERVAL),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(min=10, max=3600, step=10, unit_of_measurement="s")
            ),
        }
    )


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None):
        if user_input is not None:
            await self.async_set_unique_id("marstek_senec_controller")
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title="Marstek SENEC Controller", data=user_input)

        return self.async_show_form(step_id="user", data_schema=_schema(), errors={})

    @staticmethod
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict | None = None):
        current = {**self.config_entry.data, **self.config_entry.options}
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        return self.async_show_form(step_id="init", data_schema=_schema(current), errors={})
