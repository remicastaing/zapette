"""Paramétrage des enfants : modèle, validation, avertissements.

Ce module n'importe rien de Home Assistant.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any
import unicodedata

SCHEMA_VERSION = 1

DAYS: tuple[str, ...] = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
WEEKDAYS = DAYS[:5]
WEEKEND = DAYS[5:]
DAY_SHORTCUTS: dict[str, tuple[str, ...]] = {
    "all": DAYS,
    "weekdays": WEEKDAYS,
    "weekend": WEEKEND,
}

MAX_SLOTS = 4
MIN_SLOT_MINUTES = 5
QUOTA_STEP = 5
MINUTES_PER_DAY = 24 * 60
NAME_RE = re.compile(r"^[\w\s'\-]{1,30}$")
DEFAULT_ICON = "mdi:account-child"


class SettingsError(ValueError):
    """Erreur de validation, avec la clé de traduction et le champ concerné."""

    def __init__(self, key: str, field_name: str = "base") -> None:
        super().__init__(key)
        self.key = key
        self.field = field_name


# --- Prénom ---------------------------------------------------------------


def normalize_name(name: str) -> str:
    name = " ".join(name.split())
    if not NAME_RE.match(name) or "_" in name:
        raise SettingsError("name_invalid", "name")
    return name


def name_key(name: str) -> str:
    """Clé d'unicité : minuscules, sans accents."""
    decomposed = unicodedata.normalize("NFKD", normalize_name(name))
    return "".join(c for c in decomposed if not unicodedata.combining(c)).casefold()


# --- Jours ----------------------------------------------------------------


def expand_days(selection: list[str]) -> list[str]:
    """Développe les raccourcis et renvoie les jours dans l'ordre de la semaine."""
    chosen: set[str] = set()
    for item in selection:
        chosen.update(DAY_SHORTCUTS.get(item, (item,)))
    days = [day for day in DAYS if day in chosen]
    if not days:
        raise SettingsError("no_day_selected", "days")
    return days


# --- Quotas ---------------------------------------------------------------


def validate_quota(minutes: int) -> int:
    if not 0 <= minutes <= MINUTES_PER_DAY:
        raise SettingsError("quota_range", "quota")
    if minutes % QUOTA_STEP:
        raise SettingsError("quota_step", "quota")
    return minutes


# --- Plages ---------------------------------------------------------------


@dataclass(frozen=True, order=True)
class Slot:
    """Plage [start, end[ en minutes depuis minuit ; end = 1440 pour minuit."""

    start: int
    end: int

    @property
    def minutes(self) -> int:
        return self.end - self.start

    def to_list(self) -> list[str]:
        return [format_minutes(self.start), format_minutes(self.end % MINUTES_PER_DAY)]

    @classmethod
    def from_list(cls, value: list[str]) -> Slot:
        start, end = parse_time(value[0]), parse_time(value[1])
        return cls(start, end or MINUTES_PER_DAY)

    def __str__(self) -> str:
        return "–".join(self.to_list())


def parse_time(value: str) -> int:
    """« HH:MM » ou « HH:MM:SS » → minutes (secondes tronquées)."""
    hours, minutes, *_ = value.split(":")
    result = int(hours) * 60 + int(minutes)
    if not 0 <= result < MINUTES_PER_DAY:
        raise ValueError(value)
    return result


