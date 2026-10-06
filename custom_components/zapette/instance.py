"""Opérations sur une instance, partagées par les flux et par le panneau.

Chaque opération qui modifie l'instance fait **une seule** écriture (l'écouteur de mise à jour recharge
l'entrée une fois, sans commande de la prise). Les règles elles‑mêmes vivent dans `tv_settings.py` et
`settings.py` (sans Home Assistant).
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Any
import uuid

from homeassistant.config_entries import ConfigEntry, ConfigSubentry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er

from .codes import async_check_new_code
from .const import (
    CONF_KEYPAD_TOPIC,
    CONF_PARENTS,
    CONF_PLUG_ENTITY,
    CONF_POWER_ENTITY,
    CONF_TV_NAME,
    DOMAIN,
    SUBENTRY_CHILD,
)
from .keypad.mqtt import TopicError, normalize_topic
from .settings import DEFAULT_ICON, Child, SettingsError, WeeklyRules, name_key, normalize_name
from .tv_settings import check_parent_delete, check_parent_name, normalize_tv_name, validate_section

SECTION_IDENTITY = "identity"
SECTION_PLUG = "plug"
SECTION_KEYPAD = "keypad"
DATA_SECTIONS = (SECTION_IDENTITY, SECTION_PLUG, SECTION_KEYPAD)

TEMPLATE_DEFAULT = "default"
TEMPLATE_EMPTY = "empty"
TEMPLATE_COPY = "copy:"


class CodeError(SettingsError):
    """Code refusé (format ou déjà utilisé) : champ `code`."""

    def __init__(self, key: str) -> None:
        super().__init__(key, "code")


def device_name(name: str) -> str:
    return f"Zapette – {name}"


# --- Prise et clavier ----------------------------------------------------------------


def _entity_exists(hass: HomeAssistant, entity_id: str) -> bool:
    return hass.states.get(entity_id) is not None or er.async_get(hass).async_get(entity_id) is not None


def plug_errors(hass: HomeAssistant, user_input: dict[str, Any], entry_id: str | None) -> dict[str, str]:
    """Une prise ne sert qu'à une instance Zapette."""
    plug = user_input[CONF_PLUG_ENTITY]
    for other in hass.config_entries.async_entries(DOMAIN):
        if other.entry_id != entry_id and other.data.get(CONF_PLUG_ENTITY) == plug:
            return {CONF_PLUG_ENTITY: "plug_in_use"}
    return {}


def validate_plug(hass: HomeAssistant, values: dict[str, Any], entry_id: str | None) -> dict[str, Any]:
    """Section `plug` du panneau : prise (interrupteur existant, libre) et capteur facultatif."""
    plug = values.get(CONF_PLUG_ENTITY)
    if not isinstance(plug, str) or not plug.startswith("switch.") or not _entity_exists(hass, plug):
        raise SettingsError("plug_not_found", CONF_PLUG_ENTITY)
    power = values.get(CONF_POWER_ENTITY) or None
    if power is not None and (not isinstance(power, str) or not power.startswith("sensor.") or not _entity_exists(hass, power)):
        raise SettingsError("power_not_found", CONF_POWER_ENTITY)
    if errors := plug_errors(hass, {CONF_PLUG_ENTITY: plug}, entry_id):
        raise SettingsError(errors[CONF_PLUG_ENTITY], CONF_PLUG_ENTITY)
    return plug_data({CONF_PLUG_ENTITY: plug, CONF_POWER_ENTITY: power})


def plug_data(user_input: dict[str, Any]) -> dict[str, Any]:
    data = {CONF_PLUG_ENTITY: user_input[CONF_PLUG_ENTITY]}
    if user_input.get(CONF_POWER_ENTITY):
        data[CONF_POWER_ENTITY] = user_input[CONF_POWER_ENTITY]
    return data


def keypad_in_use(hass: HomeAssistant, topic: str, entry_id: str | None) -> bool:
    """Un clavier ne sert qu'à une instance Zapette."""
    return any(
        other.entry_id != entry_id and other.data.get(CONF_KEYPAD_TOPIC) == topic
        for other in hass.config_entries.async_entries(DOMAIN)
    )


def validate_keypad(hass: HomeAssistant, raw: str | None, entry_id: str | None) -> str | None:
    """Sujet normalisé, ou None (aucun clavier)."""
    raw = (raw or "").strip()
    if not raw:
        return None
    try:
        topic = normalize_topic(raw)
    except TopicError:
        raise SettingsError("keypad_topic_invalid", CONF_KEYPAD_TOPIC) from None
    if keypad_in_use(hass, topic, entry_id):
        raise SettingsError("keypad_in_use", CONF_KEYPAD_TOPIC)
    return topic


