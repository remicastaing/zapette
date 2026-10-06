"""Capteurs Zapette : quota du jour par enfant ; prise ; derniers accès et pile du clavier."""

from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry, ConfigSubentry
from homeassistant.const import PERCENTAGE, EntityCategory, UnitOfPower, UnitOfTime
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.event import async_track_time_change
from homeassistant.util import dt as dt_util

from .const import SUBENTRY_CHILD
from .access import AccessManager
from .coordinator import PlugCoordinator
from .entity import ZapetteChildEntity, ZapetteTvEntity, child_device
from .rules import REASONS
from .session_coordinator import SessionCoordinator
from .settings import DAYS, Child, SettingsError

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    access: AccessManager = entry.runtime_data.access
    sessions: SessionCoordinator = entry.runtime_data.sessions
    async_add_entities([CurrentUserSensor(sessions), PlannedEndSensor(sessions)])
    keypad: list[ZapetteTvEntity] = [LastDeniedSensor(access), LastGrantedSensor(access)]
    if access.adapter:
        keypad.append(KeypadBatterySensor(access))
    async_add_entities(keypad)
    if coordinator := entry.runtime_data.plug:
        tv_entities: list[ZapetteTvEntity] = [LastOutageSensor(coordinator)]
        if coordinator.power_entity:
            tv_entities.append(PowerSensor(coordinator))
        async_add_entities(tv_entities)
    for subentry in entry.subentries.values():
        if subentry.subentry_type != SUBENTRY_CHILD:
            continue
        try:
            child = Child.from_dict(dict(subentry.data))
        except SettingsError as err:
            _LOGGER.error("Enfant « %s » ignoré : paramétrage invalide (%s)", subentry.title, err.key)
            continue
        sid = subentry.subentry_id
        async_add_entities(
            [
                QuotaTodaySensor(entry, subentry, child),
                ConsumedTodaySensor(sessions, sid, child),
                RemainingTodaySensor(sessions, sid, child),
                NextSlotSensor(sessions, sid, child),
            ],
            config_subentry_id=sid,
        )


class QuotaTodaySensor(SensorEntity):
    """Quota applicable aujourd'hui (hors bonus, pas encore géré)."""

    _attr_has_entity_name = True
    _attr_translation_key = "quota_today"
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_should_poll = False

    def __init__(self, entry: ConfigEntry, subentry: ConfigSubentry, child: Child) -> None:
        self._child = child
        self._attr_unique_id = f"{subentry.subentry_id}_quota_today"
        self._attr_icon = child.icon
        self._attr_device_info = child_device(subentry.subentry_id, child)

    async def async_added_to_hass(self) -> None:
        self._update()
        self.async_on_remove(async_track_time_change(self.hass, self._midnight, hour=0, minute=0, second=1))

    @callback
    def _midnight(self, _now: Any) -> None:
        self._update()
        self.async_write_ha_state()

    def _update(self) -> None:
        day = DAYS[dt_util.now().weekday()]
        rules = self._child.rules
        self._attr_native_value = rules.quota_minutes[day] if rules.is_allowed_day(day) else 0
        self._attr_extra_state_attributes = {
            "enabled": self._child.enabled,
            "weekly_quota_minutes": dict(rules.quota_minutes),
            "slots_today": [str(slot) for slot in rules.slots[day]],
        }


class PowerSensor(ZapetteTvEntity, SensorEntity):
    """Puissance mesurée par le capteur de la prise, en W."""

    _attr_device_class = SensorDeviceClass.POWER
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: PlugCoordinator) -> None:
        super().__init__(coordinator, "power")

    @property
    def native_value(self) -> float | None:
        return self.coordinator.logic.power


