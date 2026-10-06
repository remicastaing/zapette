"""Réglages d'une télévision : sections, défauts, bornes, validation ; nom de la télé ; parents.

Source unique partagée par les flux (options, « Reconfigurer ») et le panneau.
Ce module n'importe rien de Home Assistant.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .const import (
    CONF_LOCKOUT_DURATION,
    CONF_LOCKOUT_FAILURES,
    CONF_LOCKOUT_WINDOW,
    CONF_OFF_KEY,
    CONF_PARENT_MAX_HOURS,
    CONF_STANDBY_CUT,
    CONF_STANDBY_DELAY,
    CONF_STANDBY_THRESHOLD,
    CONF_TOLERATE_MANUAL,
    CONF_WARNING_BEEP,
    CONF_WARNING_MINUTES,
    DEFAULT_LOCKOUT_DURATION,
    DEFAULT_LOCKOUT_FAILURES,
    DEFAULT_LOCKOUT_WINDOW,
    DEFAULT_OFF_KEY,
    DEFAULT_PARENT_MAX_HOURS,
    DEFAULT_STANDBY_CUT,
    DEFAULT_STANDBY_DELAY,
    DEFAULT_STANDBY_THRESHOLD,
    DEFAULT_TOLERATE_MANUAL,
    DEFAULT_WARNING_BEEP,
    DEFAULT_WARNING_MINUTES,
    OFF_KEY_NONE,
)
from .settings import SettingsError, name_key, normalize_name

# Touches de validation d'un clavier IAS ACE (noms Zigbee2MQTT), proposées comme touche d'arrêt.
OFF_KEYS = (OFF_KEY_NONE, "arm_all_zones", "arm_day_zones", "arm_night_zones", "disarm")

SECTION_PLUG_BEHAVIOR = "plug_behavior"
SECTION_KEYPAD_GUARD = "keypad_guard"
SECTION_SESSIONS = "sessions"


@dataclass(frozen=True)
class Setting:
    """Un réglage des options : type `bool`, `int` (bornes, unité) ou `choice` (valeurs)."""

    key: str
    kind: str
    default: Any
    low: int | None = None
    high: int | None = None
    unit: str | None = None
    choices: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"key": self.key, "type": self.kind, "default": self.default}
        if self.kind == "int":
            result.update(min=self.low, max=self.high, unit=self.unit)
        if self.kind == "choice":
            result["choices"] = list(self.choices)
        return result


SECTIONS: dict[str, tuple[Setting, ...]] = {
    SECTION_PLUG_BEHAVIOR: (
        Setting(CONF_TOLERATE_MANUAL, "bool", DEFAULT_TOLERATE_MANUAL),
        Setting(CONF_STANDBY_THRESHOLD, "int", DEFAULT_STANDBY_THRESHOLD, 1, 500, "W"),
        Setting(CONF_STANDBY_DELAY, "int", DEFAULT_STANDBY_DELAY, 1, 60, "min"),
        Setting(CONF_STANDBY_CUT, "bool", DEFAULT_STANDBY_CUT),
    ),
    SECTION_KEYPAD_GUARD: (
        Setting(CONF_LOCKOUT_FAILURES, "int", DEFAULT_LOCKOUT_FAILURES, 3, 20),
        Setting(CONF_LOCKOUT_WINDOW, "int", DEFAULT_LOCKOUT_WINDOW, 1, 60, "min"),
        Setting(CONF_LOCKOUT_DURATION, "int", DEFAULT_LOCKOUT_DURATION, 1, 120, "min"),
        Setting(CONF_OFF_KEY, "choice", DEFAULT_OFF_KEY, choices=OFF_KEYS),
    ),
    SECTION_SESSIONS: (
        Setting(CONF_WARNING_MINUTES, "int", DEFAULT_WARNING_MINUTES, 0, 30, "min"),
        Setting(CONF_WARNING_BEEP, "bool", DEFAULT_WARNING_BEEP),
        Setting(CONF_PARENT_MAX_HOURS, "int", DEFAULT_PARENT_MAX_HOURS, 0, 24, "h"),
    ),
}


def setting(key: str) -> Setting:
    return next(s for settings in SECTIONS.values() for s in settings if s.key == key)


def _section(section: str) -> tuple[Setting, ...]:
    try:
        return SECTIONS[section]
    except KeyError:
        raise SettingsError("unknown_section", "section") from None


def section_values(section: str, options: dict[str, Any]) -> dict[str, Any]:
    """Valeurs enregistrées complétées par les défauts (une ancienne valeur hors bornes est rendue telle quelle)."""
    return {s.key: options.get(s.key, s.default) for s in _section(section)}


def schema_payload() -> dict[str, list[dict[str, Any]]]:
    return {section: [s.to_dict() for s in settings] for section, settings in SECTIONS.items()}


def validate_value(item: Setting, value: Any) -> Any:
    if item.kind == "bool":
        if not isinstance(value, bool):
            raise SettingsError("value_invalid", item.key)
        return value
    if item.kind == "choice":
        if value not in item.choices:
            raise SettingsError("value_invalid", item.key)
        return value
    if isinstance(value, bool) or not isinstance(value, int | float) or value != int(value):
        raise SettingsError("value_range", item.key)
    number = int(value)
    if not item.low <= number <= item.high:
        raise SettingsError("value_range", item.key)
    return number


def validate_section(section: str, values: dict[str, Any]) -> dict[str, Any]:
    """Toutes les clés de la section, et elles seules ; renvoie les valeurs normalisées."""
    settings = _section(section)
    keys = {s.key for s in settings}
    for key in values:
        if key not in keys:
            raise SettingsError("value_invalid", key)
    result: dict[str, Any] = {}
    for item in settings:
        if item.key not in values:
            raise SettingsError("value_invalid", item.key)
        result[item.key] = validate_value(item, values[item.key])
    return result


# --- Nom de la télévision ---------------------------------------------------------


def normalize_tv_name(name: str, other_names: list[str]) -> str:
    """Mêmes règles qu'un prénom ; unique parmi les autres télévisions (sans casse ni accents)."""
    name = normalize_name(name)
    taken = set()
    for other in other_names:
        try:
            taken.add(name_key(other))
        except SettingsError:
            continue
    if name_key(name) in taken:
        raise SettingsError("tv_name_in_use", "name")
    return name


# --- Parents ------------------------------------------------------------------------


def check_parent_name(name: str, parents: list[dict[str, Any]], editing_id: str | None = None) -> str:
    name = normalize_name(name)
    others = {name_key(p["name"]) for p in parents if p["id"] != editing_id}
    if name_key(name) in others:
        raise SettingsError("parent_name_in_use", "name")
    return name


def check_parent_delete(parents: list[dict[str, Any]], parent_id: str) -> list[dict[str, Any]]:
    """Liste sans ce parent ; refus du dernier parent ou d'un identifiant inconnu."""
    if not any(p["id"] == parent_id for p in parents):
        raise SettingsError("not_found", "parent")
    if len(parents) <= 1:
        raise SettingsError("last_parent_code", "parent")
    return [p for p in parents if p["id"] != parent_id]
