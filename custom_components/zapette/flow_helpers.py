"""Schémas de formulaires et rendu du récapitulatif hebdomadaire."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.helpers.selector import (
    BooleanSelector,
    DurationSelector,
    DurationSelectorConfig,
    EntitySelector,
    EntitySelectorConfig,
    IconSelector,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
    TimeSelector,
)

from homeassistant.components.sensor import SensorDeviceClass

from .const import CONF_KEYPAD_TOPIC, CONF_PLUG_ENTITY, CONF_POWER_ENTITY
from .settings import DAY_SHORTCUTS, DAYS, MAX_SLOTS, Child, format_duration, warnings
from .tv_settings import (
    SECTION_KEYPAD_GUARD,
    SECTION_PLUG_BEHAVIOR,
    SECTION_SESSIONS,
    SECTIONS,
    Setting,
    section_values,
)

PASSWORD = TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD))

TEXTS: dict[str, dict[str, Any]] = {
    "fr": {
        "days": dict(zip(DAYS, ("Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"))),
        "header": "| Jour | Quota | Plages |\n|---|---|---|",
        "no_tv": "Pas de télé",
        "warnings": {
            "disabled": "{name} est désactivé : son code sera refusé.",
            "never_allowed": "{name} ne peut jamais regarder la télé.",
            "no_slot": "Pas de télé le {day} : aucune plage définie.",
            "no_quota": "Pas de télé le {day} : quota à 0.",
            "quota_exceeds_slots": "Le {day}, le quota ({quota}) dépasse la durée des plages ({slots}).",
        },
    },
    "en": {
        "days": dict(zip(DAYS, ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"))),
        "header": "| Day | Quota | Time slots |\n|---|---|---|",
        "no_tv": "No TV",
        "warnings": {
            "disabled": "{name} is disabled: their code will be refused.",
            "never_allowed": "{name} can never watch TV.",
            "no_slot": "No TV on {day}: no time slot.",
            "no_quota": "No TV on {day}: quota is 0.",
            "quota_exceeds_slots": "On {day}, the quota ({quota}) exceeds the time slots ({slots}).",
        },
    },
}


def _texts(language: str) -> dict[str, Any]:
    return TEXTS.get(language.split("-")[0], TEXTS["en"])


def day_names(language: str) -> dict[str, str]:
    return _texts(language)["days"]


def render_summary(child: Child, language: str) -> str:
    """Avertissements puis tableau Markdown de la semaine."""
    texts = _texts(language)
    lines: list[str] = []
    for key, params in warnings(child):
        if "day" in params:
            params = {**params, "day": texts["days"][params["day"]].lower()}
        lines.append("⚠️ " + texts["warnings"][key].format(**params))
    if lines:
        lines.append("")
    lines.append(texts["header"])
    for day in DAYS:
        rules = child.rules
        slots = ", ".join(str(slot) for slot in rules.slots[day]) or "—"
        quota = format_duration(rules.quota_minutes[day]) if rules.is_allowed_day(day) else texts["no_tv"]
        lines.append(f"| {texts['days'][day]} | {quota} | {slots} |")
    return "\n".join(lines)


def identity_schema() -> vol.Schema:
    return vol.Schema(
        {
            vol.Required("name"): TextSelector(),
            vol.Optional("icon"): IconSelector(),
            vol.Required("enabled", default=True): BooleanSelector(),
        }
    )


def code_schema() -> vol.Schema:
    return vol.Schema({vol.Required("code"): PASSWORD, vol.Required("code_confirm"): PASSWORD})


def parent_schema(code_required: bool) -> vol.Schema:
    """Ajout : code obligatoire. Modification : code vide = inchangé."""
    key = vol.Required if code_required else vol.Optional
    return vol.Schema(
        {vol.Required("name"): TextSelector(), key("code"): PASSWORD, key("code_confirm"): PASSWORD}
    )


def parent_select_schema(parents: dict[str, str]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required("parent"): SelectSelector(
                SelectSelectorConfig(
                    options=[SelectOptionDict(value=pid, label=name) for pid, name in parents.items()],
                    mode=SelectSelectorMode.LIST,
                )
            )
        }
    )


def template_schema(children: dict[str, str]) -> vol.Schema:
    options = [
        SelectOptionDict(value="default", label="default"),
        SelectOptionDict(value="empty", label="empty"),
    ] + [SelectOptionDict(value=f"copy:{sid}", label=title) for sid, title in children.items()]
    return vol.Schema(
        {
            vol.Required("template", default="default"): SelectSelector(
                SelectSelectorConfig(
                    options=options, translation_key="template", mode=SelectSelectorMode.LIST
                )
            )
        }
    )


def copy_schema(children: dict[str, str]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required("source"): SelectSelector(
                SelectSelectorConfig(
                    options=[SelectOptionDict(value=sid, label=title) for sid, title in children.items()]
                )
            ),
            vol.Required("copy_quotas", default=True): BooleanSelector(),
            vol.Required("copy_slots", default=True): BooleanSelector(),
        }
    )


def days_schema() -> vol.Schema:
    return vol.Schema(
        {
            vol.Required("days", default=[]): SelectSelector(
                SelectSelectorConfig(
                    options=[*DAY_SHORTCUTS, *DAYS],
                    multiple=True,
                    translation_key="days",
                    mode=SelectSelectorMode.LIST,
                )
            )
        }
    )


def quota_schema() -> vol.Schema:
    return vol.Schema(
        {
            vol.Optional("quota"): DurationSelector(DurationSelectorConfig(enable_day=False)),
            vol.Required("no_tv", default=False): BooleanSelector(),
        }
    )


def slots_schema() -> vol.Schema:
    fields: dict[Any, Any] = {}
    for index in range(1, MAX_SLOTS + 1):
        fields[vol.Optional(f"slot_{index}_start")] = TimeSelector()
        fields[vol.Optional(f"slot_{index}_end")] = TimeSelector()
    fields[vol.Required("no_slot", default=False)] = BooleanSelector()
    return vol.Schema(fields)


def plug_schema() -> vol.Schema:
    """Prise (switch) et capteur de puissance facultatif."""
    return vol.Schema(
        {
            vol.Required(CONF_PLUG_ENTITY): EntitySelector(EntitySelectorConfig(domain="switch")),
            vol.Optional(CONF_POWER_ENTITY): EntitySelector(
                EntitySelectorConfig(domain="sensor", device_class=SensorDeviceClass.POWER)
            ),
        }
    )


def _setting_selector(item: Setting) -> Any:
    if item.kind == "bool":
        return BooleanSelector()
    if item.kind == "choice":
        return SelectSelector(
            SelectSelectorConfig(options=list(item.choices), translation_key=item.key, mode=SelectSelectorMode.DROPDOWN)
        )
    config = NumberSelectorConfig(min=item.low, max=item.high, step=1, mode=NumberSelectorMode.BOX)
    if item.unit:
        config["unit_of_measurement"] = item.unit
    return NumberSelector(config)


def section_schema(section: str, options: dict[str, Any]) -> vol.Schema:
    """Formulaire d'une section de réglages : bornes, unités et défauts de `tv_settings`."""
    values = section_values(section, options)
    return vol.Schema(
        {vol.Required(item.key, default=values[item.key]): _setting_selector(item) for item in SECTIONS[section]}
    )


def plug_settings_schema(options: dict[str, Any]) -> vol.Schema:
    return section_schema(SECTION_PLUG_BEHAVIOR, options)


def keypad_schema(keypads: dict[str, str], test: bool = True) -> vol.Schema:
    """Sujet du clavier : choisi parmi les claviers découverts ou saisi ; vide = pas de clavier."""
    if keypads:
        selector: Any = SelectSelector(
            SelectSelectorConfig(
                options=[SelectOptionDict(value=topic, label=label) for topic, label in keypads.items()],
                custom_value=True,
                mode=SelectSelectorMode.DROPDOWN,
            )
        )
    else:
        selector = TextSelector()
    return vol.Schema(
        {
            vol.Optional(CONF_KEYPAD_TOPIC): selector,
            vol.Required("test_keypad", default=test): BooleanSelector(),
        }
    )


def keypad_settings_schema(options: dict[str, Any]) -> vol.Schema:
    return section_schema(SECTION_KEYPAD_GUARD, options)


def session_settings_schema(options: dict[str, Any]) -> vol.Schema:
    """Avertissement avant coupure (0 = aucun), bip du clavier, durée maximale d'une session parent (0 = jamais)."""
    return section_schema(SECTION_SESSIONS, options)
