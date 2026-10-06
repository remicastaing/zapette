"""Journal d'utilisation d'une télévision : sessions, incidents et périodes.

Ce module n'importe rien de Home Assistant. Les instants sont des `datetime` avec fuseau, rangés en
ISO 8601 UTC à la seconde (ce qui rend le tri des chaînes chronologique). Une entrée est soit
**ponctuelle** (`at`), soit une **période** (`start`, `end`) ; elle est rangée à son instant de fin.
Aucune entrée ne porte de code, d'empreinte ni rien qui en dérive.
"""

from __future__ import annotations

import bisect
from datetime import UTC, datetime, timedelta
from typing import Any

RETENTION = timedelta(days=90)
MAX_ENTRIES = 5000
POWERED_MIN = timedelta(seconds=10)  # télé hors session plus brève : non enregistrée

T_SESSION = "session"
T_DENIED = "denied"
T_LOCKOUT = "lockout"
T_BYPASS = "bypass"
T_STANDBY = "standby"
T_CONTROL_OFF = "control_off"
T_KEYPAD_OFFLINE = "keypad_offline"
T_POWERED = "powered"
T_HA_DOWN = "ha_down"
T_PLUG_LOST = "plug_lost"  # lue depuis les pertes de la prise (tranche 1), jamais stockée ici

POINTS = frozenset({T_DENIED, T_LOCKOUT, T_BYPASS, T_STANDBY})
PERIODS = frozenset({T_SESSION, T_CONTROL_OFF, T_KEYPAD_OFFLINE, T_POWERED, T_HA_DOWN, T_PLUG_LOST})
OPEN_TYPES = (T_CONTROL_OFF, T_KEYPAD_OFFLINE, T_POWERED)

ORIGIN_PARENT = "parent"
ORIGIN_TOLERATED = "tolerated"
ORIGIN_CONTROL_INACTIVE = "control_inactive"
ORIGIN_OTHER = "other"


def iso(at: datetime) -> str:
    return at.astimezone(UTC).replace(microsecond=0).isoformat()


def parse(text: Any) -> datetime | None:
    """Instant ISO avec fuseau, ou None s'il est absent ou illisible."""
    if not isinstance(text, str):
        return None
    try:
        value = datetime.fromisoformat(text)
    except ValueError:
        return None
    return value if value.tzinfo is not None else None


def entry_key(entry: dict[str, Any]) -> str:
    """Instant de rangement : fin d'une période, instant d'un ponctuel."""
    return entry["end"] if entry["t"] in PERIODS else entry["at"]


def entry_start(entry: dict[str, Any]) -> str:
    return entry["start"] if entry["t"] in PERIODS else entry["at"]


def _valid(entry: Any) -> bool:
    if not isinstance(entry, dict) or entry.get("t") not in POINTS | PERIODS or entry.get("t") == T_PLUG_LOST:
        return False
    if entry["t"] in PERIODS:
        start, end = parse(entry.get("start")), parse(entry.get("end"))
        return start is not None and end is not None and start <= end
    return parse(entry.get("at")) is not None


def _seconds(start: datetime, end: datetime) -> int:
    return round((end - start).total_seconds())


