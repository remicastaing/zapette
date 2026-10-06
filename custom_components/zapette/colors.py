"""Couleur stable d'un enfant (H3), sans Home Assistant.

L'indice dans la palette du panneau est dérivé de l'identifiant de l'enfant (sous‑entrée), pas de
son rang : supprimer un enfant ne change pas la couleur des autres, sauf de celui qui était entré en
collision avec lui. Les collisions entre enfants présents sont résolues dans l'ordre des
identifiants, par sondage linéaire.
"""

from __future__ import annotations

from collections.abc import Iterable
import hashlib

PALETTE_SIZE = 8
COLOR_PARENT = "parent"
COLOR_DELETED = "deleted"
COLOR_NEUTRAL = "neutral"


def preferred_color(child_id: str) -> int:
    return int(hashlib.sha256(child_id.encode()).hexdigest(), 16) % PALETTE_SIZE


def child_colors(child_ids: Iterable[str]) -> dict[str, int]:
    """Indice de palette de chaque enfant présent."""
    taken: set[int] = set()
    colors: dict[str, int] = {}
    for child_id in sorted(set(child_ids)):
        preferred = preferred_color(child_id)
        color = next(
            ((preferred + step) % PALETTE_SIZE for step in range(PALETTE_SIZE) if (preferred + step) % PALETTE_SIZE not in taken),
            preferred,  # plus d'enfants que de couleurs : partage
        )
        taken.add(color)
        colors[child_id] = color
    return colors