# --- Sections ---------------------------------------------------------------------------


def other_tv_names(hass: HomeAssistant, entry_id: str) -> list[str]:
    return [e.title for e in hass.config_entries.async_entries(DOMAIN) if e.entry_id != entry_id]


def async_write_section(hass: HomeAssistant, entry: ConfigEntry, section: str, values: dict[str, Any]) -> None:
    """Valide puis enregistre une section en une seule écriture (les autres clés sont conservées)."""
    if section == SECTION_IDENTITY:
        async_rename_tv(hass, entry, values.get(CONF_TV_NAME, ""))
    elif section == SECTION_PLUG:
        plug = validate_plug(hass, values, entry.entry_id)
        data = {k: v for k, v in entry.data.items() if k not in (CONF_PLUG_ENTITY, CONF_POWER_ENTITY)}
        hass.config_entries.async_update_entry(entry, data={**data, **plug})
    elif section == SECTION_KEYPAD:
        topic = validate_keypad(hass, values.get(CONF_KEYPAD_TOPIC), entry.entry_id)
        data = {k: v for k, v in entry.data.items() if k != CONF_KEYPAD_TOPIC}
        if topic:
            data[CONF_KEYPAD_TOPIC] = topic
        hass.config_entries.async_update_entry(entry, data=data)
    else:
        options = validate_section(section, values)
        hass.config_entries.async_update_entry(entry, options={**entry.options, **options})


def _rename_device(hass: HomeAssistant, entry: ConfigEntry, identifier: str, name: str) -> None:
    """Nom par défaut de l'appareil ; un nom choisi par l'utilisateur (`name_by_user`) reste prioritaire."""
    registry = dr.async_get(hass)
    if device := registry.async_get_device_by_identifier((DOMAIN, identifier), entry.entry_id):
        registry.async_update_device(device.id, name=device_name(name))


def async_rename_tv(hass: HomeAssistant, entry: ConfigEntry, raw: str) -> None:
    if not isinstance(raw, str):
        raise SettingsError("name_invalid", "name")
    name = normalize_tv_name(raw, other_tv_names(hass, entry.entry_id))
    _rename_device(hass, entry, entry.entry_id, name)
    hass.config_entries.async_update_entry(entry, title=name, data={**entry.data, CONF_TV_NAME: name})


# --- Parents ------------------------------------------------------------------------------


def new_parent(name: str, hashed: dict[str, Any]) -> dict[str, Any]:
    return {"id": uuid.uuid4().hex, "name": name, "code": hashed}


def parents_of(entry: ConfigEntry) -> list[dict[str, Any]]:
    return [dict(p) for p in entry.options.get(CONF_PARENTS, [])]


def public_parents(entry: ConfigEntry) -> list[dict[str, str]]:
    """Noms seulement : jamais de code ni d'empreinte."""
    return [{"id": p["id"], "name": p["name"]} for p in entry.options.get(CONF_PARENTS, [])]


async def async_check_parent(
    hass: HomeAssistant,
    entry: ConfigEntry,
    parents: list[dict[str, Any]],
    user_input: dict[str, Any],
    editing: dict[str, Any] | None,
) -> tuple[dict[str, str], str | None, dict[str, Any] | None]:
    """Contrôles d'un parent ajouté ou modifié : (erreurs par champ, nom, empreinte)."""
    errors: dict[str, str] = {}
    name = None
    try:
        name = check_parent_name(str(user_input.get("name", "")), parents, editing["id"] if editing else None)
    except SettingsError as err:
        errors["name"] = err.key
    hashed = editing["code"] if editing else None
    code, confirm = user_input.get("code") or "", user_input.get("code_confirm") or ""
    if code or confirm or not editing:
        error, hashed = await async_check_new_code(
            hass,
            entry,
            {"code": code, "code_confirm": confirm},
            parents=parents,
            exclude_parent=editing["id"] if editing else None,
        )
        if error:
            errors["code"] = error
    return errors, name, hashed


def _raise_first(errors: dict[str, str]) -> None:
    if errors:
        field, key = next(iter(errors.items()))
        raise SettingsError(key, field)


