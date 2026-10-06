"""Commandes WebSocket de l'onglet Réglages et de la gestion des enfants (administrateurs).

Aucune réponse, aucune erreur, aucun journal ne contient de code ni d'empreinte. Chaque écriture passe
par `instance.py` : une seule écriture, un seul rechargement, aucune commande de la prise.
"""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr, entity_registry as er

from . import instance
from .api import _child_payload, _get_child, _get_entry
from .colors import child_colors
from .const import (
    CONF_KEYPAD_TOPIC,
    CONF_PLUG_ENTITY,
    CONF_POWER_ENTITY,
    CONF_TV_NAME,
    DOMAIN,
    KEYPAD_TEST_TIMEOUT,
)
from .keypad.mqtt import TopicError, _tests, async_discover_keypads, async_wait_for_key, mqtt_ready, normalize_topic
from .settings import SettingsError
from .tv_settings import SECTIONS, schema_payload, section_values

ERR_TEST_IN_PROGRESS = "test_in_progress"

# Entités de l'état de maintenance : clé → (plateforme, ce dont elles dépendent).
STATUS_ENTITIES = {
    "control_active": ("switch", CONF_PLUG_ENTITY),
    "plug_reachable": ("binary_sensor", CONF_PLUG_ENTITY),
    "plug_problem": ("binary_sensor", CONF_PLUG_ENTITY),
    "last_outage": ("sensor", CONF_PLUG_ENTITY),
    "keypad_available": ("binary_sensor", CONF_KEYPAD_TOPIC),
    "keypad_battery": ("sensor", CONF_KEYPAD_TOPIC),
    "keypad_locked": ("binary_sensor", CONF_KEYPAD_TOPIC),
}


@callback
def async_register(hass: HomeAssistant) -> None:
    for command in (
        ws_settings,
        ws_settings_update,
        ws_parent_add,
        ws_parent_update,
        ws_parent_delete,
        ws_keypad_candidates,
        ws_keypad_test,
        ws_child_create,
        ws_child_rename,
        ws_child_delete,
    ):
        websocket_api.async_register_command(hass, command)


def _status(hass: HomeAssistant, entry: ConfigEntry) -> dict[str, Any]:
    registry = er.async_get(hass)
    device = dr.async_get(hass).async_get_device_by_identifier((DOMAIN, entry.entry_id), entry.entry_id)
    entities = {
        key: registry.async_get_entity_id(platform, DOMAIN, f"{entry.entry_id}_{key}") if entry.data.get(needs) else None
        for key, (platform, needs) in STATUS_ENTITIES.items()
    }
    return {
        "loaded": entry.state is ConfigEntryState.LOADED,
        "device_id": device.id if device else None,
        "entities": entities,
    }


def settings_payload(hass: HomeAssistant, entry: ConfigEntry) -> dict[str, Any]:
    values: dict[str, Any] = {
        instance.SECTION_IDENTITY: {CONF_TV_NAME: entry.data.get(CONF_TV_NAME, entry.title)},
        instance.SECTION_PLUG: {
            CONF_PLUG_ENTITY: entry.data.get(CONF_PLUG_ENTITY),
            CONF_POWER_ENTITY: entry.data.get(CONF_POWER_ENTITY),
        },
        instance.SECTION_KEYPAD: {CONF_KEYPAD_TOPIC: entry.data.get(CONF_KEYPAD_TOPIC)},
    }
    values.update({section: section_values(section, dict(entry.options)) for section in SECTIONS})
    return {
        "entry_id": entry.entry_id,
        "title": entry.title,
        "values": values,
        "schema": schema_payload(),
        "parents": instance.public_parents(entry),
        "status": _status(hass, entry),
    }


def _send_settings_error(connection: websocket_api.ActiveConnection, msg_id: int, err: SettingsError) -> None:
    connection.send_error(msg_id, err.key, err.field)


