"""Interface commune des claviers.

Un adaptateur transforme les messages d'un clavier en saisies (`Submission`) et en état
(`KeypadStatus`), et sait, si le clavier le permet, lui renvoyer un succès ou un échec.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

SOURCE_KEYPAD = "keypad"
SOURCE_ACTION = "action"


@dataclass(frozen=True)
class Submission:
    """Une saisie (code vide : touche seule). Le code n'apparaît jamais dans sa représentation."""

    code: str = field(repr=False)
    key: str | None = None
    source: str = SOURCE_KEYPAD
    context: dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return f"Submission(key={self.key!r}, source={self.source!r})"

    __str__ = __repr__


@dataclass(frozen=True)
class KeypadStatus:
    """État observé du clavier : None = inconnu."""

    available: bool | None = None
    battery: int | None = None


class KeypadAdapter(ABC):
    """Réception des saisies et retour au clavier."""

    def __init__(
        self,
        on_submission: Callable[[Submission], None],
        on_status: Callable[[KeypadStatus], None],
    ) -> None:
        self.on_submission = on_submission
        self.on_status = on_status
        self.status = KeypadStatus()

    @abstractmethod
    async def async_start(self) -> None:
        """S'abonner aux messages du clavier."""

    @abstractmethod
    async def async_stop(self) -> None:
        """Se désabonner."""

    @abstractmethod
    async def async_feedback(self, submission: Submission, success: bool) -> None:
        """Signaler au clavier le succès ou l'échec d'une saisie, s'il le permet."""

    async def async_warn(self) -> None:
        """Bip d'avertissement avant coupure, s'il le permet (par défaut : rien)."""
