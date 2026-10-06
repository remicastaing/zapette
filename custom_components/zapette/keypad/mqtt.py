"""Clavier Zigbee2MQTT : saisies (`action` + `action_code`), pile, disponibilité, retour `arm_mode`.

Aucun modèle n'est codé en dur : les capacités de retour sont lues dans les `exposes` publiés par
Zigbee2MQTT sur `<base>/bridge/devices`. Le code reçu n'est jamais journalisé.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
import json
import logging
from typing import Any

from homeassistant.components import mqtt
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_call_later

from ..const import DOMAIN
from .base import SOURCE_KEYPAD, KeypadAdapter, KeypadStatus, Submission

_LOGGER = logging.getLogger(__name__)

DEFAULT_BASE = "zigbee2mqtt"
DATA_TESTS = "keypad_tests"
FORBIDDEN_SUFFIXES = ("/set", "/get", "/availability")
SUCCESS_FALLBACK = "disarm"
FAILURE_MODES = ("invalid_code", "not_ready")
# Réponse d'armement du cluster IAS ACE (ZCL) : envoyée par Zigbee2MQTT quand `arm_mode` porte la
# transaction de la saisie. Valeurs fixées par la norme, indépendantes du modèle de clavier.
ARM_RESPONSE_MODES = ["disarm", "arm_day_zones", "arm_night_zones", "arm_all_zones", "invalid_code", "not_ready", "already_disarmed"]


class TopicError(ValueError):
    """Sujet de clavier invalide."""


# --- Fonctions pures ----------------------------------------------------------


def normalize_topic(text: str) -> str:
    """`clavier` → `zigbee2mqtt/clavier` ; refuse jokers, sujets techniques et vides."""
    topic = (text or "").strip().strip("/")
    if not topic or "+" in topic or "#" in topic or any(c.isspace() for c in topic):
        raise TopicError(text)
    if "/" not in topic:
        topic = f"{DEFAULT_BASE}/{topic}"
    base, _, name = topic.partition("/")
    if not name or name == "bridge" or name.startswith("bridge/") or topic.endswith(FORBIDDEN_SUFFIXES):
        raise TopicError(text)
    return topic


def split_topic(topic: str) -> tuple[str, str]:
    """(`zigbee2mqtt`, `mon_clavier`)."""
    base, _, name = topic.partition("/")
    return base, name


def parse_state(payload: str | bytes) -> tuple[Submission | None, dict[str, Any]]:
    """Message de l'appareil → (saisie éventuelle, attributs d'état utiles)."""
    data = json.loads(payload)
    if not isinstance(data, dict):
        raise ValueError("not an object")
    status: dict[str, Any] = {}
    battery = data.get("battery")
    if isinstance(battery, (int, float)) and not isinstance(battery, bool):
        status["battery"] = round(battery)
    action, code = data.get("action"), data.get("action_code")
    if isinstance(code, bool):
        code = None
    if isinstance(code, (int, float)):
        code = str(int(code))
    if not action or not isinstance(action, str):
        return None, status
    if not isinstance(code, str):
        code = ""
    context = {}
    if isinstance(data.get("action_transaction"), int):
        context["transaction"] = data["action_transaction"]
    return Submission(code.strip(), action, SOURCE_KEYPAD, context), status


def parse_availability(payload: str | bytes) -> bool | None:
    text = payload.decode() if isinstance(payload, bytes) else payload
    try:
        data = json.loads(text)
        state = data.get("state") if isinstance(data, dict) else data
    except ValueError:
        state = text.strip()
    if state == "online":
        return True
    if state == "offline":
        return False
    return None


def _find(node: Any, name: str) -> dict[str, Any] | None:
    """Cherche récursivement une capacité (`exposes`) par nom ou propriété."""
    if isinstance(node, dict):
        if node.get("name") == name or node.get("property") == name:
            return node
        node = node.get("features") or []
    if isinstance(node, list):
        for item in node:
            if found := _find(item, name):
                return found
    return None


def keypad_devices(devices: Any) -> dict[str, str]:
    """Appareils qui publient un code saisi : {friendly_name: modèle}."""
    result: dict[str, str] = {}
    for device in devices if isinstance(devices, list) else []:
        definition = device.get("definition") or {}
        if _find(definition.get("exposes"), "action_code"):
            label = " ".join(filter(None, (definition.get("vendor"), definition.get("model"))))
            result[device.get("friendly_name", "")] = label
    return {name: label for name, label in result.items() if name}


def arm_modes(devices: Any, friendly_name: str) -> list[str]:
    """Valeurs de `arm_mode.mode` exposées par l'appareil ([] : pas de retour possible)."""
    for device in devices if isinstance(devices, list) else []:
        if device.get("friendly_name") != friendly_name:
            continue
        arm_mode = _find((device.get("definition") or {}).get("exposes"), "arm_mode")
        if arm_mode is None:
            return []
        mode = _find(arm_mode.get("features") or [], "mode")
        return list((mode or {}).get("values") or [])
    return []