class HistoryLog:
    """Journal d'une télévision. Neuf ou relu au démarrage, gardé tel quel au rechargement."""

    def __init__(self) -> None:
        self.entries: list[dict[str, Any]] = []  # triées par `entry_key`
        self.open: dict[str, dict[str, Any]] = {}  # type → {"start": …, (origin)}
        self.stopped_at: str | None = None

    # --- ajout -----------------------------------------------------------------

    def _add(self, entry: dict[str, Any], now: datetime) -> None:
        keys = [entry_key(e) for e in self.entries]
        self.entries.insert(bisect.bisect_right(keys, entry_key(entry)), entry)
        self.purge(now)

    def add_session(
        self,
        *,
        profile_id: str,
        name: str,
        kind: str,
        source: str,
        reason: str,
        start: datetime,
        end: datetime,
        ignore_rules: bool,
        now: datetime,
    ) -> None:
        end = max(start, end)
        entry: dict[str, Any] = {
            "t": T_SESSION,
            "start": iso(start),
            "end": iso(end),
            "profile_id": profile_id,
            "name": name,
            "kind": kind,
            "source": source,
            "reason": reason,
            "duration": _seconds(start, end),
        }
        if ignore_rules:
            entry["ignore_rules"] = True
        self._add(entry, now)

    def add_denied(
        self,
        at: datetime,
        reason: str,
        source: str,
        profile_id: str | None = None,
        name: str | None = None,
        kind: str | None = None,
    ) -> None:
        entry: dict[str, Any] = {"t": T_DENIED, "at": iso(at), "reason": reason, "source": source}
        if profile_id is not None:
            entry.update(profile_id=profile_id, name=name, kind=kind)
        self._add(entry, at)

    def add_lockout(self, at: datetime, until: datetime) -> None:
        self._add({"t": T_LOCKOUT, "at": iso(at), "until": iso(until)}, at)

    def add_bypass(self, at: datetime, tolerated: bool) -> None:
        self._add({"t": T_BYPASS, "at": iso(at), "tolerated": tolerated}, at)

    def add_standby(self, at: datetime, power: float | None, cut: bool) -> None:
        self._add({"t": T_STANDBY, "at": iso(at), "power": power, "cut": cut}, at)

    # --- périodes ----------------------------------------------------------------

    def _open(self, kind: str, now: datetime, **extra: Any) -> bool:
        if kind in self.open:
            return False
        self.open[kind] = {"start": iso(now), **extra}
        return True

    def _close(self, kind: str, end: datetime, now: datetime, interrupted: bool = False) -> bool:
        current = self.open.pop(kind, None)
        if current is None:
            return False
        start = parse(current["start"]) or end
        end = max(start, end)
        if kind == T_POWERED and not interrupted and end - start < POWERED_MIN:
            return True  # allumage aussitôt recoupé, ou session ouverte : rien à montrer
        entry: dict[str, Any] = {"t": kind, "start": iso(start), "end": iso(end)}
        entry.update({k: v for k, v in current.items() if k != "start"})
        if interrupted:
            entry["interrupted"] = True
        self._add(entry, now)
        return True

    def set_control(self, active: bool, now: datetime) -> bool:
        """« Contrôle actif » ; vrai si le journal a changé."""
        return self._close(T_CONTROL_OFF, now, now) if active else self._open(T_CONTROL_OFF, now)

    def set_keypad(self, available: bool | None, now: datetime) -> bool:
        """Disponibilité du clavier ; inconnue (None) : sans effet."""
        if available is None:
            return False
        return self._close(T_KEYPAD_OFFLINE, now, now) if available else self._open(T_KEYPAD_OFFLINE, now)

    def set_powered(self, on: bool, origin: str, now: datetime) -> bool:
        """Télé alimentée hors de toute session (origine retenue à l'ouverture)."""
        return self._open(T_POWERED, now, origin=origin) if on else self._close(T_POWERED, now, now)

    # --- arrêt et démarrage ------------------------------------------------------

    def mark_stopped(self, now: datetime) -> None:
        self.stopped_at = iso(now)

    def startup(self, last_known: datetime | None, now: datetime) -> None:
        """Démarrage de Home Assistant : périodes ouvertes closes à l'arrêt, période `ha_down`.

        L'arrêt est la dernière écriture connue (`last_known`, l'écriture finale d'un arrêt propre,
        qui date aussi la fin `restart` d'une session) ou, à défaut, `stopped_at`. Sans `stopped_at`
        (coupure de courant), le début est estimé (`unclean`).
        """
        stopped = parse(self.stopped_at)
        stop = max((t for t in (stopped, last_known) if t is not None), default=None)
        self.stopped_at = None
        if stop is None:
            self.open.clear()
            return
        stop = min(stop, now)
        for kind in OPEN_TYPES:
            self._close(kind, stop, now, interrupted=True)
        if iso(stop) == iso(now):
            return  # aucun arrêt mesurable
        entry: dict[str, Any] = {"t": T_HA_DOWN, "start": iso(stop), "end": iso(now)}
        if stopped is None:
            entry["unclean"] = True
        self._add(entry, now)

    def purge(self, now: datetime) -> None:
        limit = iso(now - RETENTION)
        keys = [entry_key(e) for e in self.entries]
        first = bisect.bisect_left(keys, limit)
        if first:
            del self.entries[:first]
        if len(self.entries) > MAX_ENTRIES:
            del self.entries[: len(self.entries) - MAX_ENTRIES]

    # --- lecture -----------------------------------------------------------------

    def between(self, start: datetime, end: datetime) -> list[dict[str, Any]]:
        """Entrées qui chevauchent `[start, end[`, puis périodes en cours (`end` = None)."""
        low, high = iso(start), iso(end)
        keys = [entry_key(e) for e in self.entries]
        found = [dict(e) for e in self.entries[bisect.bisect_left(keys, low) :] if entry_start(e) < high]
        for kind in OPEN_TYPES:
            if (current := self.open.get(kind)) and current["start"] < high:
                found.append({"t": kind, **current, "end": None})
        return found

    # --- persistance -------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        return {"entries": self.entries, "open": self.open, "stopped_at": self.stopped_at}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HistoryLog:
        """Relecture tolérante : une entrée ou une période illisible est ignorée."""
        log = cls()
        entries = data.get("entries") if isinstance(data, dict) else None
        log.entries = sorted((e for e in entries or [] if _valid(e)), key=entry_key)
        opened = data.get("open") if isinstance(data, dict) else None
        if isinstance(opened, dict):
            for kind in OPEN_TYPES:
                current = opened.get(kind)
                if isinstance(current, dict) and parse(current.get("start")):
                    log.open[kind] = dict(current)
        stopped = data.get("stopped_at") if isinstance(data, dict) else None
        log.stopped_at = stopped if parse(stopped) else None
        return log