async def async_add_parent(hass: HomeAssistant, entry: ConfigEntry, user_input: dict[str, Any]) -> None:
    parents = parents_of(entry)
    errors, name, hashed = await async_check_parent(hass, entry, parents, user_input, None)
    _raise_first(errors)
    hass.config_entries.async_update_entry(
        entry, options={**entry.options, CONF_PARENTS: [*parents, new_parent(name, hashed)]}
    )


async def async_update_parent(
    hass: HomeAssistant, entry: ConfigEntry, parent_id: str, user_input: dict[str, Any]
) -> None:
    parents = parents_of(entry)
    editing = next((p for p in parents if p["id"] == parent_id), None)
    if editing is None:
        raise SettingsError("not_found", "parent")
    errors, name, hashed = await async_check_parent(hass, entry, parents, user_input, editing)
    _raise_first(errors)
    editing.update(name=name, code=hashed)
    hass.config_entries.async_update_entry(entry, options={**entry.options, CONF_PARENTS: parents})


def async_delete_parent(hass: HomeAssistant, entry: ConfigEntry, parent_id: str) -> None:
    parents = check_parent_delete(parents_of(entry), parent_id)
    hass.config_entries.async_update_entry(entry, options={**entry.options, CONF_PARENTS: parents})


# --- Enfants ------------------------------------------------------------------------------


def children_of(entry: ConfigEntry) -> list[ConfigSubentry]:
    return [sub for sub in entry.subentries.values() if sub.subentry_type == SUBENTRY_CHILD]


def child_name(entry: ConfigEntry, raw: str, exclude: str | None = None) -> str:
    """Prénom normalisé, unique parmi les enfants de la télé (sans casse ni accents)."""
    name = normalize_name(raw)
    others = {name_key(sub.title) for sub in children_of(entry) if sub.subentry_id != exclude}
    if name_key(name) in others:
        raise SettingsError("already_configured", "name")
    return name


def template_rules(entry: ConfigEntry, template: str) -> WeeklyRules:
    """Modèle de règles d'un nouvel enfant : par défaut, vide, ou copie d'un enfant lisible."""
    if template == TEMPLATE_EMPTY:
        return WeeklyRules.empty()
    if template.startswith(TEMPLATE_COPY):
        source = entry.subentries.get(template.removeprefix(TEMPLATE_COPY))
        if source is None or source.subentry_type != SUBENTRY_CHILD:
            raise SettingsError("not_found", "template")
        try:
            return Child.from_dict(dict(source.data)).rules.copy()
        except SettingsError:
            raise SettingsError("invalid_data", "template") from None
    if template != TEMPLATE_DEFAULT:
        raise SettingsError("not_found", "template")
    return WeeklyRules.default()


async def async_create_child(hass: HomeAssistant, entry: ConfigEntry, user_input: dict[str, Any]) -> ConfigSubentry:
    """Mêmes contrôles et même résultat que le flux de sous‑entrée."""
    name = child_name(entry, str(user_input.get("name", "")))
    rules = template_rules(entry, str(user_input.get("template", TEMPLATE_DEFAULT)))
    error, hashed = await async_check_new_code(hass, entry, user_input)
    if error:
        raise CodeError(error)
    child = Child(name, hashed, rules, user_input.get("icon") or DEFAULT_ICON, True)
    subentry = ConfigSubentry(
        data=MappingProxyType(child.to_dict()),
        subentry_type=SUBENTRY_CHILD,
        title=name,
        unique_id=name_key(name),
    )
    hass.config_entries.async_add_subentry(entry, subentry)
    return subentry


def async_rename_child(
    hass: HomeAssistant, entry: ConfigEntry, subentry: ConfigSubentry, raw_name: str, icon: str | None
) -> None:
    """Prénom et icône ; code, règles et activation inchangés ; appareil renommé."""
    try:
        child = Child.from_dict(dict(subentry.data))
    except SettingsError:
        raise SettingsError("invalid_data") from None
    child.name = child_name(entry, raw_name, exclude=subentry.subentry_id)
    child.icon = icon or DEFAULT_ICON
    _rename_device(hass, entry, subentry.subentry_id, child.name)
    hass.config_entries.async_update_subentry(
        entry, subentry, title=child.name, unique_id=name_key(child.name), data=child.to_dict()
    )


def async_delete_child(hass: HomeAssistant, entry: ConfigEntry, subentry: ConfigSubentry) -> None:
    """Appareil et entités rattachés retirés par Home Assistant ; l'historique est conservé."""
    hass.config_entries.async_remove_subentry(entry, subentry.subentry_id)
