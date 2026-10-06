"""Vue semaine de l'historique pour le calendrier du panneau (sans Home Assistant).

Découpe sessions et périodes aux minuits **locaux** (fuseau de Home Assistant), place chaque
élément à son heure d'horloge (minutes depuis minuit, fin ≤ 1440), garde les durées en temps réel
écoulé, regroupe les incidents ponctuels identiques rapprochés (H5) et prépare la légende (H3, H8).
Tranche 6 : totaux par enfant et par jour (`days[].totals`) et de la semaine
(`profiles[].week_seconds`), en secondes réelles, sessions des enfants seulement (T4).
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, tzinfo
from typing import Any

from .colors import COLOR_DELETED, COLOR_NEUTRAL, COLOR_PARENT
from .history import (
    POINTS,
    RETENTION,
    T_CONTROL_OFF,
    T_HA_DOWN,
    T_KEYPAD_OFFLINE,
    T_PLUG_LOST,
    T_POWERED,
    T_SESSION,
    entry_start,
    iso,
    parse,
)

DAY_MIN = 1440
GROUP_GAP = timedelta(minutes=10)
BANDS = (T_PLUG_LOST, T_KEYPAD_OFFLINE, T_CONTROL_OFF, T_HA_DOWN)
PARENT_KEY = "parent"
DETAIL_KEYS = ("reason", "source", "until", "tolerated", "power", "cut")


def week_monday(day: date) -> date:
    return day - timedelta(days=day.weekday())


def day_bounds(week_start: date, tz: tzinfo) -> list[datetime]:
    """Les 8 minuits locaux qui bornent les 7 jours de la semaine."""
    return [datetime.combine(week_start + timedelta(days=i), time(0), tz) for i in range(8)]


def _minute(at: datetime, tz: tzinfo, day_end: datetime) -> float:
    if at >= day_end:
        return DAY_MIN
    local = at.astimezone(tz)
    return round(local.hour * 60 + local.minute + local.second / 60, 2)


class _Profiles:
    """Profil affiché d'une entrée : prénom actuel et couleur d'un enfant présent, sinon enregistrés."""

    def __init__(self, children: dict[str, str], colors: dict[str, int]) -> None:
        self.children = children
        self.colors = colors
        self.legend: dict[str, dict[str, Any]] = {}

    def of(self, entry: dict[str, Any], legend: bool = True) -> dict[str, Any]:
        profile_id = entry.get("profile_id")
        if profile_id is None:
            return {}
        if entry.get("kind") == "parent":
            shown = {"profile_id": profile_id, "name": entry.get("name"), "kind": "parent", "color": COLOR_PARENT, "deleted": False}
            key = PARENT_KEY
        elif profile_id in self.children:
            shown = {
                "profile_id": profile_id,
                "name": self.children[profile_id],
                "kind": "child",
                "color": self.colors.get(profile_id, 0),
                "deleted": False,
            }
            key = profile_id
        else:
            shown = {"profile_id": profile_id, "name": entry.get("name"), "kind": "child", "color": COLOR_DELETED, "deleted": True}
            key = profile_id
        if legend and key not in self.legend:
            self.legend[key] = {**shown, "profile_id": None, "name": None} if key == PARENT_KEY else dict(shown)
        return shown

    def sorted_legend(self) -> list[dict[str, Any]]:
        def order(item: dict[str, Any]) -> tuple[int, str]:
            rank = 2 if item["kind"] == "parent" else 1 if item["deleted"] else 0
            return rank, str(item.get("name") or "").casefold()

        return sorted(self.legend.values(), key=order)


def week_view(
    entries: list[dict[str, Any]],
    *,
    week_start: date,
    tz: tzinfo,
    now: datetime,
    children: dict[str, str],
    colors: dict[str, int],
) -> dict[str, Any]:
    """Vue d'une semaine (lundi `week_start`) : 7 jours de sessions, bandes et marqueurs groupés."""
    bounds = day_bounds(week_start, tz)
    profiles = _Profiles(children, colors)
    days: list[dict[str, Any]] = [
        {"date": (week_start + timedelta(days=i)).isoformat(), "sessions": [], "bands": [], "markers": []} for i in range(7)
    ]
    points: list[tuple[datetime, dict[str, Any]]] = []
    seconds: dict[tuple[int, str], float] = {}  # (jour, enfant) → secondes réelles exactes

    for entry in sorted(entries, key=entry_start):
        kind = entry.get("t")
        if kind in POINTS:
            at = parse(entry.get("at"))
            if at is not None and bounds[0] <= at < bounds[7]:
                points.append((at, entry))
            continue
        start = parse(entry.get("start"))
        if start is None or kind not in (T_SESSION, T_POWERED, *BANDS):
            continue
        end = parse(entry.get("end")) if entry.get("end") else None
        if entry.get("end") and end is None:
            continue  # fin illisible : ni en cours, ni affichable
        effective = max(start, end or now)
        for i in range(7):
            low, high = bounds[i], bounds[i + 1]
            if not (start < high and (effective > low or (effective == start and start >= low))):
                continue
            clip_start, clip_end = max(start, low), min(effective, high)
            piece: dict[str, Any] = {
                "from": _minute(clip_start, tz, high) if clip_start > low else 0,
                "to": _minute(clip_end, tz, high),
                "start": iso(start),
                "end": iso(end) if end else None,
                "duration": round((effective - start).total_seconds()),
            }
            if start < low:
                piece["continued_before"] = True
            if effective > high:
                piece["continued_after"] = True
            if kind in BANDS:
                piece["type"] = kind
                piece.update({k: True for k in ("interrupted", "unclean") if entry.get(k)})
                days[i]["bands"].append(piece)
                continue
            piece["id"] = f"{kind}-{iso(start)}-{entry.get('profile_id', '')}"
            piece["kind"] = kind
            if kind == T_SESSION:
                piece.update(profiles.of(entry))
                if piece.get("kind") == "child":
                    key = (i, piece["profile_id"])
                    seconds[key] = seconds.get(key, 0.0) + (clip_end - clip_start).total_seconds()
                piece.update({k: entry[k] for k in ("reason", "source") if k in entry})
                piece.update({k: True for k in ("ignore_rules", "ongoing") if entry.get(k)})
            else:
                piece["color"] = COLOR_NEUTRAL
                piece["origin"] = entry.get("origin")
                piece.update({k: True for k in ("interrupted",) if entry.get(k)})
                if end is None:
                    piece["ongoing"] = True
            days[i]["sessions"].append(piece)

    for i, day in enumerate(days):
        day["markers"] = _group(
            [(at, e) for at, e in points if bounds[i] <= at < bounds[i + 1]], tz, bounds[i + 1], profiles
        )

    legend = profiles.sorted_legend()
    for i, day in enumerate(days):
        day["totals"] = [
            {**{k: item[k] for k in ("profile_id", "name", "color", "deleted")}, "seconds": round(seconds[(i, item["profile_id"])])}
            for item in legend
            if item["kind"] == "child" and seconds.get((i, item["profile_id"]), 0) > 0
        ]
    for item in legend:
        if item["kind"] == "child":
            item["week_seconds"] = round(sum(secs for (_, pid), secs in seconds.items() if pid == item["profile_id"]))

    minutes = [
        item["from"] if "from" in item else item["minute"]
        for day in days
        for item in (*day["sessions"], *day["bands"], *day["markers"])
    ]
    local_now = now.astimezone(tz)
    today = local_now.date()
    return {
        "week_start": week_start.isoformat(),
        "today": today.isoformat(),
        "now": iso(now),
        "now_minute": local_now.hour * 60 + local_now.minute,
        "current_week": week_start <= today < week_start + timedelta(days=7),
        "has_history": bounds[7] > now - RETENTION,
        "earliest": min(minutes, default=None),
        "days": days,
        "profiles": legend,
    }