class LastOutageSensor(ZapetteTvEntity, SensorEntity):
    """Début de la dernière perte de la prise (en cours ou terminée)."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:power-plug-off"

    def __init__(self, coordinator: PlugCoordinator) -> None:
        super().__init__(coordinator, "last_outage")

    @property
    def native_value(self) -> datetime | None:
        start = self.coordinator.open_outage or (self.coordinator.outages[-1]["start"] if self.coordinator.outages else None)
        return dt_util.parse_datetime(start) if start else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        outages = self.coordinator.outages
        since = (dt_util.utcnow() - timedelta(hours=24)).isoformat()
        recent = sum(1 for o in outages if o["end"] >= since) + (1 if self.coordinator.open_outage else 0)
        duration = None if self.coordinator.open_outage or not outages else outages[-1]["duration"]
        return {"duration": duration, "outages_24h": recent}


class LastDeniedSensor(ZapetteTvEntity, SensorEntity):
    """Motif du dernier refus (profil et heure en attributs)."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = list(REASONS)
    _attr_icon = "mdi:account-cancel"

    def __init__(self, access: AccessManager) -> None:
        super().__init__(access, "last_denied")

    @property
    def native_value(self) -> str | None:
        last = self.coordinator.last_denied
        return last["reason"] if last else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        last = self.coordinator.last_denied or {}
        return {key: last.get(key) for key in ("profile", "at", "source")}


class LastGrantedSensor(ZapetteTvEntity, SensorEntity):
    """Heure du dernier accès accordé (profil en attribut)."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:account-check"

    def __init__(self, access: AccessManager) -> None:
        super().__init__(access, "last_granted")

    @property
    def native_value(self) -> datetime | None:
        last = self.coordinator.last_granted
        return dt_util.parse_datetime(last["at"]) if last else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        last = self.coordinator.last_granted or {}
        return {key: last.get(key) for key in ("profile", "kind", "source")}


class KeypadBatterySensor(ZapetteTvEntity, SensorEntity):
    """Dernier niveau de pile connu du clavier."""

    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, access: AccessManager) -> None:
        super().__init__(access, "keypad_battery")

    @property
    def native_value(self) -> int | None:
        return self.coordinator.status.battery


# --- Sessions (tranche 3) -----------------------------------------------------------


class CurrentUserSensor(ZapetteTvEntity, SensorEntity):
    """Prénom du profil en session, ou `none` (traduit « aucun »)."""

    _attr_icon = "mdi:account-eye"

    def __init__(self, sessions: SessionCoordinator) -> None:
        super().__init__(sessions, "current_user")

    @property
    def native_value(self) -> str:
        session = self.coordinator.session
        return session.name if session else "none"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        session = self.coordinator.session
        return {"kind": session.kind if session else None}


class PlannedEndSensor(ZapetteTvEntity, SensorEntity):
    """Heure de coupure prévue de la session en cours."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:timer-off-outline"

    def __init__(self, sessions: SessionCoordinator) -> None:
        super().__init__(sessions, "planned_end")

    @property
    def native_value(self) -> datetime | None:
        return self.coordinator.planned_end()[0]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {"reason": self.coordinator.planned_end()[1]}


class _MinutesSensor(ZapetteChildEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_suggested_display_precision = 0


class ConsumedTodaySensor(_MinutesSensor):
    """Temps de télé consommé aujourd'hui (remis à zéro à minuit) ; statistiques à long terme."""

    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_icon = "mdi:timer-sand"

    def __init__(self, sessions: SessionCoordinator, subentry_id: str, child: Child) -> None:
        super().__init__(sessions, subentry_id, child, "consumed_today")

    @property
    def native_value(self) -> float:
        return round(self.sessions.logic.consumed_now(self.child_id, dt_util.utcnow()) / 60, 1)


class RemainingTodaySensor(_MinutesSensor):
    """Quota du jour + bonus − consommé, borné à 0."""

    _attr_icon = "mdi:timer-outline"

    def __init__(self, sessions: SessionCoordinator, subentry_id: str, child: Child) -> None:
        super().__init__(sessions, subentry_id, child, "remaining_today")

    @property
    def native_value(self) -> float:
        return round(self.sessions.logic.remaining(self.child_id, dt_util.utcnow()) / 60, 1)


class NextSlotSensor(ZapetteChildEntity, SensorEntity):
    """Début de la prochaine plage autorisée (un jour où l'enfant peut regarder)."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:calendar-clock"

    def __init__(self, sessions: SessionCoordinator, subentry_id: str, child: Child) -> None:
        super().__init__(sessions, subentry_id, child, "next_slot")

    @property
    def native_value(self) -> datetime | None:
        slot = self.sessions.logic.next_slot(self.child_id, dt_util.utcnow())
        return slot[0] if slot else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        slot = self.sessions.logic.next_slot(self.child_id, dt_util.utcnow())
        return {"end": slot[1].isoformat() if slot else None}
