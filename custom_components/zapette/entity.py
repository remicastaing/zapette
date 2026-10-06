"""Classe de base des entités de la télévision (appareil « Zapette – <Télévision> »)."""

from __future__ import annotations

from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity

from .const import DOMAIN
from .access import AccessManager
from .coordinator import PlugCoordinator
from .session_coordinator import SessionCoordinator
from .settings import Child


class ZapetteTvEntity(Entity):
    """Entité rattachée à l'appareil de la télévision, mise à jour par la prise ou par l'accès."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, coordinator: PlugCoordinator | AccessManager | SessionCoordinator, key: str) -> None:
        self.coordinator = coordinator
        self._attr_translation_key = key
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.entry.entry_id)},
            name=f"Zapette – {coordinator.tv_name}",
            manufacturer="Zapette",
            model="Télévision",
        )

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self.coordinator.async_add_listener(self._handle_update))

    @callback
    def _handle_update(self) -> None:
        self.async_write_ha_state()


def child_device(subentry_id: str, child: Child) -> DeviceInfo:
    return DeviceInfo(
        identifiers={(DOMAIN, subentry_id)},
        name=f"Zapette – {child.name}",
        manufacturer="Zapette",
        model="Enfant",
    )


class ZapetteChildEntity(Entity):
    """Entité d'un enfant (appareil « Zapette – <Prénom> »), mise à jour par les sessions."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, sessions: SessionCoordinator, subentry_id: str, child: Child, key: str) -> None:
        self.sessions = sessions
        self.child_id = subentry_id
        self._attr_translation_key = key
        self._attr_unique_id = f"{subentry_id}_{key}"
        self._attr_device_info = child_device(subentry_id, child)

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self.sessions.async_add_listener(self._handle_update))

    @callback
    def _handle_update(self) -> None:
        self.async_write_ha_state()
