"""Décision d'accès et anti‑essais.

Ce module n'importe rien de Home Assistant. Le code saisi n'y entre jamais : la décision reçoit le
profil reconnu (ou None) par `security.match_code`.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from .settings import DAYS, WeeklyRules

KIND_CHILD = "child"
KIND_PARENT = "parent"

LOCKED_OUT = "locked_out"
INVALID_CODE = "invalid_code"
CONTROL_INACTIVE = "control_inactive"
PLUG_UNAVAILABLE = "plug_unavailable"
PROFILE_BLOCKED = "profile_blocked"
OUTSIDE_SCHEDULE = "outside_schedule"
QUOTA_EXHAUSTED = "quota_exhausted"
TV_IN_USE = "tv_in_use"  # session déjà en cours (action `start_session`)
ERROR = "error"  # erreur interne : refus par sûreté, sans compter d'échec

REASONS = (
    LOCKED_OUT,
    INVALID_CODE,
    CONTROL_INACTIVE,
    PLUG_UNAVAILABLE,
    PROFILE_BLOCKED,
    OUTSIDE_SCHEDULE,
    QUOTA_EXHAUSTED,
    TV_IN_USE,
    ERROR,
)

# Actions d'un accès accordé (tranche 3)
ACTION_START = "start"
ACTION_STOP = "stop"  # le même enfant, ou un parent, termine la session en cours
ACTION_HANDOVER = "handover"  # un enfant reprend la télé de la session en cours (autre enfant ou parent)

# Motifs de fin de session (tranche 3)
END_USER = "user"
END_PARENT = "parent"
END_KEYPAD_OFF = "keypad_off"
END_STOPPED = "stopped"
END_QUOTA = "quota"
END_SCHEDULE = "schedule"
END_MIDNIGHT = "midnight"
END_SAFETY_LIMIT = "safety_limit"
END_STANDBY = "standby"
END_PLUG_OFF = "plug_off"
END_PLUG_LOST = "plug_lost"
END_CONTROL_INACTIVE = "control_inactive"
END_PROFILE_BLOCKED = "profile_blocked"
END_PROFILE_REMOVED = "profile_removed"
END_RESTART = "restart"
END_HANDOVER = "handover"

END_REASONS = (
    END_USER,
    END_PARENT,
    END_KEYPAD_OFF,
    END_STOPPED,
    END_QUOTA,
    END_SCHEDULE,
    END_MIDNIGHT,
    END_SAFETY_LIMIT,
    END_STANDBY,
    END_PLUG_OFF,
    END_PLUG_LOST,
    END_CONTROL_INACTIVE,
    END_PROFILE_BLOCKED,
    END_PROFILE_REMOVED,
    END_RESTART,
    END_HANDOVER,
)

MIN_REMAINING = 60  # s : en dessous, le quota est épuisé


@dataclass(frozen=True)
class Profile:
    """Un enfant (identifiant de sous‑entrée) ou un parent (identifiant du code parent)."""

    id: str
    name: str
    kind: str
    enabled: bool = True
    rules: WeeklyRules | None = None


@dataclass(frozen=True)
class Context:
    now: datetime  # instant absolu (anti‑essais)
    local_now: datetime  # heure locale de Home Assistant (plages, jour)
    control_active: bool
    plug_available: bool
    session_id: str | None = None  # profil de la session en cours
    session_kind: str | None = None
    consumed: Mapping[str, float] = field(default_factory=dict)  # s consommées aujourd'hui, par enfant


@dataclass(frozen=True)
class Decision:
    granted: bool
    reason: str | None = None
    profile: Profile | None = None
    lockout_until: datetime | None = None  # cette saisie a déclenché le verrouillage
    unlocked: bool = False  # un code parent a levé un verrouillage ou effacé des échecs
    action: str | None = None  # accordé : start, stop ou handover


def in_schedule(rules: WeeklyRules, local_now: datetime) -> bool:
    """L'instant local est‑il dans une plage [début, fin[ du jour ? (fin 1440 = minuit)"""
    day = DAYS[local_now.weekday()]
    minute = local_now.hour * 60 + local_now.minute
    return any(slot.start <= minute < slot.end for slot in rules.slots[day])


def quota_today(rules: WeeklyRules, local_now: datetime) -> int:
    return rules.quota_minutes[DAYS[local_now.weekday()]]


def remaining_seconds(rules: WeeklyRules, local_now: datetime, consumed: float, bonus_minutes: int = 0) -> float:
    """Temps restant du jour : quota + bonus − consommé, borné à 0 (bonus : tranche 4)."""
    return max(0.0, (quota_today(rules, local_now) + bonus_minutes) * 60 - consumed)


