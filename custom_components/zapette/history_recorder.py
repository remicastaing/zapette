"""Enregistreur de l'historique : branche Home Assistant sur le journal pur de `history.py`.

`Store` dédié `zapette.<entry_id>.history`, écrit au plus une fois par minute (H1) ; le journal vit
dans `hass.data` : présent au chargement = rechargement (rien n'est clos), absent = démarrage.
Les pertes de la prise restent dans le `Store` d'état (tranche 1) et sont fusionnées à la lecture.
"""

from __future__ import annotations

from datetime import datetime
import logging
import shutil
from typing import TYPE_CHECKING, Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.core import CALLBACK_TYPE, Event, HomeAssistant, callback
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .coordinator import EntryState, PlugCoordinator
from .history import (
    ORIGIN_CONTROL_INACTIVE,
    ORIGIN_OTHER,
    ORIGIN_PARENT,
    ORIGIN_TOLERATED,
    T_PLUG_LOST,
    T_SESSION,
    HistoryLog,
    entry_start,
    iso,
    parse,
)
from .plug import Bypass, Effect as PlugEffect, Standby

if TYPE_CHECKING:
    from .session import SessionEnded
    from .session_coordinator import SessionCoordinator

_LOGGER = logging.getLogger(__name__)

HISTORY_VERSION = 1
SAVE_DELAY = 60  # s : au plus une écriture par minute (clarification 2026-10-04)
DATA_HISTORY = "history"


def history_store(hass: HomeAssistant, entry_id: str) -> Store:
    return Store(hass, HISTORY_VERSION, f"{DOMAIN}.{entry_id}.history")


async def _async_load(hass: HomeAssistant, store: Store) -> dict[str, Any]:
    """Contenu du `Store`, ou {} ; un fichier illisible est mis de côté (jamais d'exception)."""
    try:
        data = await store.async_load()
    except Exception:  # noqa: BLE001 — journal illisible : on repart vide (FR-014)
        path = hass.config.path(".storage", store.key)
        backup = f"{path}.corrupt-{dt_util.utcnow().strftime('%Y%m%dT%H%M%S')}"
        try:
            await hass.async_add_executor_job(shutil.copyfile, path, backup)
        except OSError:
            backup = "(copie impossible)"
        _LOGGER.warning("Historique Zapette illisible (%s) : mis de côté sous %s, historique vide", store.key, backup)
        return {}
    return data if isinstance(data, dict) else {}


