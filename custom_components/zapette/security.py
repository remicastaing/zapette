"""Codes : validation, hachage et vérification.

Ce module n'importe rien de Home Assistant.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from typing import Any

ALGO = "pbkdf2_sha256"
ITERATIONS = 20_000
SALT_BYTES = 16
MIN_LENGTH = 4
MAX_LENGTH = 8


def _b64(raw: bytes) -> str:
    return "b64:" + base64.b64encode(raw).decode()


def _unb64(text: str) -> bytes:
    return base64.b64decode(text.removeprefix("b64:"))


def is_trivial_code(code: str) -> bool:
    """Chiffres tous identiques ou suite croissante/décroissante de pas 1."""
    steps = {int(b) - int(a) for a, b in zip(code, code[1:])}
    return steps in ({0}, {1}, {-1})


def validate_code(code: str, confirmation: str) -> tuple[str | None, str]:
    """Retourne (clé d'erreur ou None, code normalisé)."""
    code = code.strip()
    if not code.isascii() or not code.isdigit():
        return "code_not_digits", code
    if not MIN_LENGTH <= len(code) <= MAX_LENGTH:
        return "code_length", code
    if code != confirmation.strip():
        return "code_mismatch", code
    if is_trivial_code(code):
        return "code_too_simple", code
    return None, code


def hash_code(code: str, iterations: int = ITERATIONS) -> dict[str, Any]:
    salt = secrets.token_bytes(SALT_BYTES)
    digest = hashlib.pbkdf2_hmac("sha256", code.encode(), salt, iterations)
    return {"algo": ALGO, "iterations": iterations, "salt": _b64(salt), "hash": _b64(digest)}


def verify_code(code: str, hashed: dict[str, Any]) -> bool:
    if hashed.get("algo") != ALGO:
        return False
    digest = hashlib.pbkdf2_hmac(
        "sha256", code.encode(), _unb64(hashed["salt"]), int(hashed["iterations"])
    )
    return hmac.compare_digest(digest, _unb64(hashed["hash"]))


def code_in_use(code: str, hashes: list[dict[str, Any]]) -> bool:
    """Le code correspond‑il à l'une des empreintes ? (tester toutes, sans court‑circuit)"""
    matches = [verify_code(code, hashed) for hashed in hashes]
    return any(matches)


MAX_INPUT = 16  # au‑delà, une saisie ne peut correspondre à aucun code : coût borné


def match_code(code: str, candidates: list[tuple[str, dict[str, Any]]]) -> str | None:
    """Identifiant du profil dont l'empreinte correspond au code, ou None.

    Toutes les empreintes sont calculées et comparées, dans l'ordre donné et sans arrêt anticipé :
    la durée ne dépend pas du profil reconnu.
    """
    code = code[:MAX_INPUT]
    found: str | None = None
    for profile_id, hashed in candidates:
        try:
            matched = verify_code(code, hashed)
        except (KeyError, TypeError, ValueError):
            matched = False
        if matched and found is None:
            found = profile_id
    return found
