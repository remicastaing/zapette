"""Interrupteur « Contrôle actif » (persistant)."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import PlugCoordinator
from .entity import ZapetteTvEntity


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    if coordinator := entry.runtime_data.plug:
        async_add_entities([ControlSwitch(coordinator)])


class ControlSwitch(ZapetteTvEntity, SwitchEntity):
    _attr_icon = "mdi:shield-home"

    def __init__(self, coordinator: PlugCoordinator) -> None:
        super().__init__(coordinator, "control_active")

    @property
    def is_on(self) -> bool:
        return self.coordinator.logic.control_active

    async def async_turn_on(self, **kwargs: Any) -> None:
        self.coordinator.async_set_control(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        self.coordinator.async_set_control(False)
