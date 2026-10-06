"""Gestionnaire d'accès : saisie → vérification hors boucle → décision (`rules.py`) → effets.

Le code saisi ne sort jamais de `_async_handle` : il est passé à `security.match_code` dans
l'exécuteur, puis oublié. Rien de ce qui est journalisé, émis ou enregistré ne le contient.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import time
from typing import Any

from homeassistant.components import mqtt
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.event import async_track_point_in_utc_time
from homeassistant.util import dt as dt_util

from .const import (
    BATTERY_LOW,
    CONF_KEYPAD_TOPIC,
    CONF_LOCKOUT_DURATION,
    CONF_LOCKOUT_FAILURES,
    CONF_LOCKOUT_WINDOW,
    CONF_OFF_KEY,
    CONF_PARENTS,
    CONF_TV_NAME,
    DEFAULT_LOCKOUT_DURATION,
    DEFAULT_LOCKOUT_FAILURES,
    DEFAULT_LOCKOUT_WINDOW,
    DEFAULT_OFF_KEY,
    DOMAIN,
    EVENT_ACCESS_DENIED,
    EVENT_ACCESS_GRANTED,
    EVENT_KEYPAD_OFF,
    EVENT_LOCKOUT,
    SUBENTRY_CHILD,
)
from .coordinator import EntryState, PlugCoordinator
from .keypad.base import SOURCE_KEYPAD, KeypadAdapter, KeypadStatus, Submission
from .keypad.mqtt import Zigbee2MqttKeypad
from .plug import PlugRefused
from .rules import (
    ACTION_HANDOVER,
    ACTION_STOP,
    CONTROL_INACTIVE,
    END_KEYPAD_OFF,
    END_PARENT,
    END_USER,
    ERROR,
    KIND_CHILD,
    KIND_PARENT,
    PLUG_UNAVAILABLE,
    Context,
    Decision,
    KeypadGuard,
    Profile,
    decide,
    is_off_key,
)
from .security import match_code
from .history_recorder import HistoryRecorder
from .session_coordinator import SessionCoordinator
from .settings import Child, SettingsError

_LOGGER = logging.getLogger(__name__)

ISSUE_UNREACHABLE = "keypad_unreachable"
ISSUE_BATTERY = "keypad_battery_low"


def guard_settings(options: dict[str, Any]) -> tuple[int, timedelta, timedelta]:
    return (
        int(options.get(CONF_LOCKOUT_FAILURES, DEFAULT_LOCKOUT_FAILURES)),
        timedelta(minutes=int(options.get(CONF_LOCKOUT_WINDOW, DEFAULT_LOCKOUT_WINDOW))),
        timedelta(minutes=int(options.get(CONF_LOCKOUT_DURATION, DEFAULT_LOCKOUT_DURATION))),
    )


def profiles_of(entry: ConfigEntry) -> tuple[list[Profile], list[tuple[str, dict[str, Any]]]]:
    """Profils (parents puis enfants lisibles) et empreintes, dans un ordre fixe."""
    profiles: list[Profile] = []
    hashes: list[tuple[str, dict[str, Any]]] = []
    for parent in entry.options.get(CONF_PARENTS, []):
        profiles.append(Profile(parent["id"], parent["name"], KIND_PARENT))
        hashes.append((parent["id"], parent["code"]))
    for subentry_id, subentry in entry.subentries.items():
        if subentry.subentry_type != SUBENTRY_CHILD:
            continue
        try:
            child = Child.from_dict(dict(subentry.data))
        except SettingsError:
            continue  # enfant illisible : ignoré (son code est inconnu)
        profiles.append(Profile(subentry_id, child.name, KIND_CHILD, child.enabled, child.rules))
        hashes.append((subentry_id, child.code))
    return profiles, hashes


class AccessManager:
    """Un par instance chargée ; existe même sans prise ni clavier."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        state: EntryState,
        plug: PlugCoordinator | None,
        sessions: SessionCoordinator,
        history: HistoryRecorder | None = None,
    ) -> None:
        self.hass = hass
        self.history = history
        self.entry = entry
        self.plug = plug
        self.sessions = sessions
        self.state = self._state = state
        data = state.data.setdefault("keypad", {})
        self._data = data
        self.guard = KeypadGuard(*guard_settings(dict(entry.options)))
        self.guard.restore(data, dt_util.utcnow())
        self.status = KeypadStatus(battery=data.get("battery"))
        self.adapter: KeypadAdapter | None = None
        self._lock = asyncio.Lock()
        self._listeners: list[Callable[[], None]] = []
        self._timer: CALLBACK_TYPE | None = None
        self._tasks: set[asyncio.Task[Any]] = set()
        if topic := entry.data.get(CONF_KEYPAD_TOPIC):
            self.adapter = Zigbee2MqttKeypad(hass, topic, self._on_submission, self._on_status, data.get("ias_ace", False))
        sessions.beeper = self.async_warn

    # --- cycle de vie ---------------------------------------------------------

    async def async_start(self) -> None:
        self._persist()
        self._schedule()
        self._sync_issues()
        if self.adapter:
            self._spawn(self._async_start_adapter(), background=True)

    async def _async_start_adapter(self) -> None:
        # MQTT peut se connecter après Zapette au démarrage : attendre le client sans bloquer.
        if "mqtt" in self.hass.config.components or await mqtt.async_wait_for_mqtt_client(self.hass):
            if self.adapter:
                await self.adapter.async_start()

    async def async_unload(self) -> None:
        if self._timer:
            self._timer()
            self._timer = None
        for task in list(self._tasks):
            task.cancel()
        if self.adapter:
            await self.adapter.async_stop()

    @property
    def keypad_topic(self) -> str | None:
        return self.entry.data.get(CONF_KEYPAD_TOPIC)

    @property
    def off_key(self) -> str:
        return self.entry.options.get(CONF_OFF_KEY, DEFAULT_OFF_KEY)

    @property
    def tv_name(self) -> str:
        return self.entry.data.get(CONF_TV_NAME, self.entry.title)

    @property
    def last_granted(self) -> dict[str, Any] | None:
        return self._data.get("last_granted")

    @property
    def last_denied(self) -> dict[str, Any] | None:
        return self._data.get("last_denied")

    def is_locked(self) -> bool:
        return self.guard.is_locked(dt_util.utcnow())

    @callback
    def async_add_listener(self, listener: Callable[[], None]) -> CALLBACK_TYPE:
        self._listeners.append(listener)
        return lambda: self._listeners.remove(listener)

    # --- entrées --------------------------------------------------------------

    @callback
    def _on_submission(self, submission: Submission) -> None:
        if "transaction" in submission.context and not self._data.get("ias_ace"):
            # Clavier IAS ACE (réponse d'armement) : il accepte aussi un état du panneau (bip, tranche 3).
            self._data["ias_ace"] = True
            if self.adapter:
                self.adapter.ias_ace = True
            self._state.save()
        self._spawn(self.async_submit(submission))

    @callback
    def _on_status(self, status: KeypadStatus) -> None:
        self.status = status
        if self.history:
            self.history.record_keypad(status.available)
        if status.battery is not None and self._data.get("battery") != status.battery:
            self._data["battery"] = status.battery
            self._state.save()
        self._sync_issues()
        self._notify()

    async def async_submit(self, submission: Submission) -> Decision:
        """Traite une saisie (clavier ou action), dans l'ordre d'arrivée."""
        async with self._lock:
            if not submission.code:
                # Touche seule : seule la touche d'arrêt a un effet (couper la télé, sans code).
                if not is_off_key(submission.key, self.off_key):
                    return Decision(False)
                decision = self._turn_off_from_keypad(submission)
                await self._async_feedback(submission, decision.granted)
                return decision
            try:
                decision = await self._async_handle(submission)
            except Exception:  # noqa: BLE001 — sûreté : toute erreur est un refus
                _LOGGER.exception("Erreur pendant le traitement d'une saisie (%s) : accès refusé", submission.source)
                decision = Decision(False, ERROR)
                self._record(decision, submission)
            await self._async_feedback(submission, decision.granted)
            return decision

    async def _async_feedback(self, submission: Submission, success: bool) -> None:
        if submission.source == SOURCE_KEYPAD and self.adapter:
            try:
                await self.adapter.async_feedback(submission, success)
            except Exception:  # noqa: BLE001 — un retour en échec ne change pas la décision
                _LOGGER.warning("Clavier %s : retour impossible", self.keypad_topic)

    def _turn_off_from_keypad(self, submission: Submission) -> Decision:
        """Touche d'arrêt seule : coupe la télé, sans code ni règle (couper est le côté sûr).

        Valable même clavier verrouillé ; refusée si le contrôle est suspendu ou sans prise.
        """
        reason: str | None = None
        if self.plug is None:
            reason = PLUG_UNAVAILABLE
        elif not self.plug.logic.control_active:
            reason = CONTROL_INACTIVE
        elif self.sessions.async_stop(END_KEYPAD_OFF):
            pass  # session terminée (D4), prise coupée par la fin de session
        elif self.plug.logic.is_on or self.plug.logic.desired_on:
            try:
                self.plug.async_request(False)
            except PlugRefused as err:
                reason = err.reason
        data = {"entry_id": self.entry.entry_id, "key": submission.key, "done": reason is None, "reason": reason}
        self.hass.bus.async_fire(EVENT_KEYPAD_OFF, data)
        _LOGGER.info("Touche d'arrêt du clavier de %s : %s", self.tv_name, reason or "télé coupée")
        return Decision(reason is None, reason)

    async def _async_handle(self, submission: Submission) -> Decision:
        profiles, hashes = profiles_of(self.entry)
        started = time.monotonic()
        matched = await self.hass.async_add_executor_job(match_code, submission.code, hashes)
        _LOGGER.debug("Vérification du code : %.0f ms pour %d profils", (time.monotonic() - started) * 1000, len(hashes))
        profile = next((p for p in profiles if p.id == matched), None)

        now = dt_util.utcnow()
        logic = self.plug.logic if self.plug else None
        session = self.sessions.session
        context = Context(
            now=now,
            local_now=dt_util.as_local(now),
            control_active=logic.control_active if logic else bool(self._state.data.get("control_active", True)),
            plug_available=bool(logic and logic.available),
            session_id=session.profile_id if session else None,
            session_kind=session.kind if session else None,
            consumed=self.sessions.logic.consumed_all(now),
        )
        decision = decide(profile, self.guard, context)
        if decision.granted:
            decision = self._apply_session(decision, submission)
        self._record(decision, submission)
        return decision

    def _apply_session(self, decision: Decision, submission: Submission) -> Decision:
        """Ouvre, termine ou reprend la session ; un refus de la prise devient un refus d'accès."""
        assert decision.profile is not None
        if decision.action == ACTION_STOP:
            self.sessions.async_stop(END_PARENT if decision.profile.kind == KIND_PARENT else END_USER)
            return decision
        try:
            self.sessions.async_start_session(
                decision.profile, submission.source, handover=decision.action == ACTION_HANDOVER
            )
        except PlugRefused as err:
            return Decision(False, err.reason, decision.profile, unlocked=decision.unlocked)
        return decision

    async def async_warn(self) -> None:
        """Bip d'avertissement avant coupure, si le clavier le permet."""
        if self.adapter:
            try:
                await self.adapter.async_warn()
            except Exception:  # noqa: BLE001 — un bip en échec ne change pas la session
                _LOGGER.warning("Clavier %s : bip d'avertissement impossible", self.keypad_topic)

    @callback
    def async_unblock(self) -> None:
        """Action `zapette.unblock_keypad`."""
        if self.guard.unlock():
            _LOGGER.info("Clavier de %s déverrouillé par une action", self.tv_name)
        self._persist()
        self._schedule()
        self._notify()

    # --- effets ---------------------------------------------------------------

    def _record(self, decision: Decision, submission: Submission) -> None:
        profile = decision.profile
        info = {
            "at": dt_util.utcnow().isoformat(),
            "profile": profile.name if profile else None,
            "profile_id": profile.id if profile else None,
            "kind": profile.kind if profile else None,
            "source": submission.source,
        }
        base = {"entry_id": self.entry.entry_id, **{k: info[k] for k in ("profile", "profile_id", "kind", "source")}, "key": submission.key}
        if decision.granted:
            info["action"] = decision.action
        if decision.unlocked:
            _LOGGER.info("Clavier de %s déverrouillé par un code parent", self.tv_name)
        if decision.granted:
            self._data["last_granted"] = info
            self.hass.bus.async_fire(EVENT_ACCESS_GRANTED, {**base, "action": decision.action})
        else:
            self._data["last_denied"] = {**info, "reason": decision.reason}
            self.hass.bus.async_fire(EVENT_ACCESS_DENIED, {**base, "reason": decision.reason})
            if self.history:
                self.history.record_denied(
                    decision.reason or "error", submission.source, info["profile_id"], info["profile"], info["kind"]
                )
        if decision.lockout_until:
            if self.history:
                self.history.record_lockout(decision.lockout_until)
            _LOGGER.warning("Clavier de %s verrouillé jusqu'à %s après trop de codes faux", self.tv_name, decision.lockout_until)
            self.hass.bus.async_fire(EVENT_LOCKOUT, {"entry_id": self.entry.entry_id, "until": decision.lockout_until.isoformat()})
        self._persist()
        self._schedule()
        self._notify()

    def _persist(self) -> None:
        self._data.update(self.guard.to_dict())
        self._state.save()

    @callback
    def _schedule(self) -> None:
        if self._timer:
            self._timer()
            self._timer = None
        if (deadline := self.guard.next_deadline()) is not None:
            self._timer = async_track_point_in_utc_time(self.hass, self._on_timer, deadline)

    @callback
    def _on_timer(self, now: datetime) -> None:
        self._timer = None
        self.guard.is_locked(now)
        self._persist()
        self._schedule()
        self._notify()

    @callback
    def _notify(self) -> None:
        for listener in list(self._listeners):
            listener()

    @callback
    def _sync_issues(self) -> None:
        placeholders = {"tv_name": self.tv_name, "topic": self.keypad_topic or ""}
        battery = self.status.battery
        wanted = {
            ISSUE_UNREACHABLE: bool(self.adapter) and self.status.available is False,
            ISSUE_BATTERY: bool(self.adapter) and battery is not None and battery < BATTERY_LOW,
        }
        for key, active in wanted.items():
            issue_id = f"{key}_{self.entry.entry_id}"
            if active:
                ir.async_create_issue(
                    self.hass,
                    DOMAIN,
                    issue_id,
                    is_fixable=False,
                    severity=ir.IssueSeverity.ERROR if key == ISSUE_UNREACHABLE else ir.IssueSeverity.WARNING,
                    translation_key=key,
                    translation_placeholders={**placeholders, "battery": str(battery)},
                )
            else:
                ir.async_delete_issue(self.hass, DOMAIN, issue_id)

    def _spawn(self, coro: Any, background: bool = False) -> None:
        if background:
            task = self.hass.async_create_background_task(coro, f"{DOMAIN} keypad", eager_start=True)
        else:
            task = self.hass.async_create_task(coro, eager_start=True)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)


@dataclass
class ZapetteRuntime:
    """`ConfigEntry.runtime_data` : prise (si configurée), accès, sessions et historique (toujours)."""

    plug: PlugCoordinator | None
    access: AccessManager
    sessions: SessionCoordinator
    history: HistoryRecorder
