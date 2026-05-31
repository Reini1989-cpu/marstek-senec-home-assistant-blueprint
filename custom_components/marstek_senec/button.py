from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MODE_AUTO, MODE_MANUAL

BUTTONS = [
    (MODE_AUTO, "Force AUTO"),
    (MODE_MANUAL, "Force MANUAL"),
]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    controller = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MarstekSenecButton(entry, controller, mode, name) for mode, name in BUTTONS])

class MarstekSenecButton(ButtonEntity):
    _attr_has_entity_name = True

    def __init__(self, entry: ConfigEntry, controller, mode: str, name: str) -> None:
        self.entry = entry
        self.controller = controller
        self.mode = mode
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_force_{mode}"

    async def async_press(self) -> None:
        await self.controller.async_force_mode(self.mode)
