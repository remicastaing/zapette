"""Flux de configuration de Zapette : instance, codes parents, enfants."""

from __future__ import annotations

import asyncio
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    SOURCE_RECONFIGURE,
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    ConfigSubentryFlow,
    OptionsFlow,
    SubentryFlowResult,
)
from homeassistant.core import callback
from homeassistant.helpers.selector import TextSelector

from .const import (
    CONF_KEYPAD_TOPIC,
    CONF_PARENTS,
    CONF_PLUG_ENTITY,
    CONF_POWER_ENTITY,
    CONF_TV_NAME,
    DOMAIN,
    KEYPAD_TEST_TIMEOUT,
    SUBENTRY_CHILD,
)
from .flow_helpers import (
    PASSWORD,
    plug_schema,
    plug_settings_schema,
    session_settings_schema,
    code_schema,
    day_names,
    parent_schema,
    parent_select_schema,
    copy_schema,
    days_schema,
    identity_schema,
    keypad_schema,
    keypad_settings_schema,
    quota_schema,
    render_summary,
    slots_schema,
    template_schema,
)
from .codes import async_check_new_code
from .instance import (
    async_check_parent,
    child_name,
    new_parent,
    plug_data,
    template_rules,
    validate_keypad,
    validate_plug,
)
from .keypad.mqtt import async_discover_keypads, async_wait_for_key, mqtt_ready
from .settings import (
    DEFAULT_ICON,
    MAX_SLOTS,
    Child,
    SettingsError,
    WeeklyRules,
    expand_days,
    name_key,
    normalize_name,
    normalize_slots,
    validate_quota,
)
from .tv_settings import (
    SECTION_KEYPAD_GUARD,
    SECTION_PLUG_BEHAVIOR,
    SECTION_SESSIONS,
    check_parent_delete,
    validate_section,
)


class MqttUnavailable(Exception):
    """MQTT n'est pas configuré ou pas connecté."""