def format_minutes(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def normalize_slots(pairs: list[tuple[str | None, str | None]]) -> list[Slot]:
    """Valide, trie et fusionne les plages contiguës d'une journée."""
    if len(pairs) > MAX_SLOTS:
        raise SettingsError("slot_too_many")
    slots: list[Slot] = []
    for index, (start, end) in enumerate(pairs, start=1):
        if not start and not end:
            continue
        if not start or not end:
            raise SettingsError("slot_incomplete", f"slot_{index}_{'end' if start else 'start'}")
        start_min = parse_time(start)
        end_min = parse_time(end) or MINUTES_PER_DAY
        if end_min <= start_min:
            raise SettingsError("slot_order", f"slot_{index}_end")
        if end_min - start_min < MIN_SLOT_MINUTES:
            raise SettingsError("slot_too_short", f"slot_{index}_end")
        slots.append(Slot(start_min, end_min))

    slots.sort()
    merged: list[Slot] = []
    for slot in slots:
        if merged and slot.start < merged[-1].end:
            raise SettingsError("slot_overlap")
        if merged and slot.start == merged[-1].end:
            merged[-1] = Slot(merged[-1].start, slot.end)
        else:
            merged.append(slot)
    return merged


# --- Règles hebdomadaires -------------------------------------------------


@dataclass
class WeeklyRules:
    quota_minutes: dict[str, int]
    slots: dict[str, list[Slot]]

    @classmethod
    def empty(cls) -> WeeklyRules:
        return cls({day: 0 for day in DAYS}, {day: [] for day in DAYS})

    @classmethod
    def default(cls) -> WeeklyRules:
        school = [Slot(17 * 60, 19 * 60 + 30)]
        free = [Slot(9 * 60, 12 * 60), Slot(14 * 60, 19 * 60 + 30)]
        return cls(
            {"mon": 60, "tue": 60, "wed": 120, "thu": 60, "fri": 60, "sat": 120, "sun": 120},
            {
                "mon": school, "tue": school, "thu": school, "fri": school,
                "wed": [Slot(10 * 60, 12 * 60), Slot(14 * 60, 19 * 60 + 30)],
                "sat": free, "sun": free,
            },
        )

    def copy(self) -> WeeklyRules:
        return WeeklyRules(dict(self.quota_minutes), {d: list(s) for d, s in self.slots.items()})

    def slot_minutes(self, day: str) -> int:
        return sum(slot.minutes for slot in self.slots[day])

    def is_allowed_day(self, day: str) -> bool:
        return self.quota_minutes[day] > 0 and bool(self.slots[day])


@dataclass
class Child:
    name: str
    code: dict[str, Any]
    rules: WeeklyRules = field(default_factory=WeeklyRules.default)
    icon: str = DEFAULT_ICON
    enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA_VERSION,
            "name": self.name,
            "icon": self.icon,
            "enabled": self.enabled,
            "code": self.code,
            "quota_minutes": dict(self.rules.quota_minutes),
            "slots": {day: [s.to_list() for s in self.rules.slots[day]] for day in DAYS},
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Child:
        if data.get("schema") != SCHEMA_VERSION:
            raise SettingsError("unknown_schema")
        try:
            rules = WeeklyRules(
                {day: validate_quota(int(data["quota_minutes"][day])) for day in DAYS},
                {
                    day: normalize_slots([tuple(pair) for pair in data["slots"][day]])
                    for day in DAYS
                },
            )
            return cls(
                name=normalize_name(data["name"]),
                code=dict(data["code"]),
                rules=rules,
                icon=data.get("icon") or DEFAULT_ICON,
                enabled=bool(data.get("enabled", True)),
            )
        except (KeyError, TypeError, ValueError) as err:
            raise SettingsError("invalid_data") from err


def warnings(child: Child) -> list[tuple[str, dict[str, str]]]:
    """Avertissements non bloquants : (clé, paramètres)."""
    result: list[tuple[str, dict[str, str]]] = []
    if not child.enabled:
        result.append(("disabled", {"name": child.name}))
    if not any(child.rules.is_allowed_day(day) for day in DAYS):
        result.append(("never_allowed", {"name": child.name}))
        return result
    for day in DAYS:
        quota, slots = child.rules.quota_minutes[day], child.rules.slots[day]
        if quota and not slots:
            result.append(("no_slot", {"day": day}))
        elif slots and not quota:
            result.append(("no_quota", {"day": day}))
        elif quota > child.rules.slot_minutes(day):
            result.append(("quota_exceeds_slots", {
                "day": day,
                "quota": format_duration(quota),
                "slots": format_duration(child.rules.slot_minutes(day)),
            }))
    return result


def format_duration(minutes: int) -> str:
    return f"{minutes // 60} h {minutes % 60:02d}"


# --- Format du panneau (minutes) -----------------------------------------


def rules_to_minutes(rules: WeeklyRules) -> dict[str, list[Any]]:
    """Quotas et plages indexés lundi→dimanche ; plage = [début, fin] en minutes (fin ≤ 1440)."""
    return {
        "quota": [rules.quota_minutes[day] for day in DAYS],
        "slots": [[[slot.start, slot.end] for slot in rules.slots[day]] for day in DAYS],
    }


def rules_from_minutes(quota: list[Any], slots: list[Any]) -> WeeklyRules:
    """Inverse de rules_to_minutes, avec les mêmes validations que les formulaires.

    En cas d'erreur, `SettingsError.field` contient la clé du jour concerné.
    """
    if len(quota) != len(DAYS) or len(slots) != len(DAYS):
        raise SettingsError("invalid_data")
    rules = WeeklyRules.empty()
    for index, day in enumerate(DAYS):
        try:
            rules.quota_minutes[day] = validate_quota(int(quota[index]))
            pairs = []
            for start, end in slots[index]:
                start, end = int(start), int(end)
                if not (0 <= start < MINUTES_PER_DAY and 0 < end <= MINUTES_PER_DAY):
                    raise SettingsError("slot_order")
                pairs.append((format_minutes(start), format_minutes(end % MINUTES_PER_DAY)))
            rules.slots[day] = normalize_slots(pairs)
        except SettingsError as err:
            raise SettingsError(err.key, day) from err
        except (TypeError, ValueError) as err:
            raise SettingsError("invalid_data", day) from err
    return rules
