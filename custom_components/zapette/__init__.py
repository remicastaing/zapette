"""Zapette : contrôle de l'accès des enfants à la télévision."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, issue_registry as ir
from homeassistant.helpers.storage import Store
from homeassistant.helpers.typing import ConfigType

from .api import async_register_commands
from .access import ISSUE_BATTERY, ISSUE_UNREACHABLE, AccessManager, ZapetteRuntime
from .const import CONF_PLUG_ENTITY, CONF_TV_NAME, DOMAIN
from .coordinator import DATA_LOGIC, ISSUE_STANDBY_CUT, STORAGE_VERSION, EntryState, PlugCoordinator
from .history_recorder import DATA_HISTORY, HistoryRecorder, history_store
from .session_coordinator import DATA_SESSIONS, SessionCoordinator
from .panel import async_register_panel, async_unregister_panel
from .services import async_register_services

PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.BUTTON, Platform.SENSOR, Platform.SWITCH]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

type ZapetteConfigEntry = ConfigEntry[ZapetteRuntime]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    async_register_commands(hass)
    async_register_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ZapetteConfigEntry) -> bool:
    await async_register_panel(hass)
    state = await EntryState.async_load(hass, entry.entry_id)
    coordinator = None
    missing_issue = f"plug_missing_{entry.entry_id}"
    if entry.data.get(CONF_PLUG_ENTITY):
        coordinator = await PlugCoordinator.async_create(hass, entry, state)
        ir.async_delete_issue(hass, DOMAIN, missing_issue)
    else:
        ir.async_create_issue(
            hass,
            DOMAIN,
            missing_issue,
            is_fixable=False,
            severity=ir.IssueSeverity.WARNING,
            translation_key="plug_missing",
            translation_placeholders={"tv_name": entry.data.get(CONF_TV_NAME, entry.title)},
        )
    # L'historique est prêt avant les sessions : il reçoit la fin `restart` émise au démarrage.
    history = await HistoryRecorder.async_create(hass, entry, state)
    sessions = SessionCoordinator.create(hass, entry, state, coordinator)
    sessions.history = history
    access = AccessManager(hass, entry, state, coordinator, sessions, history)
    history.async_attach(coordinator, sessions)
    entry.runtime_data = ZapetteRuntime(coordinator, access, sessions, history)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    if coordinator:
        await coordinator.async_start()
    await sessions.async_start()
    await access.async_start()
    entry.async_on_unload(entry.add_update_listener(_async_reload))
    return True


DATA_RELOADING = "reloading"


async def _async_reload(hass: HomeAssistant, entry: ZapetteConfigEntry) -> None:
    """Enfant, prise ou réglage modifié : rechargement (sans commande de la prise).

    Le panneau reste enregistré pendant ce rechargement : sinon, avec une seule télévision, il
    disparaîtrait un instant et Home Assistant renverrait le parent qui vient d'enregistrer vers
    l'accueil.
    """
    reloading = hass.data.setdefault(DOMAIN, {}).setdefault(DATA_RELOADING, set())
    reloading.add(entry.entry_id)
    try:
        await hass.config_entries.async_reload(entry.entry_id)
    finally:
        reloading.discard(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ZapetteConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        runtime = entry.runtime_data
        await runtime.access.async_unload()
        await runtime.sessions.async_unload()
        if runtime.plug:
            await runtime.plug.async_unload()
        await runtime.history.async_unload()
        await runtime.access.state.async_flush()
    reloading = entry.entry_id in hass.data.get(DOMAIN, {}).get(DATA_RELOADING, ())
    others = [e for e in hass.config_entries.async_loaded_entries(DOMAIN) if e.entry_id != entry.entry_id]
    if unloaded and not reloading and not others:
        async_unregister_panel(hass)
    return unloaded


async def async_remove_entry(hass: HomeAssistant, entry: ZapetteConfigEntry) -> None:
    """Instance supprimée : la prise n'est pas commandée ; état et réparations effacés."""
    hass.data.get(DOMAIN, {}).get(DATA_LOGIC, {}).pop(entry.entry_id, None)
    hass.data.get(DOMAIN, {}).get(DATA_SESSIONS, {}).pop(entry.entry_id, None)
    hass.data.get(DOMAIN, {}).get(DATA_HISTORY, {}).pop(entry.entry_id, None)
    await Store(hass, STORAGE_VERSION, f"{DOMAIN}.{entry.entry_id}").async_remove()
    await history_store(hass, entry.entry_id).async_remove()
    for key in ("unreachable", "off_failed", "missing"):
        ir.async_delete_issue(hass, DOMAIN, f"plug_{key}_{entry.entry_id}")
    ir.async_delete_issue(hass, DOMAIN, f"{ISSUE_STANDBY_CUT}_{entry.entry_id}")
    for key in (ISSUE_UNREACHABLE, ISSUE_BATTERY):
        ir.async_delete_issue(hass, DOMAIN, f"{key}_{entry.entry_id}")