def feedback_payload(modes: list[str], submission: Submission, success: bool) -> dict[str, Any] | None:
    """Charge `arm_mode` à publier, ou None si le clavier ne sait pas l'afficher.

    Une saisie qui porte une transaction attend la réponse d'armement normalisée (IAS ACE) : ses
    modes sont ceux de la norme, même si le clavier ne déclare pas `arm_mode` dans ses `exposes`
    (cas du frient KEPZB‑110). Sinon, on se fie aux modes déclarés.
    """
    if "transaction" in submission.context:
        modes = ARM_RESPONSE_MODES
    if not modes:
        return None
    if success:
        mode = submission.key if submission.key in modes else SUCCESS_FALLBACK
        if mode not in modes:
            return None
    else:
        mode = next((m for m in FAILURE_MODES if m in modes), None)
        if mode is None:
            return None
    arm_mode: dict[str, Any] = {"mode": mode}
    if "transaction" in submission.context:
        arm_mode["transaction"] = submission.context["transaction"]
    return {"arm_mode": arm_mode}


WARN_DELAY = 5  # s : durée du bip (temporisation de sortie) avant le retour au repos


def warn_payloads(modes: list[str], ias_ace: bool) -> list[dict[str, Any]]:
    """Bip d'avertissement : état « temporisation de sortie » sonore, puis retour au repos.

    Sans transaction, Zigbee2MQTT envoie un `panelStatusChanged` IAS ACE (`delay` → secondes
    restantes, `audiblenotif` 1 = son par défaut). Seulement pour un clavier IAS ACE reconnu ou
    qui déclare `exit_delay`.
    """
    if not ias_ace and "exit_delay" not in modes:
        return []
    return [
        {"arm_mode": {"mode": "exit_delay", "delay": WARN_DELAY, "audiblenotif": 1}},
        {"arm_mode": {"mode": "disarm"}},
    ]


# --- Home Assistant -----------------------------------------------------------


def mqtt_ready(hass: HomeAssistant) -> bool:
    return "mqtt" in hass.config.components and mqtt.is_connected(hass)


def _tests(hass: HomeAssistant) -> set[str]:
    return hass.data.setdefault(DOMAIN, {}).setdefault(DATA_TESTS, set())


async def async_discover_keypads(hass: HomeAssistant, base: str = DEFAULT_BASE, timeout: float = 3) -> dict[str, str]:
    """Claviers connus de Zigbee2MQTT (message retenu `<base>/bridge/devices`)."""
    if not mqtt_ready(hass):
        return {}
    devices = await _async_read_retained(hass, f"{base}/bridge/devices", timeout)
    return keypad_devices(devices)


async def _async_read_retained(hass: HomeAssistant, topic: str, timeout: float) -> Any:
    future: asyncio.Future[Any] = hass.loop.create_future()

    @callback
    def received(msg: mqtt.ReceiveMessage) -> None:
        if not future.done():
            try:
                future.set_result(json.loads(msg.payload))
            except ValueError:
                future.set_result(None)

    unsub = await mqtt.async_subscribe(hass, topic, received)
    try:
        async with asyncio.timeout(timeout):
            return await future
    except TimeoutError:
        return None
    finally:
        unsub()