@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required("type"): "zapette/settings", vol.Required("entry_id"): str})
@callback
def ws_settings(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    if (entry := _get_entry(hass, connection, msg)) is None:
        return
    connection.send_result(msg["id"], settings_payload(hass, entry))


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): "zapette/settings/update",
        vol.Required("entry_id"): str,
        vol.Required("section"): str,
        vol.Required("values"): dict,
    }
)
@callback
def ws_settings_update(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Une section à la fois, en une seule écriture."""
    if (entry := _get_entry(hass, connection, msg)) is None:
        return
    try:
        instance.async_write_section(hass, entry, msg["section"], msg["values"])
    except SettingsError as err:
        _send_settings_error(connection, msg["id"], err)
        return
    connection.send_result(msg["id"], settings_payload(hass, entry))


# --- Parents -------------------------------------------------------------------------------

CODE_FIELDS = {vol.Optional("code", default=""): str, vol.Optional("code_confirm", default=""): str}


def _parents_result(connection: websocket_api.ActiveConnection, msg_id: int, entry: ConfigEntry) -> None:
    connection.send_result(msg_id, {"parents": instance.public_parents(entry)})


@websocket_api.require_admin
@websocket_api.websocket_command(
    {vol.Required("type"): "zapette/parent/add", vol.Required("entry_id"): str, vol.Required("name"): str, **CODE_FIELDS}
)
@websocket_api.async_response
async def ws_parent_add(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    if (entry := _get_entry(hass, connection, msg)) is None:
        return
    try:
        await instance.async_add_parent(hass, entry, msg)
    except SettingsError as err:
        _send_settings_error(connection, msg["id"], err)
        return
    _parents_result(connection, msg["id"], entry)


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): "zapette/parent/update",
        vol.Required("entry_id"): str,
        vol.Required("parent_id"): str,
        vol.Required("name"): str,
        **CODE_FIELDS,
    }
)
@websocket_api.async_response
async def ws_parent_update(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Code et confirmation vides : code inchangé."""
    if (entry := _get_entry(hass, connection, msg)) is None:
        return
    try:
        await instance.async_update_parent(hass, entry, msg["parent_id"], msg)
    except SettingsError as err:
        _send_settings_error(connection, msg["id"], err)
        return
    _parents_result(connection, msg["id"], entry)


@websocket_api.require_admin
@websocket_api.websocket_command(
    {vol.Required("type"): "zapette/parent/delete", vol.Required("entry_id"): str, vol.Required("parent_id"): str}
)
@callback
def ws_parent_delete(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    if (entry := _get_entry(hass, connection, msg)) is None:
        return
    try:
        instance.async_delete_parent(hass, entry, msg["parent_id"])
    except SettingsError as err:
        _send_settings_error(connection, msg["id"], err)
        return
    _parents_result(connection, msg["id"], entry)


# --- Clavier --------------------------------------------------------------------------------


@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required("type"): "zapette/keypad/candidates", vol.Required("entry_id"): str})
@websocket_api.async_response
async def ws_keypad_candidates(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Claviers Zigbee2MQTT qui envoient des codes (découverte bornée, vide sans MQTT)."""
    if _get_entry(hass, connection, msg) is None:
        return
    ready = mqtt_ready(hass)
    found = await async_discover_keypads(hass) if ready else {}
    connection.send_result(
        msg["id"],
        {
            "mqtt": ready,
            "keypads": [
                {"topic": f"zigbee2mqtt/{name}", "label": f"{name} — {label}" if label else name}
                for name, label in found.items()
            ],
        },
    )


@websocket_api.require_admin
@websocket_api.websocket_command(
    {vol.Required("type"): "zapette/keypad/test", vol.Required("entry_id"): str, vol.Required("topic"): str}
)
@callback
def ws_keypad_test(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Test de saisie par abonnement : un seul événement (touche, rien reçu, MQTT indisponible).

    Seule la touche remonte ; pendant le test, l'instance qui utilise ce clavier ignore ses saisies.
    Le désabonnement (ou la fermeture de la connexion) annule le test.
    """
    if _get_entry(hass, connection, msg) is None:
        return
    try:
        topic = normalize_topic(msg["topic"])
    except TopicError:
        connection.send_error(msg["id"], "keypad_topic_invalid", CONF_KEYPAD_TOPIC)
        return
    tests = _tests(hass)
    if topic in tests:
        connection.send_error(msg["id"], ERR_TEST_IN_PROGRESS, CONF_KEYPAD_TOPIC)
        return
    tests.add(topic)  # réservé dès maintenant : un second test sur ce sujet est refusé

    async def run() -> None:
        try:
            if not mqtt_ready(hass):
                event: dict[str, Any] = {"status": "no_mqtt"}
            else:
                try:
                    key = await async_wait_for_key(hass, topic, KEYPAD_TEST_TIMEOUT)
                    event = {"status": "key", "key": key or "—"}
                except TimeoutError:
                    event = {"status": "timeout", "seconds": KEYPAD_TEST_TIMEOUT}
            connection.subscriptions.pop(msg["id"], None)
            connection.send_message(websocket_api.event_message(msg["id"], event))
        finally:
            tests.discard(topic)

    # Réponse d'abord : sans MQTT, la tâche (démarrée tout de suite) envoie aussitôt son événement.
    connection.send_result(msg["id"])
    task = hass.async_create_background_task(run(), f"zapette keypad test {topic}")

    @callback
    def cancel() -> None:
        task.cancel()
        tests.discard(topic)  # au cas où la tâche serait annulée avant d'avoir démarré

    if not task.done():
        connection.subscriptions[msg["id"]] = cancel


# --- Enfants --------------------------------------------------------------------------------


def _child_result(connection: websocket_api.ActiveConnection, msg_id: int, entry: ConfigEntry, subentry_id: str) -> None:
    colors = child_colors(sub.subentry_id for sub in instance.children_of(entry))
    connection.send_result(msg_id, _child_payload(entry.subentries[subentry_id], colors[subentry_id]))


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): "zapette/child/create",
        vol.Required("entry_id"): str,
        vol.Required("name"): str,
        vol.Optional("icon"): vol.Any(str, None),
        vol.Required("code"): str,
        vol.Required("code_confirm"): str,
        vol.Optional("template", default=instance.TEMPLATE_DEFAULT): str,
    }
)
@websocket_api.async_response
async def ws_child_create(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Mêmes contrôles et même résultat que « Ajouter un enfant » des intégrations."""
    if (entry := _get_entry(hass, connection, msg)) is None:
        return
    try:
        subentry = await instance.async_create_child(hass, entry, msg)
    except SettingsError as err:
        _send_settings_error(connection, msg["id"], err)
        return
    _child_result(connection, msg["id"], entry, subentry.subentry_id)


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): "zapette/child/rename",
        vol.Required("entry_id"): str,
        vol.Required("subentry_id"): str,
        vol.Required("name"): str,
        vol.Optional("icon"): vol.Any(str, None),
    }
)
@callback
def ws_child_rename(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Prénom et icône ; code, règles, temps consommé et session en cours conservés."""
    if (found := _get_child(hass, connection, msg)) is None:
        return
    entry, subentry = found
    try:
        instance.async_rename_child(hass, entry, subentry, msg["name"], msg.get("icon"))
    except SettingsError as err:
        _send_settings_error(connection, msg["id"], err)
        return
    _child_result(connection, msg["id"], entry, subentry.subentry_id)


@websocket_api.require_admin
@websocket_api.websocket_command(
    {vol.Required("type"): "zapette/child/delete", vol.Required("entry_id"): str, vol.Required("subentry_id"): str}
)
@callback
def ws_child_delete(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Enfant, appareil et entités retirés ; historique conservé ; une session en cours se termine."""
    if (found := _get_child(hass, connection, msg)) is None:
        return
    entry, subentry = found
    instance.async_delete_child(hass, entry, subentry)
    connection.send_result(msg["id"])
