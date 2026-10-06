"""Description des événements de la prise et du clavier dans le journal (français / anglais)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from homeassistant.core import Event, HomeAssistant, callback

from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    EVENT_ACCESS_DENIED,
    EVENT_ACCESS_GRANTED,
    EVENT_BYPASS,
    EVENT_KEYPAD_OFF,
    EVENT_LOCKOUT,
    EVENT_PLUG_BACK,
    EVENT_PLUG_LOST,
    EVENT_SESSION_ENDED,
    EVENT_SESSION_STARTED,
    EVENT_SESSION_WARNING,
    EVENT_STANDBY,
)

# Clés de description du journal (homeassistant.components.logbook), sans importer le composant.
NAME = "name"
MESSAGE = "message"
ENTITY_ID = "entity_id"

TEXTS: dict[str, dict[str, Any]] = {
    "fr": {
        "bypass": "prise allumée sans autorisation, recoupée",
        "bypass_tolerated": "prise allumée à la main (toléré)",
        "standby": "télé en veille ({power} W), prise coupée",
        "standby_unknown": "télé en veille, prise coupée",
        "standby_kept": "télé en veille ({power} W), prise non coupée",
        "standby_kept_unknown": "télé en veille, prise non coupée",
        "lost": "prise injoignable",
        "back": "prise de nouveau joignable après {duration}",
        "granted_child": "{profile} a allumé la télé ({source})",
        "granted_parent": "{profile} a allumé la télé (code parent, {source})",
        "denied": "accès refusé à {profile} : {reason}",
        "denied_unknown": "accès refusé : {reason}",
        "lockout": "clavier verrouillé jusqu'à {until} après trop de codes faux",
        "keypad_off": "télé coupée depuis le clavier",
        "keypad_off_refused": "coupure depuis le clavier refusée : {reason}",
        "keypad": "clavier",
        "action": "action",
        "stopped_child": "{profile} a éteint la télé ({source})",
        "stopped_parent": "{profile} a éteint la télé (code parent, {source})",
        "handover": "{profile} a pris la télé ({source})",
        "session_child": "session de {profile} jusqu'à {end}",
        "session_parent": "session parent de {profile} jusqu'à {end}",
        "session_open": "session de {profile} sans limite",
        "session_ignore": "session de {profile} sans règles jusqu'à {end}",
        "warning": "{profile} : coupure dans {minutes} min",
        "ended": "fin de la session de {profile} après {duration} : {reason}",
        "end_reasons": {
            "user": "code ressaisi",
            "parent": "code parent",
            "keypad_off": "touche d'arrêt",
            "stopped": "arrêtée par un parent",
            "quota": "quota épuisé",
            "schedule": "fin de la plage horaire",
            "midnight": "minuit",
            "safety_limit": "durée maximale atteinte",
            "standby": "télé en veille",
            "plug_off": "prise coupée",
            "plug_lost": "prise injoignable",
            "control_inactive": "contrôle suspendu",
            "profile_blocked": "enfant désactivé",
            "profile_removed": "enfant supprimé",
            "restart": "redémarrage de Home Assistant",
            "handover": "télé reprise par un autre enfant",
        },
        "reasons": {
            "locked_out": "clavier verrouillé",
            "invalid_code": "code inconnu",
            "control_inactive": "contrôle suspendu",
            "plug_unavailable": "prise injoignable",
            "profile_blocked": "profil désactivé",
            "outside_schedule": "hors des plages horaires",
            "quota_exhausted": "quota épuisé",
            "tv_in_use": "télé déjà utilisée",
            "error": "erreur interne",
        },
    },
    "en": {
        "bypass": "plug turned on without permission, turned off again",
        "bypass_tolerated": "plug turned on manually (tolerated)",
        "standby": "TV on standby ({power} W), plug turned off",
        "standby_unknown": "TV on standby, plug turned off",
        "standby_kept": "TV on standby ({power} W), plug left on",
        "standby_kept_unknown": "TV on standby, plug left on",
        "lost": "plug unreachable",
        "back": "plug reachable again after {duration}",
        "granted_child": "{profile} turned the TV on ({source})",
        "granted_parent": "{profile} turned the TV on (parent code, {source})",
        "denied": "access denied to {profile}: {reason}",
        "denied_unknown": "access denied: {reason}",
        "lockout": "keypad locked until {until} after too many wrong codes",
        "keypad_off": "TV turned off from the keypad",
        "keypad_off_refused": "turning off from the keypad refused: {reason}",
        "keypad": "keypad",
        "action": "action",
        "stopped_child": "{profile} turned the TV off ({source})",
        "stopped_parent": "{profile} turned the TV off (parent code, {source})",
        "handover": "{profile} took over the TV ({source})",
        "session_child": "{profile}'s session until {end}",
        "session_parent": "parent session of {profile} until {end}",
        "session_open": "{profile}'s session without limit",
        "session_ignore": "{profile}'s session without rules until {end}",
        "warning": "{profile}: cut-off in {minutes} min",
        "ended": "end of {profile}'s session after {duration}: {reason}",
        "end_reasons": {
            "user": "code entered again",
            "parent": "parent code",
            "keypad_off": "stop key",
            "stopped": "stopped by a parent",
            "quota": "quota used up",
            "schedule": "end of allowed hours",
            "midnight": "midnight",
            "safety_limit": "maximum length reached",
            "standby": "TV on standby",
            "plug_off": "plug turned off",
            "plug_lost": "plug unreachable",
            "control_inactive": "control suspended",
            "profile_blocked": "child disabled",
            "profile_removed": "child removed",
            "restart": "Home Assistant restart",
            "handover": "TV taken over by another child",
        },
        "reasons": {
            "locked_out": "keypad locked",
            "invalid_code": "unknown code",
            "control_inactive": "control suspended",
            "plug_unavailable": "plug unreachable",
            "profile_blocked": "profile disabled",
            "outside_schedule": "outside allowed hours",
            "quota_exhausted": "quota used up",
            "tv_in_use": "TV already in use",
            "error": "internal error",
        },
    },
}


def format_duration(seconds: int) -> str:
    """40 s, 3 min 05 s, 1 h 02 min."""
    hours, rest = divmod(int(seconds), 3600)
    minutes, secs = divmod(rest, 60)
    if hours:
        return f"{hours} h {minutes:02d} min"
    if minutes:
        return f"{minutes} min {secs:02d} s"
    return f"{secs} s"


@callback
def async_describe_events(
    hass: HomeAssistant,
    async_describe_event: Callable[[str, str, Callable[[Event], dict[str, Any]]], None],
) -> None:
    def texts() -> dict[str, Any]:
        return TEXTS.get(hass.config.language.split("-")[0], TEXTS["en"])

    def name(event: Event) -> str:
        entry = hass.config_entries.async_get_entry(event.data.get("entry_id", ""))
        return f"Zapette – {entry.title}" if entry else "Zapette"

    @callback
    def describe(event: Event) -> dict[str, Any]:
        data = event.data
        if event.event_type == EVENT_BYPASS:
            message = texts()["bypass_tolerated" if data.get("tolerated") else "bypass"]
        elif event.event_type == EVENT_STANDBY:
            power = data.get("power")
            key = "standby" if data.get("cut", True) else "standby_kept"
            message = texts()[key].format(power=round(power)) if power is not None else texts()[f"{key}_unknown"]
        elif event.event_type == EVENT_PLUG_LOST:
            message = texts()["lost"]
        elif event.event_type == EVENT_PLUG_BACK:
            message = texts()["back"].format(duration=format_duration(data.get("duration", 0)))
        elif event.event_type in (EVENT_SESSION_STARTED, EVENT_SESSION_WARNING, EVENT_SESSION_ENDED):
            message = describe_session(texts(), event)
        else:
            message = describe_access(texts(), event)
        return {NAME: name(event), MESSAGE: message, ENTITY_ID: data.get("entity_id")}

    for event_type in (
        EVENT_BYPASS,
        EVENT_STANDBY,
        EVENT_PLUG_LOST,
        EVENT_PLUG_BACK,
        EVENT_ACCESS_GRANTED,
        EVENT_ACCESS_DENIED,
        EVENT_LOCKOUT,
        EVENT_KEYPAD_OFF,
        EVENT_SESSION_STARTED,
        EVENT_SESSION_WARNING,
        EVENT_SESSION_ENDED,
    ):
        async_describe_event(DOMAIN, event_type, describe)


def describe_access(texts: dict[str, Any], event: Event) -> str:
    """Accès accordé ou refusé, verrouillage (aucun code dans les données)."""
    data = event.data
    if event.event_type == EVENT_KEYPAD_OFF:
        if data.get("done"):
            return texts["keypad_off"]
        return texts["keypad_off_refused"].format(reason=texts["reasons"].get(data.get("reason"), data.get("reason")))
    if event.event_type == EVENT_LOCKOUT:
        until = dt_util.parse_datetime(data.get("until") or "")
        return texts["lockout"].format(until=dt_util.as_local(until).strftime("%H:%M") if until else "?")
    source = texts.get(data.get("source"), data.get("source"))
    if event.event_type == EVENT_ACCESS_GRANTED:
        parent = data.get("kind") == "parent"
        if data.get("action") == "stop":
            key = "stopped_parent" if parent else "stopped_child"
        elif data.get("action") == "handover":
            key = "handover"
        else:
            key = "granted_parent" if parent else "granted_child"
        return texts[key].format(profile=data.get("profile"), source=source)
    reason = texts["reasons"].get(data.get("reason"), data.get("reason"))
    if data.get("profile"):
        return texts["denied"].format(profile=data["profile"], reason=reason)
    return texts["denied_unknown"].format(reason=reason)


def _hhmm(value: str | None) -> str:
    moment = dt_util.parse_datetime(value or "")
    return dt_util.as_local(moment).strftime("%H:%M") if moment else "?"


def describe_session(texts: dict[str, Any], event: Event) -> str:
    """Ouverture, avertissement et fin de session."""
    data = event.data
    profile = data.get("profile")
    if event.event_type == EVENT_SESSION_WARNING:
        return texts["warning"].format(profile=profile, minutes=data.get("minutes_left"))
    if event.event_type == EVENT_SESSION_ENDED:
        reason = texts["end_reasons"].get(data.get("reason"), data.get("reason"))
        return texts["ended"].format(profile=profile, duration=format_duration(data.get("duration", 0)), reason=reason)
    if not data.get("planned_end"):
        return texts["session_open"].format(profile=profile)
    if data.get("kind") == "parent":
        key = "session_parent"
    else:
        key = "session_ignore" if data.get("ignore_rules") else "session_child"
    return texts[key].format(profile=profile, end=_hhmm(data.get("planned_end")))
