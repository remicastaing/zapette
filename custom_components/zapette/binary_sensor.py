"""Capteurs binaires : prise (alimentée, souhaitée, joignable, problème, veille) et clavier."""

from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from homeassistant.util import dt as dt_util

from .access import AccessManager
from .coordinator import PlugCoordinator
from .entity import ZapetteChildEntity, ZapetteTvEntity
from .const import SUBENTRY_CHILD
from .session_coordinator import SessionCoordinator
from .settings import Child, SettingsError


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    access: AccessManager = entry.runtime_data.access
    sessions: SessionCoordinator = entry.runtime_data.sessions
    async_add_entities([SessionActive(sessions)])
    for subentry in entry.subentries.values():
        if subentry.subentry_type != SUBENTRY_CHILD:
            continue
        try:
            child = Child.from_dict(dict(subentry.data))
        except SettingsError:
            continue
        sid = subentry.subentry_id
        async_add_entities([InSession(sessions, sid, child), AllowedNow(sessions, sid, child)], config_subentry_id=sid)
    keypad: list[ZapetteTvEntity] = [KeypadLocked(access)]
    if access.adapter:
        keypad.append(KeypadAvailable(access))
    async_add_entities(keypad)
    coordinator: PlugCoordinator | None = entry.runtime_data.plug
    if not coordinator:
        return
    entities: list[ZapetteTvEntity] = [
        TvPowered(coordinator),
        DesiredPower(coordinator),
        PlugReachable(coordinator),
        PlugProblem(coordinator),
    ]
    if coordinator.power_entity:
        entities.append(StandbySensor(coordinator))
    async_add_entities(entities)


class TvPowered(ZapetteTvEntity, BinarySensorEntity):
    """État de la prise vu par Zapette."""

    _attr_device_class = BinarySensorDeviceClass.POWER

    def __init__(self, coordinator: PlugCoordinator) -> None:
        super().__init__(coordinator, "tv_powered")

    @property
    def available(self) -> bool:
        return bool(self.coordinator.logic.available)

    @property
    def is_on(self) -> bool:
        return self.coordinator.logic.is_on

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {"plug_entity": self.coordinator.plug_entity}


class DesiredPower(ZapetteTvEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.POWER

    def __init__(self, coordinator: PlugCoordinator) -> None:
        super().__init__(coordinator, "desired_power")

    @property
    def is_on(self) -> bool:
        return self.coordinator.logic.desired_on

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {"tolerated": self.coordinator.logic.tolerated}


class PlugReachable(ZapetteTvEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: PlugCoordinator) -> None:
        super().__init__(coordinator, "plug_reachable")

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.logic.available)


class PlugProblem(ZapetteTvEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: PlugCoordinator) -> None:
        super().__init__(coordinator, "plug_problem")

    @property
    def is_on(self) -> bool:
        return self.coordinator.logic.problem is not None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {"reason": self.coordinator.logic.problem}


class StandbySensor(ZapetteTvEntity, BinarySensorEntity):
    _attr_icon = "mdi:sleep"

    def __init__(self, coordinator: PlugCoordinator) -> None:
        super().__init__(coordinator, "standby")

    @property
    def is_on(self) -> bool:
        return self.coordinator.logic.standby

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        low_since = self.coordinator.logic.low_since
        return {"low_power_since": low_since.isoformat() if low_since else None}


class KeypadLocked(ZapetteTvEntity, BinarySensorEntity):
    """Verrouillage anti‑essais en cours."""

    _attr_icon = "mdi:lock-alert"

    def __init__(self, access: AccessManager) -> None:
        super().__init__(access, "keypad_locked")

    @property
    def is_on(self) -> bool:
        return self.coordinator.is_locked()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        guard = self.coordinator.guard
        until = guard.locked_until
        return {
            "until": until.isoformat() if until else None,
            "recent_failures": guard.recent_failures(dt_util.utcnow()),
        }


class KeypadAvailable(ZapetteTvEntity, BinarySensorEntity):
    """Clavier joignable selon Zigbee2MQTT ; inconnu tant que rien n'a été publié."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, access: AccessManager) -> None:
        super().__init__(access, "keypad_available")

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.status.available

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {"topic": self.coordinator.keypad_topic}


# --- Sessions (tranche 3) -----------------------------------------------------------


class SessionActive(ZapetteTvEntity, BinarySensorEntity):
    """Une session est en cours."""

    _attr_device_class = BinarySensorDeviceClass.RUNNING
    _attr_icon = "mdi:television-play"

    def __init__(self, sessions: SessionCoordinator) -> None:
        super().__init__(sessions, "session_active")

    @property
    def is_on(self) -> bool:
        return self.coordinator.session is not None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        session = self.coordinator.session
        if session is None:
            return {"profile": None, "kind": None, "started_at": None, "source": None, "ignore_rules": None}
        return {
            "profile": session.name,
            "kind": session.kind,
            "started_at": session.started_at.isoformat(),
            "source": session.source,
            "ignore_rules": session.ignore_rules,
        }


class InSession(ZapetteChildEntity, BinarySensorEntity):
    """Cet enfant regarde la télé."""

    _attr_icon = "mdi:television-play"

    def __init__(self, sessions: SessionCoordinator, subentry_id: str, child: Child) -> None:
        super().__init__(sessions, subentry_id, child, "in_session")

    @property
    def is_on(self) -> bool:
        return self.sessions.logic.in_session(self.child_id)


class AllowedNow(ZapetteChildEntity, BinarySensorEntity):
    """L'enfant pourrait ouvrir une session maintenant selon ses règles (autre session ignorée)."""

    _attr_icon = "mdi:television-guide"

    def __init__(self, sessions: SessionCoordinator, subentry_id: str, child: Child) -> None:
        super().__init__(sessions, subentry_id, child, "allowed_now")

    @property
    def is_on(self) -> bool:
        return self.sessions.logic.refusal(self.child_id, dt_util.utcnow()) is None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {"reason": self.sessions.logic.refusal(self.child_id, dt_util.utcnow())}
