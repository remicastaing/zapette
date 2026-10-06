"""Actions : allumer et couper la télé, saisir un code, déverrouiller le clavier."""

from __future__ import annotations

import voluptuous as vol

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse, callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv

from .access import ZapetteRuntime
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    SERVICE_START_SESSION,
    SERVICE_STOP_SESSION,
    SERVICE_SUBMIT_CODE,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    SERVICE_UNBLOCK_KEYPAD,
)
from .coordinator import PlugCoordinator
from .keypad.base import SOURCE_ACTION, Submission
from .plug import PlugRefused
from .rules import CONTROL_INACTIVE, END_STOPPED, KIND_CHILD, PLUG_UNAVAILABLE, TV_IN_USE
from .session_coordinator import SessionCoordinator, entry_profiles
from .settings import SettingsError, name_key

ATTR_CONFIG_ENTRY_ID = "config_entry_id"
ATTR_CODE = "code"
ATTR_KEY = "key"
SCHEMA = vol.Schema({vol.Required(ATTR_CONFIG_ENTRY_ID): cv.string})
ATTR_PROFILE = "profile"
ATTR_IGNORE_RULES = "ignore_rules"
START_SCHEMA = SCHEMA.extend({vol.Required(ATTR_PROFILE): cv.string, vol.Optional(ATTR_IGNORE_RULES, default=False): cv.boolean})
SUBMIT_SCHEMA = SCHEMA.extend({vol.Required(ATTR_CODE): vol.All(cv.string, vol.Length(min=1)), vol.Optional(ATTR_KEY): cv.string})


def request(coordinator: PlugCoordinator, on: bool) -> None:
    """Demande commune aux actions et aux boutons ; erreur traduite en cas de refus."""
    try:
        coordinator.async_request(on)
    except PlugRefused as err:
        raise ServiceValidationError(translation_domain=DOMAIN, translation_key=err.reason) from err


def turn_off(coordinator: PlugCoordinator, sessions: SessionCoordinator) -> None:
    """« Couper la télé » : pendant une session, la termine (motif `stopped`) ; sinon coupe la prise."""
    if not sessions.async_stop(END_STOPPED):
        request(coordinator, False)


def _refuse(reason: str) -> ServiceValidationError:
    return ServiceValidationError(translation_domain=DOMAIN, translation_key=reason)


def start_session(runtime: ZapetteRuntime, profile_name: str, ignore_rules: bool) -> None:
    """Action `start_session` : mêmes contrôles que le clavier, sauf code et verrouillage."""
    sessions = runtime.sessions
    profiles, _ = entry_profiles(sessions.entry)
    try:
        key = name_key(profile_name)
    except SettingsError as err:
        raise _refuse("profile_unknown") from err
    profile = next((p for p in profiles.values() if name_key(p.name) == key), None)
    if profile is None:
        raise _refuse("profile_unknown")
    if sessions.session is not None:
        raise _refuse(TV_IN_USE)
    plug = runtime.plug
    if plug is None:
        raise _refuse(PLUG_UNAVAILABLE)
    if not plug.logic.control_active:
        raise _refuse(CONTROL_INACTIVE)
    if not plug.logic.available:
        raise _refuse(PLUG_UNAVAILABLE)
    if profile.kind == KIND_CHILD and not ignore_rules:
        if reason := sessions.logic.refusal(profile.id, dt_util.utcnow()):
            raise _refuse(reason)
    try:
        sessions.async_start_session(profile, SOURCE_ACTION, ignore_rules=ignore_rules)
    except PlugRefused as err:
        raise _refuse(err.reason) from err


def _runtime(hass: HomeAssistant, call: ServiceCall) -> ZapetteRuntime:
    entry = hass.config_entries.async_get_entry(call.data[ATTR_CONFIG_ENTRY_ID])
    if entry is None or entry.domain != DOMAIN or entry.state is not ConfigEntryState.LOADED:
        raise ServiceValidationError(translation_domain=DOMAIN, translation_key="entry_not_loaded")
    return entry.runtime_data


def _coordinator(hass: HomeAssistant, call: ServiceCall) -> PlugCoordinator:
    if not (coordinator := _runtime(hass, call).plug):
        raise ServiceValidationError(translation_domain=DOMAIN, translation_key="entry_not_loaded")
    return coordinator


@callback
def async_register_services(hass: HomeAssistant) -> None:
    async def turn_on(call: ServiceCall) -> None:
        request(_coordinator(hass, call), True)

    async def turn_off_tv(call: ServiceCall) -> None:
        runtime = _runtime(hass, call)
        turn_off(_coordinator(hass, call), runtime.sessions)

    async def start(call: ServiceCall) -> None:
        start_session(_runtime(hass, call), call.data[ATTR_PROFILE], call.data[ATTR_IGNORE_RULES])

    async def stop(call: ServiceCall) -> None:
        _runtime(hass, call).sessions.async_stop(END_STOPPED)

    async def submit_code(call: ServiceCall) -> ServiceResponse:
        """Saisie générique : mêmes règles et même anti‑essais que le clavier, sans retour."""
        access = _runtime(hass, call).access
        submission = Submission(call.data[ATTR_CODE], call.data.get(ATTR_KEY), SOURCE_ACTION)
        decision = await access.async_submit(submission)
        profile = decision.profile
        return {
            "granted": decision.granted,
            "reason": decision.reason,
            "profile": profile.name if profile else None,
            "kind": profile.kind if profile else None,
            "action": decision.action,
        }

    async def unblock_keypad(call: ServiceCall) -> None:
        _runtime(hass, call).access.async_unblock()

    hass.services.async_register(DOMAIN, SERVICE_TURN_ON, turn_on, schema=SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_TURN_OFF, turn_off_tv, schema=SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_START_SESSION, start, schema=START_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_STOP_SESSION, stop, schema=SCHEMA)
    hass.services.async_register(
        DOMAIN, SERVICE_SUBMIT_CODE, submit_code, schema=SUBMIT_SCHEMA, supports_response=SupportsResponse.OPTIONAL
    )
    hass.services.async_register(DOMAIN, SERVICE_UNBLOCK_KEYPAD, unblock_keypad, schema=SCHEMA)
