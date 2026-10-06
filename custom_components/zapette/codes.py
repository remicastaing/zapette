"""Contrôle d'un nouveau code (format + unicité) pour les flux et l'API du panneau."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_PARENTS, SUBENTRY_CHILD
from .security import code_in_use, hash_code, validate_code


async def async_check_new_code(
    hass: HomeAssistant,
    entry: ConfigEntry | None,
    user_input: dict[str, Any],
    *,
    parents: list[dict[str, Any]] | None = None,
    exclude_child: str | None = None,
    exclude_parent: str | None = None,
) -> tuple[str | None, dict[str, Any] | None]:
    """Valide un code saisi ; renvoie (erreur, empreinte).

    `parents` remplace les codes parents enregistrés (brouillon du flux d'options).
    """
    error, code = validate_code(user_input["code"], user_input["code_confirm"])
    if error:
        return error, None
    if entry is not None:
        if parents is None:
            parents = entry.options.get(CONF_PARENTS, [])
        hashes = [parent["code"] for parent in parents if parent["id"] != exclude_parent]
        hashes += [
            sub.data["code"]
            for sid, sub in entry.subentries.items()
            if sub.subentry_type == SUBENTRY_CHILD and sid != exclude_child and "code" in sub.data
        ]
        if await hass.async_add_executor_job(code_in_use, code, hashes):
            return "code_in_use", None
    return None, await hass.async_add_executor_job(hash_code, code)