class ZapetteConfigFlow(ConfigFlow, domain=DOMAIN):
    """Création d'une instance Zapette (une télévision)."""

    VERSION = 1

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}
        self._options: dict[str, Any] = {}
        self._keypads: dict[str, str] = {}
        self._test_task: asyncio.Task[str] | None = None
        self._test_key = ""

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> ParentsOptionsFlow:
        return ParentsOptionsFlow()

    @classmethod
    @callback
    def async_get_supported_subentry_types(cls, config_entry: ConfigEntry) -> dict[str, type[ConfigSubentryFlow]]:
        return {SUBENTRY_CHILD: ChildSubentryFlow}

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                parent_name = normalize_name(user_input["parent_name"])
            except SettingsError:
                errors["parent_name"] = "name_invalid"
            error, hashed = await async_check_new_code(self.hass, None, user_input)
            if error:
                errors["code"] = error
            if not errors:
                self._data = {CONF_TV_NAME: user_input[CONF_TV_NAME]}
                self._options = {CONF_PARENTS: [new_parent(parent_name, hashed)]}
                return await self.async_step_plug()
        schema = vol.Schema(
            {
                vol.Required(CONF_TV_NAME): TextSelector(),
                vol.Required("parent_name"): TextSelector(),
                vol.Required("code"): PASSWORD,
                vol.Required("code_confirm"): PASSWORD,
            }
        )
        return self.async_show_form(
            step_id="user", data_schema=self.add_suggested_values_to_schema(schema, user_input), errors=errors
        )


    async def async_step_plug(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Prise de la télé et capteur de puissance facultatif."""
        errors: dict[str, str] = {}
        if user_input is not None:
            errors = plug_errors(self.hass, user_input, None)
            if not errors:
                self._data.update(plug_data(user_input))
                return await self.async_step_keypad()
        return self.async_show_form(
            step_id="plug", data_schema=self.add_suggested_values_to_schema(plug_schema(), user_input), errors=errors
        )

    # --- clavier (création et reconfiguration) ------------------------------------

    @property
    def _reconfiguring(self) -> bool:
        return self.source == SOURCE_RECONFIGURE

    async def async_step_keypad(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Clavier Zigbee2MQTT (facultatif), désigné par son sujet."""
        errors: dict[str, str] = {}
        if user_input is not None:
            entry_id = self._get_reconfigure_entry().entry_id if self._reconfiguring else None
            try:
                topic = validate_keypad(self.hass, user_input.get(CONF_KEYPAD_TOPIC), entry_id)
            except SettingsError as err:
                errors[err.field] = err.key
            else:
                if topic is None:
                    self._data.pop(CONF_KEYPAD_TOPIC, None)
                    return await self.async_step_keypad_finish()
                self._data[CONF_KEYPAD_TOPIC] = topic
                if user_input.get("test_keypad"):
                    return await self.async_step_keypad_test()
                return await self.async_step_keypad_finish()
        else:
            found = await async_discover_keypads(self.hass)
            self._keypads = {f"zigbee2mqtt/{name}": f"{name} — {label}" if label else name for name, label in found.items()}
        suggested = user_input or ({CONF_KEYPAD_TOPIC: self._data[CONF_KEYPAD_TOPIC]} if self._data.get(CONF_KEYPAD_TOPIC) else None)
        return self.async_show_form(
            step_id="keypad",
            data_schema=self.add_suggested_values_to_schema(keypad_schema(self._keypads), suggested),
            errors=errors,
        )

    async def async_step_keypad_test(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Test de saisie : seule la touche est remontée ; le code n'est ni évalué ni conservé."""
        topic = self._data[CONF_KEYPAD_TOPIC]
        if self._test_task is None:
            self._test_task = self.hass.async_create_task(self._async_test(topic))
        if not self._test_task.done():
            return self.async_show_progress(
                step_id="keypad_test",
                progress_action="keypad_test",
                progress_task=self._test_task,
                description_placeholders={"topic": topic, "seconds": str(KEYPAD_TEST_TIMEOUT)},
            )
        task, self._test_task = self._test_task, None
        try:
            self._test_key = task.result() or "—"
            next_step = "keypad_test_ok"
        except TimeoutError:
            next_step = "keypad_test_timeout"
        except MqttUnavailable:
            next_step = "keypad_test_no_mqtt"
        return self.async_show_progress_done(next_step_id=next_step)

    async def _async_test(self, topic: str) -> str:
        if not mqtt_ready(self.hass):
            raise MqttUnavailable
        return await async_wait_for_key(self.hass, topic, KEYPAD_TEST_TIMEOUT)

    async def async_step_keypad_test_ok(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        return self.async_show_menu(
            step_id="keypad_test_ok",
            menu_options=["keypad_finish", "keypad_test", "keypad"],
            description_placeholders={"key": self._test_key, "topic": self._data[CONF_KEYPAD_TOPIC]},
        )

    async def async_step_keypad_test_timeout(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        return self.async_show_menu(
            step_id="keypad_test_timeout",
            menu_options=["keypad_test", "keypad_finish", "keypad"],
            description_placeholders={"topic": self._data[CONF_KEYPAD_TOPIC], "seconds": str(KEYPAD_TEST_TIMEOUT)},
        )

    async def async_step_keypad_test_no_mqtt(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        return self.async_show_menu(step_id="keypad_test_no_mqtt", menu_options=["keypad_test", "keypad_finish", "keypad"])

    async def async_step_keypad_finish(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if self._reconfiguring:
            # L'écouteur de mise à jour recharge l'entrée (sans commande de la prise).
            return self.async_update_and_abort(self._get_reconfigure_entry(), data=self._data)
        return self.async_create_entry(title=self._data[CONF_TV_NAME], data=self._data, options=self._options)

    @callback
    def async_remove(self) -> None:
        if self._test_task and not self._test_task.done():
            self._test_task.cancel()

    # --- reconfiguration ------------------------------------------------------------

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Menu : prise ou clavier. Les enfants, codes et réglages sont conservés."""
        entry = self._get_reconfigure_entry()
        self._data = dict(entry.data)
        return self.async_show_menu(
            step_id="reconfigure",
            menu_options=["reconfigure_plug", "keypad"],
            description_placeholders={"tv_name": entry.title},
        )

    async def async_step_reconfigure_plug(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Changer de prise ou de capteur."""
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}
        if user_input is not None:
            errors = plug_errors(self.hass, user_input, entry.entry_id)
            if not errors:
                data = {key: value for key, value in entry.data.items() if key not in (CONF_PLUG_ENTITY, CONF_POWER_ENTITY)}
                # L'écouteur de mise à jour recharge l'entrée.
                return self.async_update_and_abort(entry, data={**data, **plug_data(user_input)})
        suggested = user_input or {key: entry.data[key] for key in (CONF_PLUG_ENTITY, CONF_POWER_ENTITY) if entry.data.get(key)}
        return self.async_show_form(
            step_id="reconfigure_plug",
            data_schema=self.add_suggested_values_to_schema(plug_schema(), suggested),
            errors=errors,
            description_placeholders={"tv_name": entry.title},
        )


def plug_errors(hass: Any, user_input: dict[str, Any], entry_id: str | None) -> dict[str, str]:
    """Contrôles partagés avec le panneau (prise existante et libre, capteur existant)."""
    try:
        validate_plug(hass, user_input, entry_id)
    except SettingsError as err:
        return {err.field: err.key}
    return {}


class ParentsOptionsFlow(OptionsFlow):
    """« Configurer » : gestion des codes parents (brouillon enregistré en une fois)."""

    def __init__(self) -> None:
        self._parents: list[dict[str, Any]] | None = None
        self._editing: str | None = None
        self._plug_settings: dict[str, Any] = {}
        self._keypad_settings: dict[str, Any] = {}
        self._session_settings: dict[str, Any] = {}

    @property
    def _draft(self) -> list[dict[str, Any]]:
        if self._parents is None:
            self._parents = [dict(p) for p in self.config_entry.options.get(CONF_PARENTS, [])]
        return self._parents

    def _choices(self) -> dict[str, str]:
        return {parent["id"]: parent["name"] for parent in self._draft}

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        return self.async_show_menu(
            step_id="init",
            menu_options=["add_parent", "edit_parent", "delete_parent", "plug_settings", "keypad_settings", "session_settings", "save"],
            description_placeholders={"parents": ", ".join(self._choices().values()) or "—"},
        )

    async def async_step_add_parent(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        self._editing = None
        return await self.async_step_parent()

    async def async_step_edit_parent(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            self._editing = user_input["parent"]
            return await self.async_step_parent()
        return self.async_show_form(step_id="edit_parent", data_schema=parent_select_schema(self._choices()))

    async def async_step_parent(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Formulaire commun ajout/modification."""
        editing = next((p for p in self._draft if p["id"] == self._editing), None)
        errors: dict[str, str] = {}
        if user_input is not None:
            errors, name, hashed = await async_check_parent(
                self.hass, self.config_entry, self._draft, user_input, editing
            )

            if not errors:
                if editing:
                    editing.update(name=name, code=hashed)
                else:
                    self._draft.append(new_parent(name, hashed))
                return await self.async_step_init()

        suggested = {"name": user_input["name"]} if user_input else {"name": editing["name"]} if editing else None
        return self.async_show_form(
            step_id="parent",
            data_schema=self.add_suggested_values_to_schema(parent_schema(code_required=editing is None), suggested),
            errors=errors,
        )

    async def async_step_delete_parent(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                self._parents = check_parent_delete(self._draft, user_input["parent"])
            except SettingsError as err:
                errors[err.field] = err.key
            else:
                return await self.async_step_init()
        return self.async_show_form(
            step_id="delete_parent", data_schema=parent_select_schema(self._choices()), errors=errors
        )

    async def async_step_plug_settings(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Tolérance de l'allumage manuel et détection de veille (brouillon)."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                self._plug_settings = validate_section(SECTION_PLUG_BEHAVIOR, user_input)
            except SettingsError as err:
                errors[err.field] = err.key
            else:
                return await self.async_step_init()
        current = {**self.config_entry.options, **self._plug_settings, **(user_input or {})}
        return self.async_show_form(step_id="plug_settings", data_schema=plug_settings_schema(current), errors=errors)

    async def async_step_keypad_settings(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Clavier : anti‑essais (échecs, fenêtre, durée) et touche d'arrêt (brouillon)."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                self._keypad_settings = validate_section(SECTION_KEYPAD_GUARD, user_input)
            except SettingsError as err:
                errors[err.field] = err.key
            else:
                return await self.async_step_init()
        current = {**self.config_entry.options, **self._keypad_settings, **(user_input or {})}
        return self.async_show_form(step_id="keypad_settings", data_schema=keypad_settings_schema(current), errors=errors)

    async def async_step_session_settings(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Sessions : avertissement avant coupure, bip, durée maximale d'une session parent (brouillon)."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                self._session_settings = validate_section(SECTION_SESSIONS, user_input)
            except SettingsError as err:
                errors[err.field] = err.key
            else:
                return await self.async_step_init()
        current = {**self.config_entry.options, **self._session_settings, **(user_input or {})}
        return self.async_show_form(step_id="session_settings", data_schema=session_settings_schema(current), errors=errors)

    async def async_step_save(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        return self.async_create_entry(
            data={
                **self.config_entry.options,
                **self._plug_settings,
                **self._keypad_settings,
                **self._session_settings,
                CONF_PARENTS: self._draft,
            }
        )


class ChildSubentryFlow(ConfigSubentryFlow):
    """Ajout (user) et reconfiguration (menu) d'un enfant."""

    def __init__(self) -> None:
        self._name = ""
        self._icon = DEFAULT_ICON
        self._enabled = True
        self._code: dict[str, Any] | None = None
        self._rules = WeeklyRules.default()
        self._days: list[str] = []

    # --- utilitaires ---------------------------------------------------------

    @property
    def _reconfiguring(self) -> bool:
        return self.source == SOURCE_RECONFIGURE

    @property
    def _self_id(self) -> str | None:
        return self._reconfigure_subentry_id if self._reconfiguring else None

    def _draft(self) -> Child:
        return Child(self._name, self._code or {}, self._rules, self._icon, self._enabled)

    def _summary(self) -> dict[str, str]:
        return {"name": self._name, "summary": render_summary(self._draft(), self.hass.config.language)}

    def _other_children(self) -> dict[str, str]:
        return {
            sid: sub.title
            for sid, sub in self._get_entry().subentries.items()
            if sub.subentry_type == SUBENTRY_CHILD and sid != self._self_id
        }

    def _after_edit(self) -> SubentryFlowResult:
        return self._show_menu()

    async def async_step_menu(self, user_input: dict[str, Any] | None = None) -> SubentryFlowResult:
        return self._show_menu()

    def _show_menu(self) -> SubentryFlowResult:
        return self.async_show_menu(
            step_id="menu",
            menu_options=["identity", "code", "quota_days", "slot_days", "copy", "save"],
            description_placeholders=self._summary(),
        )

    # --- ajout ---------------------------------------------------------------

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> SubentryFlowResult:
        return await self.async_step_identity(user_input)

    async def async_step_identity(self, user_input: dict[str, Any] | None = None) -> SubentryFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                name = child_name(self._get_entry(), user_input["name"], exclude=self._self_id)
            except SettingsError as err:
                errors[err.field] = err.key
            else:
                self._name = name
                self._icon = user_input.get("icon") or DEFAULT_ICON
                self._enabled = user_input["enabled"]
                return self._after_edit() if self._reconfiguring else await self.async_step_code()

        suggested = user_input or {"name": self._name, "icon": self._icon, "enabled": self._enabled}
        return self.async_show_form(
            step_id="identity",
            data_schema=self.add_suggested_values_to_schema(identity_schema(), suggested),
            errors=errors,
        )

    async def async_step_code(self, user_input: dict[str, Any] | None = None) -> SubentryFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            error, hashed = await async_check_new_code(
                self.hass, self._get_entry(), user_input, exclude_child=self._self_id
            )
            if error:
                errors["code"] = error
            else:
                self._code = hashed
                return self._after_edit() if self._reconfiguring else await self.async_step_template()
        return self.async_show_form(
            step_id="code", data_schema=code_schema(), errors=errors, description_placeholders={"name": self._name}
        )

    async def async_step_template(self, user_input: dict[str, Any] | None = None) -> SubentryFlowResult:
        if user_input is not None:
            self._rules = template_rules(self._get_entry(), user_input["template"])
            return await self.async_step_summary()
        return self.async_show_form(
            step_id="template",
            data_schema=template_schema(self._other_children()),
            description_placeholders={"name": self._name},
        )

    async def async_step_summary(self, user_input: dict[str, Any] | None = None) -> SubentryFlowResult:
        if user_input is not None:
            return self.async_create_entry(
                title=self._name, data=self._draft().to_dict(), unique_id=name_key(self._name)
            )
        return self.async_show_form(
            step_id="summary", data_schema=vol.Schema({}), description_placeholders=self._summary()
        )

    # --- reconfiguration -----------------------------------------------------

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None) -> SubentryFlowResult:
        subentry = self._get_reconfigure_subentry()
        try:
            child = Child.from_dict(dict(subentry.data))
        except SettingsError:
            return self.async_abort(reason="invalid_data")
        self._name, self._icon, self._enabled = child.name, child.icon, child.enabled
        self._code, self._rules = child.code, child.rules
        return self._after_edit()

    async def async_step_quota_days(self, user_input: dict[str, Any] | None = None) -> SubentryFlowResult:
        return await self._select_days("quota_days", self.async_step_quota, user_input)

    async def async_step_slot_days(self, user_input: dict[str, Any] | None = None) -> SubentryFlowResult:
        return await self._select_days("slot_days", self.async_step_slots, user_input)

    async def _select_days(self, step_id: str, next_step: Any, user_input: dict[str, Any] | None) -> SubentryFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                self._days = expand_days(user_input["days"])
            except SettingsError as err:
                errors[err.field] = err.key
            else:
                return await next_step()
        return self.async_show_form(
            step_id=step_id, data_schema=days_schema(), errors=errors, description_placeholders=self._summary()
        )

    async def async_step_quota(self, user_input: dict[str, Any] | None = None) -> SubentryFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            duration = user_input.get("quota") or {}
            minutes = 0 if user_input["no_tv"] else int(duration.get("hours", 0)) * 60 + int(duration.get("minutes", 0))
            try:
                validate_quota(minutes)
            except SettingsError as err:
                errors[err.field] = err.key
            else:
                for day in self._days:
                    self._rules.quota_minutes[day] = minutes
                return self._after_edit()

        values = {self._rules.quota_minutes[day] for day in self._days}
        suggested = user_input
        if suggested is None and len(values) == 1:
            (minutes,) = values
            suggested = {"quota": {"hours": minutes // 60, "minutes": minutes % 60, "seconds": 0}}
        return self.async_show_form(
            step_id="quota",
            data_schema=self.add_suggested_values_to_schema(quota_schema(), suggested),
            errors=errors,
            description_placeholders={"days": self._days_label()},
        )

    async def async_step_slots(self, user_input: dict[str, Any] | None = None) -> SubentryFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            pairs = [
                (user_input.get(f"slot_{i}_start"), user_input.get(f"slot_{i}_end"))
                for i in range(1, MAX_SLOTS + 1)
            ]
            try:
                if user_input["no_slot"] and any(a or b for a, b in pairs):
                    raise SettingsError("slot_conflict")
                slots = [] if user_input["no_slot"] else normalize_slots(pairs)
            except SettingsError as err:
                errors[err.field] = err.key
            else:
                for day in self._days:
                    self._rules.slots[day] = list(slots)
                return self._after_edit()

        suggested = user_input
        if suggested is None and len({tuple(self._rules.slots[day]) for day in self._days}) == 1:
            current = self._rules.slots[self._days[0]]
            suggested = {}
            for index, slot in enumerate(current, start=1):
                suggested[f"slot_{index}_start"], suggested[f"slot_{index}_end"] = slot.to_list()
        return self.async_show_form(
            step_id="slots",
            data_schema=self.add_suggested_values_to_schema(slots_schema(), suggested),
            errors=errors,
            description_placeholders={"days": self._days_label()},
        )

    async def async_step_copy(self, user_input: dict[str, Any] | None = None) -> SubentryFlowResult:
        children = self._other_children()
        if not children:
            return self._after_edit()
        if user_input is not None:
            source = Child.from_dict(dict(self._get_entry().subentries[user_input["source"]].data)).rules
            if user_input["copy_quotas"]:
                self._rules.quota_minutes = dict(source.quota_minutes)
            if user_input["copy_slots"]:
                self._rules.slots = {day: list(slots) for day, slots in source.slots.items()}
            return self._after_edit()
        return self.async_show_form(step_id="copy", data_schema=copy_schema(children))

    async def async_step_save(self, user_input: dict[str, Any] | None = None) -> SubentryFlowResult:
        return self.async_update_and_abort(
            self._get_entry(),
            self._get_reconfigure_subentry(),
            title=self._name,
            unique_id=name_key(self._name),
            data=self._draft().to_dict(),
        )

    def _days_label(self) -> str:
        names = day_names(self.hass.config.language)
        return ", ".join(names[day] for day in self._days)
