"""Boutons « Allumer la télé », « Couper la télé » et « Arrêter la session »."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import PlugCoordinator
from .entity import ZapetteTvEntity
from .rules import END_STOPPED
from .services import request, turn_off
from .session_coordinator import SessionCoordinator


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    sessions: SessionCoordinator = entry.runtime_data.sessions
    async_add_entities([StopSessionButton(sessions)])
    if coordinator := entry.runtime_data.plug:
        async_add_entities([PowerButton(coordinator, sessions, True), PowerButton(coordinator, sessions, False)])


class PowerButton(ZapetteTvEntity, ButtonEntity):
    def __init__(self, coordinator: PlugCoordinator, sessions: SessionCoordinator, on: bool) -> None:
        super().__init__(coordinator, "turn_on_tv" if on else "turn_off_tv")
        self._sessions = sessions
        self._on = on
        self._attr_icon = "mdi:television" if on else "mdi:television-off"

    async def async_press(self) -> None:
        if self._on:
            request(self.coordinator, True)
        else:
            turn_off(self.coordinator, self._sessions)


class StopSessionButton(ZapetteTvEntity, ButtonEntity):
    """Termine la session en cours (motif `stopped`) et coupe la prise."""

    _attr_icon = "mdi:stop-circle-outline"

    def __init__(self, sessions: SessionCoordinator) -> None:
        super().__init__(sessions, "stop_session")

    async def async_press(self) -> None:
        self.coordinator.async_stop(END_STOPPED)
