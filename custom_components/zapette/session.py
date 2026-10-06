"""Sessions : qui regarde, depuis quand, jusqu'à quand ; temps consommés du jour.

Ce module n'importe rien de Home Assistant. Les instants sont des `datetime` UTC ; le fuseau de
Home Assistant (`zoneinfo`) sert aux jours, aux plages et à minuit. Le temps consommé est du
temps réel écoulé. Chaque entrée renvoie la liste des effets à exécuter ; `next_deadline()` donne
l'instant auquel appeler `tick()`.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import UTC, date, datetime, time, timedelta, tzinfo
import math
from typing import Any

from .rules import (
    END_CONTROL_INACTIVE,
    END_HANDOVER,
    END_MIDNIGHT,
    END_PLUG_LOST,
    END_PLUG_OFF,
    END_PROFILE_BLOCKED,
    END_PROFILE_REMOVED,
    END_QUOTA,
    END_RESTART,
    END_SAFETY_LIMIT,
    END_SCHEDULE,
    END_STANDBY,
    KIND_CHILD,
    Profile,
    child_refusal,
    remaining_seconds,
)
from .settings import DAYS, MINUTES_PER_DAY, WeeklyRules

# Fins sans commande à la prise : déjà coupée, injoignable, non pilotée, ou télé reprise.
NO_CUT = frozenset({END_STANDBY, END_PLUG_OFF, END_PLUG_LOST, END_CONTROL_INACTIVE, END_RESTART, END_HANDOVER})
# Échéances simultanées : motif retenu dans cet ordre.
DEADLINE_ORDER = (END_QUOTA, END_SCHEDULE, END_MIDNIGHT, END_SAFETY_LIMIT)
HEARTBEAT = timedelta(minutes=1)


@dataclass(frozen=True)
class SessionSettings:
    warning: timedelta = timedelta(minutes=5)  # 0 : pas d'avertissement
    parent_max: timedelta | None = timedelta(hours=4)  # None : jamais


@dataclass
class Session:
    profile_id: str
    name: str
    kind: str
    started_at: datetime
    source: str = "keypad"
    ignore_rules: bool = False
    warned: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "name": self.name,
            "kind": self.kind,
            "started_at": self.started_at.isoformat(),
            "source": self.source,
            "ignore_rules": self.ignore_rules,
            "warned": self.warned,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Session:
        started = datetime.fromisoformat(data["started_at"])
        if started.tzinfo is None:
            raise ValueError("started_at")
        return cls(
            profile_id=str(data["profile_id"]),
            name=str(data["name"]),
            kind=str(data["kind"]),
            started_at=started,
            source=str(data.get("source", "keypad")),
            ignore_rules=bool(data.get("ignore_rules", False)),
            warned=bool(data.get("warned", False)),
        )


# --- Effets -------------------------------------------------------------------


@dataclass(frozen=True)
class SessionStarted:
    session: Session
    planned_end: datetime | None
    remaining: float | None  # s, enfant


@dataclass(frozen=True)
class SessionWarning:
    session: Session
    minutes_left: int
    planned_end: datetime
    beep: bool


@dataclass(frozen=True)
class SessionEnded:
    session: Session
    reason: str
    at: datetime
    duration: timedelta
    cut: bool  # demander la coupure de la prise
    consumed: float | None  # s du jour, enfant
    remaining: float | None  # s du jour, enfant


Effect = SessionStarted | SessionWarning | SessionEnded


# --- Logique ------------------------------------------------------------------


class SessionLogic:
    """Une par télévision. Neuve = démarrage de Home Assistant (voir `end_after_restart`)."""

    def __init__(self, tz: tzinfo, settings: SessionSettings, now: datetime) -> None:
        self.tz = tz
        self.settings = settings
        self.profiles: dict[str, Profile] = {}
        self.session: Session | None = None
        self.day: date = self._local(now).date()
        self.consumed: dict[str, float] = {}  # s des sessions terminées du jour, par enfant
        self.last_ended: dict[str, Any] | None = None

    # --- temps local -----------------------------------------------------------

    def _local(self, at: datetime) -> datetime:
        return at.astimezone(self.tz)

    def _day_start(self, day: date) -> datetime:
        return datetime.combine(day, time(0), self.tz).astimezone(UTC)

    def _at(self, day: date, minutes: int) -> datetime:
        """Instant UTC d'une heure locale (minutes depuis minuit ; 1440 = minuit suivant)."""
        if minutes >= MINUTES_PER_DAY:
            return self._day_start(day + timedelta(days=1))
        return datetime.combine(day, time(minutes // 60, minutes % 60), self.tz).astimezone(UTC)

    def midnight_after(self, now: datetime) -> datetime:
        return self._day_start(self._local(now).date() + timedelta(days=1))

    # --- lecture ----------------------------------------------------------------

    def consumed_now(self, child_id: str, now: datetime) -> float:
        """Secondes consommées aujourd'hui, session en cours comprise."""
        total = self.consumed.get(child_id, 0.0)
        session = self.session
        if session and session.kind == KIND_CHILD and session.profile_id == child_id:
            total += self._overlap(session.started_at, now)
        return total

    def consumed_all(self, now: datetime) -> dict[str, float]:
        result = dict(self.consumed)
        if self.session and self.session.kind == KIND_CHILD:
            result[self.session.profile_id] = self.consumed_now(self.session.profile_id, now)
        return result

    def remaining(self, child_id: str, now: datetime) -> float:
        profile = self.profiles.get(child_id)
        if profile is None:
            return 0.0
        rules = profile.rules or WeeklyRules.empty()
        return remaining_seconds(rules, self._local(now), self.consumed_now(child_id, now))

    def refusal(self, child_id: str, now: datetime) -> str | None:
        """Motif qui empêche l'enfant de regarder maintenant selon ses règles (autres sessions ignorées)."""
        profile = self.profiles.get(child_id)
        if profile is None:
            return END_PROFILE_REMOVED
        return child_refusal(profile, self._local(now), self.consumed_now(child_id, now))

    def in_session(self, profile_id: str) -> bool:
        return self.session is not None and self.session.profile_id == profile_id

    def planned_end(self, now: datetime) -> tuple[datetime | None, str | None]:
        """Coupure prévue de la session en cours et son motif (None : aucune)."""
        session = self.session
        if session is None:
            return None, None
        candidates: list[tuple[datetime, str]] = []
        limit = self.settings.parent_max
        if session.kind == KIND_CHILD:
            candidates.append((self.midnight_after(now), END_MIDNIGHT))
            if session.ignore_rules:
                if limit:
                    candidates.append((session.started_at + limit, END_SAFETY_LIMIT))
            elif (profile := self.profiles.get(session.profile_id)) is not None:
                rules = profile.rules or WeeklyRules.empty()
                candidates.append((now + timedelta(seconds=self.remaining(session.profile_id, now)), END_QUOTA))
                candidates.append((self._slot_end(rules, now), END_SCHEDULE))
        elif limit:
            candidates.append((session.started_at + limit, END_SAFETY_LIMIT))
        if not candidates:
            return None, None
        return min(candidates, key=lambda c: (c[0], DEADLINE_ORDER.index(c[1])))

    def next_slot(self, child_id: str, now: datetime) -> tuple[datetime, datetime] | None:
        """Prochaine plage qui commence après maintenant, un jour où l'enfant peut regarder."""
        profile = self.profiles.get(child_id)
        if profile is None or not profile.enabled or profile.rules is None:
            return None
        rules = profile.rules
        today = self._local(now).date()
        exhausted_today = self.remaining(child_id, now) < 60
        for offset in range(8):
            day = today + timedelta(days=offset)
            key = DAYS[day.weekday()]
            if rules.quota_minutes[key] <= 0 or (offset == 0 and exhausted_today):
                continue
            for slot in rules.slots[key]:
                start = self._at(day, slot.start)
                if start > now:
                    return start, self._at(day, slot.end)
        return None

    def next_deadline(self, now: datetime) -> datetime:
        deadlines = [self.midnight_after(now), self._next_boundary(now)]
        if self.session is not None:
            end, _ = self.planned_end(now)
            if end is not None:
                deadlines.append(end)
                warning = self.settings.warning
                if warning and not self.session.warned:
                    deadlines.append(max(now, end - warning))
            minute = now.replace(second=0, microsecond=0)
            deadlines.append(minute + HEARTBEAT)
        return min(deadlines)

    # --- entrées ----------------------------------------------------------------

    def start(
        self, profile: Profile, now: datetime, source: str = "keypad", ignore_rules: bool = False
    ) -> list[Effect]:
        """Ouvre une session ; la session précédente doit avoir été terminée par l'appelant."""
        effects = self._roll(now)
        if self.session is not None:
            raise RuntimeError("session already running")
        self.session = Session(profile.id, profile.name, profile.kind, now, source, ignore_rules and profile.kind == KIND_CHILD)
        end, _ = self.planned_end(now)
        child = profile.kind == KIND_CHILD
        effects.append(SessionStarted(replace(self.session), end, self.remaining(profile.id, now) if child else None))
        # Déjà dans la fenêtre : prévenir tout de suite, sans bip (le clavier vient d'afficher le succès).
        effects += self._warn_if_due(now, beep=False)
        return effects

    def stop(self, reason: str, now: datetime) -> list[Effect]:
        effects = self._roll(now)
        if self.session is not None:
            effects.append(self._end(reason, now))
        return effects

    def tick(self, now: datetime) -> list[Effect]:
        effects = self._roll(now)
        if self.session is None:
            return effects
        end, reason = self.planned_end(now)
        if end is not None and now >= end and reason:
            effects.append(self._end(reason, now))
            return effects
        return effects + self._warn_if_due(now, beep=True)

    def update_profiles(self, profiles: dict[str, Profile], now: datetime, child_ids: set[str] | None = None) -> list[Effect]:
        """Profils relus (rechargement). `child_ids` : toutes les sous‑entrées enfant, même illisibles."""
        self.profiles = dict(profiles)
        effects = self._roll(now)
        session = self.session
        if session is not None and session.kind == KIND_CHILD:
            profile = self.profiles.get(session.profile_id)
            if profile is None:
                effects.append(self._end(END_PROFILE_REMOVED, now))
            elif not profile.enabled:
                session.name = profile.name
                effects.append(self._end(END_PROFILE_BLOCKED, now))
            else:
                session.name = profile.name
        elif session is not None and (profile := self.profiles.get(session.profile_id)) is not None:
            session.name = profile.name
        effects += self._reevaluate(now)
        if child_ids is not None:
            # Enfants supprimés : temps purgé (un enfant illisible garde le sien).
            self.consumed = {cid: secs for cid, secs in self.consumed.items() if cid in child_ids}
        return effects

    def update_settings(self, settings: SessionSettings, now: datetime) -> list[Effect]:
        self.settings = settings
        return self._roll(now) + self._reevaluate(now)

    # --- persistance ------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "day": self.day.isoformat(),
            "consumed": dict(self.consumed),
            "session": self.session.to_dict() if self.session else None,
            "last_ended": self.last_ended,
        }

    def restore(self, data: dict[str, Any], now: datetime) -> None:
        """Relit l'état enregistré ; données illisibles → état neuf."""
        try:
            day = date.fromisoformat(data["day"]) if data.get("day") else self._local(now).date()
            consumed = {str(k): float(v) for k, v in (data.get("consumed") or {}).items()}
            session = Session.from_dict(data["session"]) if data.get("session") else None
        except (KeyError, TypeError, ValueError):
            return
        self.day, self.consumed, self.session = day, consumed, session
        last = data.get("last_ended")
        self.last_ended = last if isinstance(last, dict) else None

    def end_after_restart(self, saved_at: datetime | None, now: datetime) -> list[Effect]:
        """Démarrage : la session trouvée se termine (motif `restart`), décomptée jusqu'à l'arrêt."""
        effects: list[Effect] = []
        if self.session is not None:
            at = saved_at or self.session.started_at
            at = max(self.session.started_at, min(at, now))
            effects.append(self._end(END_RESTART, at))
        return effects + self._roll(now)

    # --- interne ----------------------------------------------------------------

    def _overlap(self, start: datetime, end: datetime) -> float:
        """Secondes de [start, end[ qui tombent dans le jour des compteurs."""
        lo = max(start, self._day_start(self.day))
        hi = min(end, self._day_start(self.day + timedelta(days=1)))
        return max(0.0, (hi - lo).total_seconds())

    def _end(self, reason: str, at: datetime) -> SessionEnded:
        session = self.session
        assert session is not None
        consumed = remaining = None
        if session.kind == KIND_CHILD:
            self.consumed[session.profile_id] = self.consumed.get(session.profile_id, 0.0) + self._overlap(session.started_at, at)
        self.session = None
        if session.kind == KIND_CHILD:
            consumed = self.consumed[session.profile_id]
            # Temps restant du jour des compteurs (une fin à minuit pile appartient encore à ce jour).
            last = min(at, self._day_start(self.day + timedelta(days=1)) - timedelta(microseconds=1))
            remaining = self.remaining(session.profile_id, last) if session.profile_id in self.profiles else None
        duration = max(timedelta(0), at - session.started_at)
        self.last_ended = {
            "profile": session.name,
            "profile_id": session.profile_id,
            "kind": session.kind,
            "reason": reason,
            "at": at.isoformat(),
            "duration": round(duration.total_seconds()),
        }
        return SessionEnded(session, reason, at, duration, reason not in NO_CUT, consumed, remaining)

    def _roll(self, now: datetime) -> list[Effect]:
        """Changement de jour : session enfant terminée à minuit (D7), compteurs remis à zéro."""
        effects: list[Effect] = []
        today = self._local(now).date()
        if today <= self.day:
            return effects
        midnight = self._day_start(self.day + timedelta(days=1))
        session = self.session
        if session is not None and session.kind == KIND_CHILD:
            # Motif de l'échéance juste avant minuit (une fin de plage ou de quota à 00:00 prime).
            _, reason = self.planned_end(midnight - timedelta(microseconds=1))
            effects.append(self._end(reason or END_MIDNIGHT, max(session.started_at, midnight)))
        self.day = today
        self.consumed = {}
        return effects

    def _warn_if_due(self, now: datetime, beep: bool) -> list[Effect]:
        session = self.session
        warning = self.settings.warning
        if session is None or session.warned or not warning:
            return []
        end, _ = self.planned_end(now)
        if end is None or end - now > warning:
            return []
        session.warned = True
        minutes = max(1, math.ceil((end - now).total_seconds() / 60 - 0.01))
        return [SessionWarning(replace(session), minutes, end, beep)]

    def _reevaluate(self, now: datetime) -> list[Effect]:
        """Règles ou réglages modifiés : fin si l'échéance est dépassée, avertissement réarmé."""
        session = self.session
        if session is None:
            return []
        end, reason = self.planned_end(now)
        if end is not None and reason and now >= end:
            return [self._end(reason, now)]
        if session.warned and (end is None or end - now > self.settings.warning):
            session.warned = False
        return self._warn_if_due(now, beep=True)

    def _slot_end(self, rules: WeeklyRules, now: datetime) -> datetime:
        """Fin de la plage en cours (instant UTC), ou maintenant si l'instant est hors plage."""
        local = self._local(now)
        minute = local.hour * 60 + local.minute
        for slot in rules.slots[DAYS[local.weekday()]]:
            if slot.start <= minute < slot.end:
                return self._at(local.date(), slot.end)
        return now

    def _next_boundary(self, now: datetime) -> datetime:
        """Prochain début ou fin de plage d'un enfant aujourd'hui (entités « Autorisé maintenant »…)."""
        local = self._local(now)
        day = DAYS[local.weekday()]
        best = self.midnight_after(now)
        for profile in self.profiles.values():
            if profile.kind != KIND_CHILD or profile.rules is None:
                continue
            for slot in profile.rules.slots[day]:
                for minutes in (slot.start, slot.end):
                    at = self._at(local.date(), minutes)
                    if now < at < best:
                        best = at
        return best