def child_refusal(profile: Profile, local_now: datetime, consumed: float) -> str | None:
    """Motif qui empêche l'enfant d'ouvrir une session selon ses seules règles, ou None."""
    if not profile.enabled:
        return PROFILE_BLOCKED
    rules = profile.rules or WeeklyRules.empty()
    if not in_schedule(rules, local_now):
        return OUTSIDE_SCHEDULE
    if remaining_seconds(rules, local_now, consumed) < MIN_REMAINING:
        return QUOTA_EXHAUSTED
    return None


def is_off_key(key: str | None, off_key: str | None) -> bool:
    """Touche seule (sans code) qui coupe la télé ; `off_key` None ou "none" : désactivé."""
    return bool(key) and off_key not in (None, "none") and key == off_key


# --- Anti‑essais --------------------------------------------------------------


@dataclass
class KeypadGuard:
    """N échecs dans une fenêtre glissante de F → verrouillage de D."""

    max_failures: int = 5
    window: timedelta = timedelta(minutes=5)
    duration: timedelta = timedelta(minutes=10)
    failures: list[datetime] = field(default_factory=list)
    locked_until: datetime | None = None

    def is_locked(self, now: datetime) -> bool:
        if self.locked_until is not None and now >= self.locked_until:
            self.locked_until = None
        return self.locked_until is not None

    def recent_failures(self, now: datetime) -> int:
        self._forget(now)
        return len(self.failures)

    def record_failure(self, now: datetime) -> datetime | None:
        """Compte un échec ; renvoie la fin du verrouillage s'il commence."""
        self._forget(now)
        self.failures.append(now)
        if len(self.failures) < self.max_failures:
            return None
        self.failures = []
        self.locked_until = now + self.duration
        return self.locked_until

    def unlock(self) -> bool:
        """Lève le verrouillage et efface les échecs ; vrai si quelque chose a changé."""
        changed = self.locked_until is not None or bool(self.failures)
        self.locked_until = None
        self.failures = []
        return changed

    def next_deadline(self) -> datetime | None:
        return self.locked_until

    def update_settings(self, max_failures: int, window: timedelta, duration: timedelta) -> None:
        """Nouveaux réglages : le verrouillage en cours garde son échéance."""
        self.max_failures, self.window, self.duration = max_failures, window, duration

    def _forget(self, now: datetime) -> None:
        self.failures = [at for at in self.failures if now - at < self.window]

    def to_dict(self) -> dict[str, Any]:
        return {
            "failures": [at.isoformat() for at in self.failures],
            "locked_until": self.locked_until.isoformat() if self.locked_until else None,
        }

    def restore(self, data: dict[str, Any], now: datetime) -> None:
        """Relit l'état enregistré ; un verrouillage expiré pendant l'arrêt est levé."""
        try:
            self.failures = [datetime.fromisoformat(at) for at in data.get("failures", [])]
            until = data.get("locked_until")
            self.locked_until = datetime.fromisoformat(until) if until else None
        except (TypeError, ValueError):
            self.failures, self.locked_until = [], None
        self.is_locked(now)
        self._forget(now)


# --- Décision -----------------------------------------------------------------


def decide(profile: Profile | None, guard: KeypadGuard, context: Context) -> Decision:
    """Ordre (tranche 3) : parent → verrouillage → inconnu → sa propre session → contrôle → prise →
    enfant désactivé → plage → temps restant → reprise de la session en cours (autre enfant ou
    parent) → début de session.
    """
    now = context.now
    locked = guard.is_locked(now)

    if profile is not None and profile.kind == KIND_PARENT:
        unlocked = guard.unlock()
        if context.session_id is not None:
            return Decision(True, profile=profile, unlocked=unlocked, action=ACTION_STOP)
        if reason := _global_refusal(context):
            return Decision(False, reason, profile, unlocked=unlocked)
        return Decision(True, profile=profile, unlocked=unlocked, action=ACTION_START)

    if locked:
        return Decision(False, LOCKED_OUT)

    if profile is None:
        return Decision(False, INVALID_CODE, lockout_until=guard.record_failure(now))

    if context.session_id == profile.id:
        # Le code sert d'interrupteur : arrêt toujours possible (même hors plage, prise injoignable).
        return Decision(True, profile=profile, action=ACTION_STOP)
    if reason := _global_refusal(context):
        return Decision(False, reason, profile)
    if reason := child_refusal(profile, context.local_now, context.consumed.get(profile.id, 0.0)):
        return Decision(False, reason, profile)
    if context.session_id is not None:
        # Décision de Rémi (2026-10-03) : un enfant qui a droit à la télé la reprend, que la session
        # en cours soit celle d'un autre enfant ou d'un parent ; celle-ci se termine (`handover`).
        return Decision(True, profile=profile, action=ACTION_HANDOVER)
    return Decision(True, profile=profile, action=ACTION_START)


def _global_refusal(context: Context) -> str | None:
    if not context.control_active:
        return CONTROL_INACTIVE
    if not context.plug_available:
        return PLUG_UNAVAILABLE
    return None