def _group(
    points: list[tuple[datetime, dict[str, Any]]], tz: tzinfo, day_end: datetime, profiles: _Profiles
) -> list[dict[str, Any]]:
    """Regroupement en chaîne : même type, motif et profil, moins de 10 min après le précédent."""
    groups: list[dict[str, Any]] = []
    last: dict[tuple[Any, ...], tuple[datetime, dict[str, Any]]] = {}
    for at, entry in sorted(points, key=lambda p: p[0]):
        key = (entry["t"], entry.get("reason"), entry.get("profile_id"), entry.get("tolerated"), entry.get("cut"))
        item = {"at": iso(at), "minute": _minute(at, tz, day_end), **{k: entry[k] for k in DETAIL_KEYS if k in entry}}
        previous = last.get(key)
        if previous and at - previous[0] < GROUP_GAP:
            group = previous[1]
            group["items"].append(item)
            group["count"] += 1
            group["last"] = item["at"]
        else:
            group = {
                "type": entry["t"],
                "minute": item["minute"],
                "count": 1,
                "first": item["at"],
                "last": item["at"],
                "items": [item],
                **{k: entry[k] for k in DETAIL_KEYS if k in entry},
                **profiles.of(entry),
            }
            groups.append(group)
        last[key] = (at, group)
    return groups
