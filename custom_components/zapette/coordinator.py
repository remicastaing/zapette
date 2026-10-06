"""Coordinateur de la prise : branche Home Assistant sur la logique pure de `plug.py`."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STOP, UnitOfPower
from homeassistant.core import CALLBACK_TYPE, Event, EventStateChangedData, HomeAssistant, State, callback
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.event import async_track_point_in_utc_time, async_track_state_change_event
from homeassistant.helpers.start import async_at_started
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (
    CONF_PLUG_ENTITY,
    CONF_POWER_ENTITY,
    CONF_STANDBY_CUT,
    CONF_STANDBY_DELAY,
    CONF_STANDBY_THRESHOLD,
    CONF_TOLERATE_MANUAL,
    CONF_TV_NAME,
    DEFAULT_STANDBY_CUT,
    DEFAULT_STANDBY_DELAY,
    DEFAULT_STANDBY_THRESHOLD,
    DEFAULT_TOLERATE_MANUAL,
    DOMAIN,
    EVENT_BYPASS,
    EVENT_PLUG_BACK,
    EVENT_PLUG_LOST,
    EVENT_STANDBY,
)
from .plug import (
    PROBLEM_OFF_FAILED,
    PROBLEM_UNREACHABLE,
    Bypass,
    Command,
    Effect,
    PlugBack,
    PlugLogic,
    PlugLost,
    PlugSettings,
    Standby,
)

_LOGGER = logging.getLogger(__name__)

STORAGE_VERSION = 1
OUTAGE_RETENTION = timedelta(days=90)
OUTAGE_MAX = 500
DATA_LOGIC = "logic"
ISSUE_STANDBY_CUT = "standby_cut_disabled"


def settings_from_options(options: dict[str, Any]) -> PlugSettings:
    return PlugSettings(
        tolerate_manual=options.get(CONF_TOLERATE_MANUAL, DEFAULT_TOLERATE_MANUAL),
        standby_threshold=float(options.get(CONF_STANDBY_THRESHOLD, DEFAULT_STANDBY_THRESHOLD)),
        standby_delay=timedelta(minutes=options.get(CONF_STANDBY_DELAY, DEFAULT_STANDBY_DELAY)),
        standby_cut=bool(options.get(CONF_STANDBY_CUT, DEFAULT_STANDBY_CUT)),
    )


def plug_state(state: State | None) -> str | None:
    """"on" / "off", ou None si la prise est indisponible, inconnue ou absente."""
    if state is None or state.state not in ("on", "off"):
        return None
    return state.state


def power_watts(state: State | None) -> float | None:
    """Puissance en W, ou None si absente, illisible ou dans une unité inconnue."""
    if state is None:
        return None
    try:
        value = float(state.state)
    except ValueError:
        return None
    unit = state.attributes.get("unit_of_measurement")
    if unit in (None, UnitOfPower.WATT):
        return value
    if unit == UnitOfPower.KILO_WATT:
        return value * 1000
    return None


class EntryState:
    """`Store` `zapette.<entry_id>` partagé par la prise et le clavier (sections distinctes)."""

    def __init__(self, store: Store, data: dict[str, Any]) -> None:
        self._store = store
        self.data = data

    @classmethod
    async def async_load(cls, hass: HomeAssistant, entry_id: str) -> EntryState:
        store: Store = Store(hass, STORAGE_VERSION, f"{DOMAIN}.{entry_id}")
        return cls(store, await store.async_load() or {})

    def _payload(self) -> dict[str, Any]:
        return {**self.data, "saved_at": dt_util.utcnow().isoformat()}

    @callback
    def save(self) -> None:
        self._store.async_delay_save(self._payload, 1)

    async def async_flush(self) -> None:
        await self._store.async_save(self._payload())


class PlugCoordinator:
    """Une instance par entrée chargée ; la logique (`PlugLogic`) survit aux rechargements."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, logic: PlugLogic, state: EntryState) -> None:
        self.hass = hass
        self.entry = entry
        self.logic = logic
        self._entry_state = state
        self._data = state.data
        self._listeners: list[Callable[[], None]] = []
        self._effect_listeners: list[Callable[[Effect], None]] = []
        self._unsubs: list[CALLBACK_TYPE] = []
        self._timer: CALLBACK_TYPE | None = None
        self._tasks: set[Any] = set()

    @classmethod
    async def async_create(cls, hass: HomeAssistant, entry: ConfigEntry, state: EntryState) -> PlugCoordinator:
        data = state.data
        data.setdefault("control_active", True)
        data.setdefault("outages", [])
        data.setdefault("open_outage", None)

        plug = entry.data[CONF_PLUG_ENTITY]
        settings = settings_from_options(dict(entry.options))
        logics: dict[str, PlugLogic] = hass.data.setdefault(DOMAIN, {}).setdefault(DATA_LOGIC, {})
        logic = logics.get(entry.entry_id)
        if logic is None:
            # Démarrage : état souhaité « coupée » ; une perte ouverte avant l'arrêt est close.
            logic = logics[entry.entry_id] = PlugLogic(plug, settings, data["control_active"])
            if data["open_outage"]:
                end = data.get("saved_at") or data["open_outage"]
                _add_outage(data, data["open_outage"], end, interrupted=True)
                data["open_outage"] = None
        else:
            # Rechargement : l'état est conservé, aucune commande.
            if logic.plug_entity != plug:
                _LOGGER.info("Prise changée : %s → %s (aucune commande)", logic.plug_entity, plug)
                logic.change_plug(plug)
            logic.update_settings(settings, dt_util.utcnow())
        return cls(hass, entry, logic, state)

    # --- cycle de vie ---------------------------------------------------------

    async def async_start(self) -> None:
        self._sync_standby_issue()
        self._unsubs.append(self.hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, self._on_stop))
        # Au démarrage, attendre que Home Assistant ait chargé la prise (MQTT) avant d'observer.
        self._unsubs.append(async_at_started(self.hass, self._async_observe))

    async def _async_observe(self, _hass: HomeAssistant) -> None:
        entities = [self.plug_entity] + ([self.power_entity] if self.power_entity else [])
        self._unsubs.append(async_track_state_change_event(self.hass, entities, self._on_state_change))
        now = dt_util.utcnow()
        effects = self.logic.observe_power(power_watts(self._state(self.power_entity)), now) if self.power_entity else []
        effects += self.logic.observe_plug(plug_state(self._state(self.plug_entity)), now)
        if not self.power_entity:
            effects += self.logic.observe_power(None, now)
        self._apply(effects)

    async def async_unload(self) -> None:
        for unsub in self._unsubs:
            unsub()
        self._unsubs.clear()
        if self._timer:
            self._timer()
            self._timer = None

    # --- lecture pour les entités --------------------------------------------

    @property
    def tv_name(self) -> str:
        return self.entry.data.get(CONF_TV_NAME, self.entry.title)

    @property
    def plug_entity(self) -> str:
        return self.entry.data[CONF_PLUG_ENTITY]

    @property
    def power_entity(self) -> str | None:
        return self.entry.data.get(CONF_POWER_ENTITY) or None

    @property
    def outages(self) -> list[dict[str, Any]]:
        return self._data["outages"]

    @property
    def open_outage(self) -> str | None:
        return self._data["open_outage"]

    @callback
    def async_add_listener(self, listener: Callable[[], None]) -> CALLBACK_TYPE:
        self._listeners.append(listener)
        return lambda: self._listeners.remove(listener)

    @callback
    def async_add_effect_listener(self, listener: Callable[[Effect], None]) -> CALLBACK_TYPE:
        """Prévenu de chaque effet **avant** son exécution (ex. : la session finit avant la coupure)."""
        self._effect_listeners.append(listener)
        return lambda: self._effect_listeners.remove(listener)

    # --- demandes ------------------------------------------------------------

    @callback
    def async_request(self, on: bool) -> None:
        """Allumer/couper à la demande du parent ; lève `PlugRefused`."""
        self._apply(self.logic.request(on, dt_util.utcnow()))

    @callback
    def async_set_control(self, active: bool) -> None:
        self._apply(self.logic.set_control(active, dt_util.utcnow()))
        self._data["control_active"] = active
        self._save()

    # --- événements Home Assistant -------------------------------------------

    @callback
    def _on_state_change(self, event: Event[EventStateChangedData]) -> None:
        now = dt_util.utcnow()
        new_state = event.data["new_state"]
        if event.data["entity_id"] == self.plug_entity:
            self._apply(self.logic.observe_plug(plug_state(new_state), now))
        else:
            self._apply(self.logic.observe_power(power_watts(new_state), now))

    @callback
    def _on_timer(self, now: datetime) -> None:
        self._timer = None
        self._apply(self.logic.tick(now))

    @callback
    def _on_stop(self, _event: Event) -> None:
        # Le Store vide les écritures différées à l'arrêt : `saved_at` date alors l'arrêt.
        self._save()

    # --- effets --------------------------------------------------------------

    @callback
    def _apply(self, effects: list[Effect]) -> None:
        base = {"entry_id": self.entry.entry_id, "entity_id": self.plug_entity}
        for effect in effects:
            for effect_listener in list(self._effect_listeners):
                effect_listener(effect)
            match effect:
                case Command(on=on):
                    task = self.hass.async_create_task(self._async_command(on), eager_start=True)
                    self._tasks.add(task)
                    task.add_done_callback(self._tasks.discard)
                case Bypass(tolerated=tolerated):
                    _LOGGER.warning("Prise %s allumée sans autorisation (tolérée : %s)", self.plug_entity, tolerated)
                    self.hass.bus.async_fire(EVENT_BYPASS, {**base, "tolerated": tolerated})
                case Standby(power=power, cut=cut):
                    self.hass.bus.async_fire(EVENT_STANDBY, {**base, "power": power, "cut": cut})
                case PlugLost(at=at):
                    _LOGGER.warning("Prise %s injoignable", self.plug_entity)
                    self._data["open_outage"] = at.isoformat()
                    self._save()
                    self.hass.bus.async_fire(EVENT_PLUG_LOST, base)
                case PlugBack(lost_at=lost_at, at=at) as back:
                    _LOGGER.info("Prise %s de nouveau joignable après %s", self.plug_entity, back.duration)
                    _add_outage(self._data, lost_at.isoformat(), at.isoformat())
                    self._data["open_outage"] = None
                    self._save()
                    duration = round(back.duration.total_seconds())
                    self.hass.bus.async_fire(EVENT_PLUG_BACK, {**base, "lost_at": lost_at.isoformat(), "duration": duration})
        self._sync_issues()
        self._schedule()
        for listener in list(self._listeners):
            listener()

    async def _async_command(self, on: bool) -> None:
        service = "turn_on" if on else "turn_off"
        try:
            await self.hass.services.async_call("switch", service, {"entity_id": self.plug_entity}, blocking=True)
        except Exception as err:  # noqa: BLE001 — toute erreur d'envoi est un échec de commande
            _LOGGER.warning("Commande %s de la prise %s en échec : %s", service, self.plug_entity, err)
            self._apply(self.logic.command_failed(on, dt_util.utcnow()))

    @callback
    def _schedule(self) -> None:
        if self._timer:
            self._timer()
            self._timer = None
        deadline = self.logic.next_deadline()
        if deadline is not None:
            self._timer = async_track_point_in_utc_time(self.hass, self._on_timer, deadline)

    @callback
    def _sync_standby_issue(self) -> None:
        """Option « Couper la prise en veille » désactivée : réparation visible (H9)."""
        issue_id = f"{ISSUE_STANDBY_CUT}_{self.entry.entry_id}"
        if self.logic.settings.standby_cut:
            ir.async_delete_issue(self.hass, DOMAIN, issue_id)
            return
        ir.async_create_issue(
            self.hass,
            DOMAIN,
            issue_id,
            is_fixable=False,
            severity=ir.IssueSeverity.WARNING,
            translation_key=ISSUE_STANDBY_CUT,
            translation_placeholders={"tv_name": self.tv_name},
        )

    @callback
    def _sync_issues(self) -> None:
        problem = self.logic.problem
        placeholders = {"tv_name": self.tv_name, "entity_id": self.plug_entity}
        for key in (PROBLEM_UNREACHABLE, PROBLEM_OFF_FAILED):
            issue_id = f"plug_{key}_{self.entry.entry_id}"
            if problem == key:
                ir.async_create_issue(
                    self.hass,
                    DOMAIN,
                    issue_id,
                    is_fixable=False,
                    severity=ir.IssueSeverity.ERROR,
                    translation_key=f"plug_{key}",
                    translation_placeholders=placeholders,
                )
            else:
                ir.async_delete_issue(self.hass, DOMAIN, issue_id)

    # --- persistance ---------------------------------------------------------

    def _state(self, entity_id: str | None) -> State | None:
        return self.hass.states.get(entity_id) if entity_id else None

    @callback
    def _save(self) -> None:
        self._entry_state.save()


def _add_outage(data: dict[str, Any], start: str, end: str, interrupted: bool = False) -> None:
    start_dt, end_dt = dt_util.parse_datetime(start), dt_util.parse_datetime(end)
    outage: dict[str, Any] = {
        "start": start,
        "end": end,
        "duration": round((end_dt - start_dt).total_seconds()) if start_dt and end_dt else None,
    }
    if interrupted:
        outage["interrupted"] = True
    limit = (dt_util.utcnow() - OUTAGE_RETENTION).isoformat()
    data["outages"] = [o for o in data["outages"] if o["end"] >= limit][-(OUTAGE_MAX - 1) :] + [outage]
