"""Coordinateur des sessions : branche Home Assistant sur la logique pure de `session.py`."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta
import logging
from typing import TYPE_CHECKING, Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.core import CALLBACK_TYPE, Event, HomeAssistant, callback
from homeassistant.helpers.event import async_track_point_in_utc_time
from homeassistant.util import dt as dt_util

from .const import (
    CONF_PARENT_MAX_HOURS,
    CONF_PARENTS,
    CONF_TV_NAME,
    CONF_WARNING_BEEP,
    CONF_WARNING_MINUTES,
    DEFAULT_PARENT_MAX_HOURS,
    DEFAULT_WARNING_BEEP,
    DEFAULT_WARNING_MINUTES,
    DOMAIN,
    EVENT_SESSION_ENDED,
    EVENT_SESSION_STARTED,
    EVENT_SESSION_WARNING,
    SUBENTRY_CHILD,
)
from .coordinator import EntryState, PlugCoordinator
from .plug import Effect as PlugEffect, PlugRefused, Standby
from .rules import (
    END_CONTROL_INACTIVE,
    END_HANDOVER,
    END_PLUG_LOST,
    END_PLUG_OFF,
    END_STANDBY,
    KIND_CHILD,
    KIND_PARENT,
    PLUG_UNAVAILABLE,
    Profile,
)
from .session import Effect, Session, SessionEnded, SessionLogic, SessionSettings, SessionStarted, SessionWarning
from .settings import Child, SettingsError

if TYPE_CHECKING:
    from .history_recorder import HistoryRecorder

_LOGGER = logging.getLogger(__name__)

DATA_SESSIONS = "sessions"
SECTION = "sessions"


def session_settings(options: dict[str, Any]) -> SessionSettings:
    hours = int(options.get(CONF_PARENT_MAX_HOURS, DEFAULT_PARENT_MAX_HOURS))
    return SessionSettings(
        warning=timedelta(minutes=int(options.get(CONF_WARNING_MINUTES, DEFAULT_WARNING_MINUTES))),
        parent_max=timedelta(hours=hours) if hours > 0 else None,
    )


def entry_profiles(entry: ConfigEntry) -> tuple[dict[str, Profile], set[str]]:
    """Profils lisibles (parents et enfants) et identifiants de toutes les sous‑entrées enfant."""
    profiles: dict[str, Profile] = {
        parent["id"]: Profile(parent["id"], parent["name"], KIND_PARENT) for parent in entry.options.get(CONF_PARENTS, [])
    }
    child_ids: set[str] = set()
    for subentry_id, subentry in entry.subentries.items():
        if subentry.subentry_type != SUBENTRY_CHILD:
            continue
        child_ids.add(subentry_id)
        try:
            child = Child.from_dict(dict(subentry.data))
        except SettingsError:
            continue
        profiles[subentry_id] = Profile(subentry_id, child.name, KIND_CHILD, child.enabled, child.rules)
    return profiles, child_ids


def minutes(seconds: float | None) -> float | None:
    return None if seconds is None else round(seconds / 60, 1)


class SessionCoordinator:
    """Un par entrée chargée ; la logique (`SessionLogic`) survit aux rechargements."""

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry, logic: SessionLogic, state: EntryState, plug: PlugCoordinator | None
    ) -> None:
        self.hass = hass
        self.entry = entry
        self.logic = logic
        self.plug = plug
        self._state = state
        self._startup = False
        self._listeners: list[Callable[[], None]] = []
        self._unsubs: list[CALLBACK_TYPE] = []
        self._timer: CALLBACK_TYPE | None = None
        self.beeper: Callable[[], Awaitable[None]] | None = None  # bip du clavier (AccessManager)
        self.history: HistoryRecorder | None = None  # historique (tranche 4)

    @classmethod
    def create(
        cls, hass: HomeAssistant, entry: ConfigEntry, state: EntryState, plug: PlugCoordinator | None
    ) -> SessionCoordinator:
        logics: dict[str, SessionLogic] = hass.data.setdefault(DOMAIN, {}).setdefault(DATA_SESSIONS, {})
        logic = logics.get(entry.entry_id)
        startup = logic is None
        if logic is None:
            now = dt_util.utcnow()
            logic = logics[entry.entry_id] = SessionLogic(dt_util.get_default_time_zone(), session_settings(dict(entry.options)), now)
            section = state.data.get(SECTION)
            if isinstance(section, dict):
                logic.restore(section, now)
        coordinator = cls(hass, entry, logic, state, plug)
        coordinator._startup = startup
        return coordinator

    # --- cycle de vie ---------------------------------------------------------

    async def async_start(self) -> None:
        now = dt_util.utcnow()
        profiles, child_ids = entry_profiles(self.entry)
        effects: list[Effect] = []
        if self._startup:
            # Démarrage de Home Assistant (D1) : la session trouvée se termine, décomptée jusqu'à
            # l'arrêt ; la prise est coupée par la règle de démarrage de la tranche 1.
            self.logic.profiles = profiles
            saved_at = dt_util.parse_datetime(self._state.data.get("saved_at") or "")
            effects += self.logic.end_after_restart(saved_at, now)
        effects += self.logic.update_profiles(profiles, now, child_ids)
        effects += self.logic.update_settings(session_settings(dict(self.entry.options)), now)
        self._unsubs.append(self.hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, self._on_stop))
        if self.plug:
            self._unsubs.append(self.plug.async_add_listener(self._on_plug))
            self._unsubs.append(self.plug.async_add_effect_listener(self._on_plug_effect))
        self._apply(effects)

    async def async_unload(self) -> None:
        for unsub in self._unsubs:
            unsub()
        self._unsubs.clear()
        if self._timer:
            self._timer()
            self._timer = None
        self._persist()

    # --- lecture pour les entités et l'accès ------------------------------------

    @property
    def tv_name(self) -> str:
        return self.entry.data.get(CONF_TV_NAME, self.entry.title)

    @property
    def session(self) -> Session | None:
        return self.logic.session

    @property
    def warning_beep(self) -> bool:
        return bool(self.entry.options.get(CONF_WARNING_BEEP, DEFAULT_WARNING_BEEP))

    def planned_end(self) -> tuple[datetime | None, str | None]:
        return self.logic.planned_end(dt_util.utcnow())

    @callback
    def async_add_listener(self, listener: Callable[[], None]) -> CALLBACK_TYPE:
        self._listeners.append(listener)
        return lambda: self._listeners.remove(listener)

    # --- demandes ---------------------------------------------------------------

    @callback
    def async_start_session(
        self, profile: Profile, source: str, ignore_rules: bool = False, handover: bool = False
    ) -> None:
        """Ouvre une session ; allume la prise sauf si la télé est déjà allumée (D5). Lève `PlugRefused`."""
        if self.plug is None:
            raise PlugRefused(PLUG_UNAVAILABLE)
        logic = self.plug.logic
        if not logic.desired_on:
            # Télé déjà allumée (allumage toléré) : la demande l'adopte sans commande.
            self.plug.async_request(True)
        now = dt_util.utcnow()
        effects: list[Effect] = []
        if handover:
            effects += self.logic.stop(END_HANDOVER, now)
        elif self.logic.session is not None:
            raise RuntimeError("session already running")
        effects += self.logic.start(profile, now, source, ignore_rules)
        self._apply(effects)

    @callback
    def async_stop(self, reason: str) -> bool:
        """Termine la session en cours (et coupe la prise selon le motif) ; faux s'il n'y en avait pas."""
        if self.logic.session is None:
            return False
        self._apply(self.logic.stop(reason, dt_util.utcnow()))
        return True

    # --- événements ---------------------------------------------------------------

    @callback
    def _on_plug(self) -> None:
        """La logique de la prise a changé : la session suit (contrôle, veille, coupure, perte)."""
        if self.logic.session is None or self.plug is None:
            return
        plug = self.plug.logic
        if not plug.control_active:
            reason = END_CONTROL_INACTIVE
        elif not plug.desired_on:
            reason = END_STANDBY if plug.standby else END_PLUG_LOST if plug.grace_expired else END_PLUG_OFF
        else:
            return
        self._apply(self.logic.stop(reason, dt_util.utcnow()))

    @callback
    def _on_plug_effect(self, effect: PlugEffect) -> None:
        """Veille détectée (D2) : la session se termine avant que la prise soit coupée.

        Option « Couper la prise en veille » désactivée (ou contrôle suspendu) : la session continue.
        """
        if isinstance(effect, Standby) and effect.cut and self.logic.session is not None:
            self._apply(self.logic.stop(END_STANDBY, dt_util.utcnow()))

    @callback
    def _on_timer(self, now: datetime) -> None:
        self._timer = None
        self._apply(self.logic.tick(dt_util.utcnow()))

    @callback
    def _on_stop(self, _event: Event) -> None:
        self._persist()

    # --- effets -----------------------------------------------------------------

    @callback
    def _apply(self, effects: list[Effect]) -> None:
        for effect in effects:
            match effect:
                case SessionStarted():
                    self._started(effect)
                case SessionWarning():
                    self._warning(effect)
                case SessionEnded():
                    self._ended(effect)
        self._persist()
        self._schedule()
        for listener in list(self._listeners):
            listener()

    def _base(self, session: Session) -> dict[str, Any]:
        return {
            "entry_id": self.entry.entry_id,
            "profile": session.name,
            "profile_id": session.profile_id,
            "kind": session.kind,
        }

    def _started(self, effect: SessionStarted) -> None:
        session = effect.session
        planned = effect.planned_end.isoformat() if effect.planned_end else None
        _LOGGER.info("Session de %s sur %s ouverte (coupure prévue : %s)", session.name, self.tv_name, planned)
        self.hass.bus.async_fire(
            EVENT_SESSION_STARTED,
            {
                **self._base(session),
                "source": session.source,
                "ignore_rules": session.ignore_rules,
                "planned_end": planned,
                "remaining": minutes(effect.remaining),
            },
        )

    def _warning(self, effect: SessionWarning) -> None:
        session = effect.session
        _LOGGER.info("Session de %s : coupure dans %d min", session.name, effect.minutes_left)
        self.hass.bus.async_fire(
            EVENT_SESSION_WARNING,
            {**self._base(session), "minutes_left": effect.minutes_left, "planned_end": effect.planned_end.isoformat()},
        )
        if effect.beep and self.warning_beep and self.beeper:
            self.hass.async_create_task(self.beeper(), eager_start=True)

    def _ended(self, effect: SessionEnded) -> None:
        session = effect.session
        _LOGGER.info("Session de %s terminée (%s) après %s", session.name, effect.reason, effect.duration)
        data = {
            **self._base(session),
            "reason": effect.reason,
            "duration": round(effect.duration.total_seconds()),
        }
        if session.kind == KIND_CHILD:
            data["consumed_today"] = minutes(effect.consumed)
            data["remaining"] = minutes(effect.remaining)
        self.hass.bus.async_fire(EVENT_SESSION_ENDED, data)
        if self.history:
            self.history.record_session(effect)
        if effect.cut and self.plug is not None:
            try:
                self.plug.async_request(False)
            except PlugRefused as err:
                _LOGGER.warning("Fin de session sans coupure de la prise %s : %s", self.plug.plug_entity, err.reason)

    @callback
    def _persist(self) -> None:
        self._state.data[SECTION] = self.logic.to_dict()
        self._state.save()

    @callback
    def _schedule(self) -> None:
        if self._timer:
            self._timer()
            self._timer = None
        self._timer = async_track_point_in_utc_time(self.hass, self._on_timer, self.logic.next_deadline(dt_util.utcnow()))