async def async_wait_for_key(hass: HomeAssistant, topic: str, timeout: float) -> str:
    """Test de saisie : attend une saisie avec code sur le sujet et renvoie **seulement** la touche.

    Pendant l'attente, l'adaptateur d'une instance chargée ignore ce sujet (rien n'est évalué).
    Lève `TimeoutError` si rien n'arrive.
    """
    future: asyncio.Future[str] = hass.loop.create_future()

    @callback
    def received(msg: mqtt.ReceiveMessage) -> None:
        try:
            submission, _status = parse_state(msg.payload)
        except ValueError:
            return
        if submission is not None and submission.code and not future.done():
            future.set_result(submission.key or "")

    tests = _tests(hass)
    tests.add(topic)
    unsub = await mqtt.async_subscribe(hass, topic, received)
    try:
        async with asyncio.timeout(timeout):
            return await future
    finally:
        unsub()
        tests.discard(topic)


class Zigbee2MqttKeypad(KeypadAdapter):
    """Clavier désigné par son sujet Zigbee2MQTT."""

    def __init__(
        self,
        hass: HomeAssistant,
        topic: str,
        on_submission: Callable[[Submission], None],
        on_status: Callable[[KeypadStatus], None],
        ias_ace: bool = False,
    ) -> None:
        super().__init__(on_submission, on_status)
        self.ias_ace = ias_ace
        self.hass = hass
        self.topic = topic
        self.base, self.name = split_topic(topic)
        self.modes: list[str] = []
        self._unsubs: list[Callable[[], None]] = []

    async def async_start(self) -> None:
        if "mqtt" not in self.hass.config.components:
            _LOGGER.warning("Clavier %s : l'intégration MQTT n'est pas configurée", self.topic)
            return
        self._unsubs = [
            await mqtt.async_subscribe(self.hass, self.topic, self._on_message),
            await mqtt.async_subscribe(self.hass, f"{self.topic}/availability", self._on_availability),
            await mqtt.async_subscribe(self.hass, f"{self.base}/bridge/devices", self._on_devices),
        ]

    async def async_stop(self) -> None:
        for unsub in self._unsubs:
            unsub()
        self._unsubs = []

    async def async_feedback(self, submission: Submission, success: bool) -> None:
        payload = feedback_payload(self.modes, submission, success)
        if payload is not None:
            await mqtt.async_publish(self.hass, f"{self.topic}/set", json.dumps(payload))

    async def async_warn(self) -> None:
        payloads = warn_payloads(self.modes, self.ias_ace)
        if not payloads:
            return
        first, rest = payloads[0], payloads[1:]
        await mqtt.async_publish(self.hass, f"{self.topic}/set", json.dumps(first))

        async def back_to_rest(_now: Any) -> None:
            for payload in rest:
                await mqtt.async_publish(self.hass, f"{self.topic}/set", json.dumps(payload))

        self._unsubs.append(async_call_later(self.hass, WARN_DELAY, back_to_rest))

    @callback
    def _on_message(self, msg: mqtt.ReceiveMessage) -> None:
        try:
            submission, status = parse_state(msg.payload)
        except ValueError:
            _LOGGER.warning("Clavier %s : message illisible ignoré", self.topic)
            return
        if "battery" in status:
            self._set_status(battery=status["battery"])
        if submission is None or self.topic in _tests(self.hass):
            return
        self.on_submission(submission)

    @callback
    def _on_availability(self, msg: mqtt.ReceiveMessage) -> None:
        self._set_status(available=parse_availability(msg.payload))

    @callback
    def _on_devices(self, msg: mqtt.ReceiveMessage) -> None:
        try:
            self.modes = arm_modes(json.loads(msg.payload), self.name)
        except ValueError:
            return

    def _set_status(self, **changes: Any) -> None:
        self.status = KeypadStatus(**{**self.status.__dict__, **changes})
        self.on_status(self.status)
