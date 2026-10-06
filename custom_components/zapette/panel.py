"""Panneau « Zapette » dans la barre latérale (administrateurs)."""

from __future__ import annotations

import hashlib
from pathlib import Path

from homeassistant.components import frontend, panel_custom
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN

PANEL_URL_PATH = DOMAIN
WEBCOMPONENT = "zapette-panel"
STATIC_URL = f"/{DOMAIN}_static"
FRONTEND_DIR = Path(__file__).parent / "frontend"
ENTRYPOINT = "zapette-panel.js"
DATA_STATIC_REGISTERED = f"{DOMAIN}_static_registered"


def _bundle_version() -> str:
    """Empreinte du bundle, pour invalider le cache du navigateur à chaque build."""
    return hashlib.sha256((FRONTEND_DIR / ENTRYPOINT).read_bytes()).hexdigest()[:12]


async def async_register_panel(hass: HomeAssistant) -> None:
    if frontend.async_panel_exists(hass, PANEL_URL_PATH):
        return
    if not hass.data.get(DATA_STATIC_REGISTERED):
        await hass.http.async_register_static_paths(
            [StaticPathConfig(STATIC_URL, str(FRONTEND_DIR), cache_headers=False)]
        )
        hass.data[DATA_STATIC_REGISTERED] = True
    version = await hass.async_add_executor_job(_bundle_version)
    await panel_custom.async_register_panel(
        hass,
        frontend_url_path=PANEL_URL_PATH,
        webcomponent_name=WEBCOMPONENT,
        sidebar_title="Zapette",
        sidebar_icon="mdi:television-classic",
        module_url=f"{STATIC_URL}/{ENTRYPOINT}?v={version}",
        require_admin=True,
        config={},
    )


@callback
def async_unregister_panel(hass: HomeAssistant) -> None:
    frontend.async_remove_panel(hass, PANEL_URL_PATH, warn_if_unknown=False)
