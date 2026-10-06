"""Commandes WebSocket du panneau Zapette."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.config_entries import ConfigEntry, ConfigSubentry
from homeassistant.core import HomeAssistant, callback
from homeassistant.util import dt as dt_util

from .codes import async_check_new_code
from .colors import child_colors
from .const import DOMAIN, SUBENTRY_CHILD
from .history_view import day_bounds, week_monday, week_view
from .settings import Child, SettingsError, rules_from_minutes, rules_to_minutes


@callback
def async_register_commands(hass: HomeAssistant) -> None:
    websocket_api.async_register_command(hass, ws_instances)
    websocket_api.async_register_command(hass, ws_children)
    websocket_api.async_register_command(hass, ws_update_child)
    websocket_api.async_register_command(hass, ws_set_child_code)
    websocket_api.async_register_command(hass, ws_history)
    websocket_api.async_register_command(hass, ws_history_week)

    from .api_settings import async_register as async_register_settings  # importe api : import différé

    async_register_settings(hass)

MAX_PERIOD = timedelta(days=92)
ERR_INVALID_PERIOD = "invalid_period"


def _children(entry: ConfigEntry) -> list[ConfigSubentry]:
    return [sub for sub in entry.subentries.values() if sub.subentry_type == SUBENTRY_CHILD]


def _child_name(subentry: ConfigSubentry) -> str:
    try:
        return Child.from_dict(dict(subentry.data)).name
    except SettingsError:
        return subentry.title


def _child_payload(subentry: ConfigSubentry, color: int = 0) -> dict[str, Any]:
    try:
        child = Child.from_dict(dict(subentry.data))
    except SettingsError:
        return {"subentry_id": subentry.subentry_id, "name": subentry.title, "invalid": True, "color": color}
    return {
        "subentry_id": subentry.subentry_id,
        "color": color,
        "name": child.name,
        "icon": child.icon,
        "enabled": child.enabled,
        **rules_to_minutes(child.rules),
    }


def _get_entry(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> ConfigEntry | None:
    entry = hass.config_entries.async_get_entry(msg["entry_id"])
    if entry is None or entry.domain != DOMAIN:
        connection.send_error(msg["id"], websocket_api.ERR_NOT_FOUND, "Instance Zapette introuvable")
        return None
    return entry


def _get_child(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> tuple[ConfigEntry, ConfigSubentry] | None:
    if (entry := _get_entry(hass, connection, msg)) is None:
        return None
    subentry = entry.subentries.get(msg["subentry_id"])
    if subentry is None or subentry.subentry_type != SUBENTRY_CHILD:
        connection.send_error(msg["id"], websocket_api.ERR_NOT_FOUND, "Enfant introuvable")
        return None
    return entry, subentry


@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required("type"): "zapette/instances"})
@callback
def ws_instances(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    connection.send_result(
        msg["id"],
        [{"entry_id": e.entry_id, "title": e.title} for e in hass.config_entries.async_entries(DOMAIN)],
    )


@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required("type"): "zapette/children", vol.Required("entry_id"): str})
@callback
def ws_children(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    if (entry := _get_entry(hass, connection, msg)) is None:
        return
    children = _children(entry)
    colors = child_colors(sub.subentry_id for sub in children)
    runtime = getattr(entry, "runtime_data", None)
    session = runtime.sessions.session if runtime else None
    watching = session.profile_id if session else None
    connection.send_result(
        msg["id"],
        {
            "entry_id": entry.entry_id,
            "title": entry.title,
            "children": [
                {**_child_payload(sub, colors[sub.subentry_id]), "in_session": sub.subentry_id == watching}
                for sub in children
            ],
        },
    )


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): "zapette/child/update",
        vol.Required("entry_id"): str,
        vol.Required("subentry_id"): str,
        vol.Required("enabled"): bool,
        vol.Required("quota"): [int],
        vol.Required("slots"): [[[int]]],
    }
)
@callback
def ws_update_child(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Enregistre activation, quotas et plages (prénom et code restent inchangés)."""
    if (found := _get_child(hass, connection, msg)) is None:
        return
    entry, subentry = found
    try:
        child = Child.from_dict(dict(subentry.data))
        child.rules = rules_from_minutes(msg["quota"], msg["slots"])
    except SettingsError as err:
        connection.send_error(msg["id"], err.key, err.field)
        return
    child.enabled = msg["enabled"]
    hass.config_entries.async_update_subentry(entry, subentry, data=child.to_dict())
    colors = child_colors(sub.subentry_id for sub in _children(entry))
    connection.send_result(msg["id"], _child_payload(entry.subentries[subentry.subentry_id], colors[subentry.subentry_id]))


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): "zapette/child/set_code",
        vol.Required("entry_id"): str,
        vol.Required("subentry_id"): str,
        vol.Required("code"): str,
        vol.Required("code_confirm"): str,
    }
)
@websocket_api.async_response
async def ws_set_child_code(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    if (found := _get_child(hass, connection, msg)) is None:
        return
    entry, subentry = found
    error, hashed = await async_check_new_code(hass, entry, msg, exclude_child=subentry.subentry_id)
    if error:
        connection.send_error(msg["id"], error, "code")
        return
    hass.config_entries.async_update_subentry(entry, subentry, data={**subentry.data, "code": hashed})
    connection.send_result(msg["id"])


def _get_history(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> ConfigEntry | None:
    """Instance chargée (son historique vit dans `runtime_data`)."""
    if (entry := _get_entry(hass, connection, msg)) is None:
        return None
    if getattr(entry, "runtime_data", None) is None:
        connection.send_error(msg["id"], websocket_api.ERR_NOT_FOUND, "Instance Zapette non chargée")
        return None
    return entry


@websocket_api.require_admin
@websocket_api.websocket_command(
    {vol.Required("type"): "zapette/history", vol.Required("entry_id"): str, vol.Required("start"): str, vol.Required("end"): str}
)
@callback
def ws_history(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Historique brut d'une période (au plus 92 jours) ; éléments en cours avec `end` = None."""
    if (entry := _get_history(hass, connection, msg)) is None:
        return
    start, end = dt_util.parse_datetime(msg["start"]), dt_util.parse_datetime(msg["end"])
    if start is None or end is None or start.tzinfo is None or end.tzinfo is None or not start < end <= start + MAX_PERIOD:
        connection.send_error(msg["id"], ERR_INVALID_PERIOD, "Période invalide (ISO avec fuseau, 92 jours au plus)")
        return
    connection.send_result(
        msg["id"],
        {
            "entry_id": entry.entry_id,
            "entries": entry.runtime_data.history.read(start, end),
            "now": dt_util.utcnow().isoformat(),
        },
    )


@websocket_api.require_admin
@websocket_api.websocket_command(
    {vol.Required("type"): "zapette/history/week", vol.Required("entry_id"): str, vol.Optional("week"): str}
)
@callback
def ws_history_week(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Semaine préparée pour le calendrier (fuseau de Home Assistant) ; jamais après la semaine en cours."""
    if (entry := _get_history(hass, connection, msg)) is None:
        return
    tz = dt_util.get_default_time_zone()
    now = dt_util.utcnow()
    current = week_monday(now.astimezone(tz).date())
    try:
        monday = week_monday(date.fromisoformat(msg["week"])) if msg.get("week") else current
    except ValueError:
        connection.send_error(msg["id"], ERR_INVALID_PERIOD, "Semaine invalide (AAAA-MM-JJ)")
        return
    monday = min(monday, current)
    bounds = day_bounds(monday, tz)
    children = {sub.subentry_id: _child_name(sub) for sub in _children(entry)}
    result = week_view(
        entry.runtime_data.history.read(bounds[0], bounds[7]),
        week_start=monday,
        tz=tz,
        now=now,
        children=children,
        colors=child_colors(children),
    )
    connection.send_result(msg["id"], {"entry_id": entry.entry_id, "title": entry.title, **result})