class HistoryRecorder:
    """Un par entrée chargée ; appelé par les coordinateurs, sans minuterie propre."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, log: HistoryLog, store: Store, state: EntryState) -> None:
        self.hass = hass
        self.entry = entry
        self.log = log
        self._store = store
        self._state = state
        self.plug: PlugCoordinator | None = None
        self.sessions: SessionCoordinator | None = None
        self._unsubs: list[CALLBACK_TYPE] = []

    @classmethod
    async def async_create(cls, hass: HomeAssistant, entry: ConfigEntry, state: EntryState) -> HistoryRecorder:
        store = history_store(hass, entry.entry_id)
        logs: dict[str, HistoryLog] = hass.data.setdefault(DOMAIN, {}).setdefault(DATA_HISTORY, {})
        log = logs.get(entry.entry_id)
        now = dt_util.utcnow()
        if log is None:
            # Démarrage : périodes ouvertes closes à l'arrêt, période « Home Assistant arrêté ».
            data = await _async_load(hass, store)
            log = logs[entry.entry_id] = HistoryLog.from_dict(data)
            known = [t for t in (parse(data.get("saved_at")), parse(state.data.get("saved_at"))) if t]
            log.startup(max(known, default=None), now)
        log.purge(now)
        recorder = cls(hass, entry, log, store, state)
        recorder._save()
        return recorder

    # --- cycle de vie ---------------------------------------------------------

    @callback
    def async_attach(self, plug: PlugCoordinator | None, sessions: SessionCoordinator) -> None:
        """Écoute la prise et les sessions (contrôle suspendu, télé hors session, veille, contournement)."""
        self.plug = plug
        self.sessions = sessions
        self._unsubs.append(self.hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, self._on_stop))
        if plug:
            self._unsubs.append(plug.async_add_effect_listener(self._on_plug_effect))
            self._unsubs.append(plug.async_add_listener(self._on_change))
        self._unsubs.append(sessions.async_add_listener(self._on_change))
        self._on_change()

    async def async_unload(self) -> None:
        """Rechargement ou arrêt : rien n'est clos ; écriture immédiate."""
        for unsub in self._unsubs:
            unsub()
        self._unsubs.clear()
        await self._store.async_save(self._payload())

    # --- enregistrement ---------------------------------------------------------

    @callback
    def record_session(self, effect: SessionEnded) -> None:
        session = effect.session
        self.log.add_session(
            profile_id=session.profile_id,
            name=session.name,
            kind=session.kind,
            source=session.source,
            reason=effect.reason,
            start=session.started_at,
            end=effect.at,
            ignore_rules=session.ignore_rules,
            now=dt_util.utcnow(),
        )
        self._save()

    @callback
    def record_denied(self, reason: str, source: str, profile_id: str | None, name: str | None, kind: str | None) -> None:
        self.log.add_denied(dt_util.utcnow(), reason, source, profile_id, name, kind)
        self._save()

    @callback
    def record_lockout(self, until: datetime) -> None:
        self.log.add_lockout(dt_util.utcnow(), until)
        self._save()

    @callback
    def record_keypad(self, available: bool | None) -> None:
        if self.log.set_keypad(available, dt_util.utcnow()):
            self._save()

    @callback
    def _on_plug_effect(self, effect: PlugEffect) -> None:
        match effect:
            case Bypass(tolerated=tolerated):
                self.log.add_bypass(dt_util.utcnow(), tolerated)
                self._save()
            case Standby(power=power, cut=cut):
                self.log.add_standby(dt_util.utcnow(), power, cut)
                self._save()

    @callback
    def _on_change(self) -> None:
        """Contrôle suspendu et télé alimentée hors session, d'après la logique de la prise."""
        if self.plug is None or self.sessions is None:
            return
        logic = self.plug.logic
        now = dt_util.utcnow()
        changed = self.log.set_control(logic.control_active, now)
        powered = logic.is_on and self.sessions.session is None
        changed |= self.log.set_powered(powered, _origin(logic) if powered else "", now)
        if changed:
            self._save()

    @callback
    def _on_stop(self, _event: Event) -> None:
        self.log.mark_stopped(dt_util.utcnow())
        self._save()  # écriture différée vidée par le `Store` à l'arrêt

    # --- lecture -------------------------------------------------------------------

    def read(self, start: datetime, end: datetime) -> list[dict[str, Any]]:
        """Entrées qui chevauchent `[start, end[`, pertes de la prise et session en cours comprises."""
        low, high = iso(start), iso(end)
        found = self.log.between(start, end)
        data = self._state.data
        for outage in data.get("outages") or []:
            if isinstance(outage, dict) and _overlaps(outage.get("start"), outage.get("end"), low, high):
                found.append({"t": T_PLUG_LOST, **outage, "start": _norm(outage["start"]), "end": _norm(outage["end"])})
        if (lost := data.get("open_outage")) and _overlaps(lost, None, low, high):
            found.append({"t": T_PLUG_LOST, "start": iso(parse(lost) or start), "end": None})
        if self.sessions and (session := self.sessions.session) and iso(session.started_at) < high:
            found.append(
                {
                    "t": T_SESSION,
                    "start": iso(session.started_at),
                    "end": None,
                    "ongoing": True,
                    "profile_id": session.profile_id,
                    "name": session.name,
                    "kind": session.kind,
                    "source": session.source,
                    **({"ignore_rules": True} if session.ignore_rules else {}),
                }
            )
        return sorted(found, key=entry_start)

    # --- persistance ---------------------------------------------------------------

    def _payload(self) -> dict[str, Any]:
        return {**self.log.to_dict(), "saved_at": iso(dt_util.utcnow())}

    @callback
    def _save(self) -> None:
        self._store.async_delay_save(self._payload, SAVE_DELAY)


def _origin(logic: Any) -> str:
    if logic.tolerated:
        return ORIGIN_TOLERATED
    if not logic.control_active:
        return ORIGIN_CONTROL_INACTIVE
    if logic.desired_on:
        return ORIGIN_PARENT
    return ORIGIN_OTHER


def _norm(text: str) -> str:
    return iso(parse(text))  # type: ignore[arg-type] — validé par `_overlaps`


def _overlaps(start: Any, end: Any, low: str, high: str) -> bool:
    begin, finish = parse(start), parse(end) if end is not None else None
    if begin is None or (end is not None and finish is None):
        return False
    return iso(begin) < high and (finish is None or iso(finish) >= low)
