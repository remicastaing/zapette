"""Diagnostics : configuration et état, codes et empreintes expurgés."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

TO_REDACT = {"code", "salt", "hash"}


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry) -> dict[str, Any]:
    runtime = entry.runtime_data
    access = runtime.access
    return async_redact_data(
        {
            "entry": {"title": entry.title, "data": dict(entry.data), "options": dict(entry.options)},
            "children": [
                {"subentry_id": sid, "title": sub.title, "data": dict(sub.data)}
                for sid, sub in entry.subentries.items()
            ],
            "plug": {
                "entity_id": runtime.plug.plug_entity,
                "available": runtime.plug.logic.available,
                "desired_on": runtime.plug.logic.desired_on,
                "control_active": runtime.plug.logic.control_active,
            }
            if runtime.plug
            else None,
            "keypad": {
                "topic": access.keypad_topic,
                "available": access.status.available,
                "battery": access.status.battery,
                "feedback_modes": getattr(access.adapter, "modes", None),
                "locked": access.is_locked(),
            },
            "sessions": {
                "session": runtime.sessions.session.to_dict() if runtime.sessions.session else None,
                "planned_end": (end.isoformat() if (end := runtime.sessions.planned_end()[0]) else None),
                "warning_beep": runtime.sessions.warning_beep,
            },
            "history": {
                "entries": len(runtime.history.log.entries),
                "by_type": _count(runtime.history.log.entries),
                "oldest": runtime.history.log.entries[0].get("end") or runtime.history.log.entries[0].get("at")
                if runtime.history.log.entries
                else None,
                "open": runtime.history.log.open,
                "stopped_at": runtime.history.log.stopped_at,
            },
            "store": access.state.data,
        },
        TO_REDACT,
    )


def _count(entries: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for entry in entries:
        counts[entry["t"]] = counts.get(entry["t"], 0) + 1
    return counts
