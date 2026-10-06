"""Pilotage de la prise : état souhaité, sûreté, contournement, veille.

Ce module n'importe rien de Home Assistant. Chaque entrée est horodatée et renvoie la liste des
effets à exécuter ; `next_deadline()` donne l'instant auquel appeler `tick()`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

GRACE = timedelta(minutes=2)
CONFIRM_TIMEOUT = timedelta(seconds=10)
RETRY_INTERVAL = timedelta(seconds=30)
ALERT_DELAY = timedelta(minutes=2)

PROBLEM_UNREACHABLE = "unreachable"
PROBLEM_OFF_FAILED = "off_failed"


@dataclass(frozen=True)
class PlugSettings:
    tolerate_manual: bool = False
    standby_threshold: float = 15.0  # W
    standby_delay: timedelta = timedelta(minutes=3)
    standby_cut: bool = True  # faux : veille détectée sans coupure (réglage de développement)


# --- Effets -----------------------------------------------------------------


@dataclass(frozen=True)
class Command:
    """Allumer ou couper la prise."""

    on: bool


@dataclass(frozen=True)
class Bypass:
    """Prise allumée sans demande alors que l'état souhaité est « coupée »."""

    tolerated: bool


@dataclass(frozen=True)
class Standby:
    """Télé en veille (puissance sous le seuil pendant le délai) ; `cut` : la prise est coupée."""

    power: float | None
    cut: bool = True


@dataclass(frozen=True)
class PlugLost:
    at: datetime


@dataclass(frozen=True)
class PlugBack:
    lost_at: datetime
    at: datetime

    @property
    def duration(self) -> timedelta:
        return self.at - self.lost_at


Effect = Command | Bypass | Standby | PlugLost | PlugBack


class PlugRefused(Exception):
    """Demande refusée ; `reason` est une clé de traduction."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


@dataclass(frozen=True)
class Pending:
    on: bool
    sent_at: datetime


# --- Logique ----------------------------------------------------------------


class PlugLogic:
    """État de pilotage d'une prise. Un objet neuf = démarrage : état souhaité « coupée »."""

    def __init__(self, plug_entity: str, settings: PlugSettings, control_active: bool = True) -> None:
        self.plug_entity = plug_entity
        self.settings = settings
        self.control_active = control_active
        self.desired_on = False
        self.available: bool | None = None  # None : jamais observée
        self.plug_on: bool | None = None  # dernier état connu quand joignable
        self.synced = False  # première observation à réconcilier
        self.adopt = False  # après un changement de prise : adopter son état
        self.tolerated = False
        self.pending: Pending | None = None
        self.off_failing_since: datetime | None = None
        self.off_alert = False
        self.next_retry: datetime | None = None
        self.lost_since: datetime | None = None
        self.lost_reported = False  # PlugLost émis pour la perte en cours
        self.grace_expired = False
        self.power: float | None = None
        self.low_since: datetime | None = None
        self.standby = False

    # --- lecture -------------------------------------------------------------

    @property
    def problem(self) -> str | None:
        if self.grace_expired:
            return PROBLEM_UNREACHABLE
        if self.off_alert:
            return PROBLEM_OFF_FAILED
        return None

    @property
    def is_on(self) -> bool:
        return bool(self.available and self.plug_on)

    def next_deadline(self) -> datetime | None:
        deadlines: list[datetime] = []
        if self.pending:
            deadlines.append(self.pending.sent_at + CONFIRM_TIMEOUT)
        if self.next_retry:
            deadlines.append(self.next_retry)
        if self.off_failing_since and not self.off_alert:
            deadlines.append(self.off_failing_since + ALERT_DELAY)
        if self.lost_since and not self.grace_expired:
            deadlines.append(self.lost_since + GRACE)
        if self.low_since and not self.standby and self.is_on:
            deadlines.append(self.low_since + self.settings.standby_delay)
        return min(deadlines, default=None)

    # --- entrées -------------------------------------------------------------

    def request(self, on: bool, now: datetime) -> list[Effect]:
        """Demande du parent (action, bouton)."""
        if not self.control_active:
            raise PlugRefused("control_inactive")
        if on and not self.available:
            raise PlugRefused("plug_unavailable")
        self.desired_on = on
        self.tolerated = False
        contradicted = self.pending is not None and self.pending.on != on
        if self.available and (self.plug_on != on or contradicted):
            return self._send(on, now)
        if contradicted:
            self.pending = None
        return []

    def observe_plug(self, state: str | None, now: datetime) -> list[Effect]:
        """Nouvel état de la prise : "on", "off", ou None (indisponible, inconnue, absente)."""
        effects: list[Effect] = []
        if state not in ("on", "off"):
            if self.available is not False:
                # Jamais vue depuis le démarrage (MQTT pas encore connecté) : la perte n'est
                # signalée que si elle dépasse le délai de grâce, datée du démarrage.
                self.lost_reported = self.available is True
                self.available = False
                self.lost_since = now
                self.pending = None
                self.low_since = None
                self.standby = False
                if self.lost_reported:
                    effects.append(PlugLost(now))
            return effects

        on = state == "on"
        returned = self.available is False
        if returned and self.lost_since is not None and self.lost_reported:
            effects.append(PlugBack(self.lost_since, now))
        self.lost_since = None
        self.lost_reported = False
        self.grace_expired = False
        self.available = True
        previous, self.plug_on = self.plug_on, on

        if self.adopt:
            self.adopt = False
            self.synced = True
            self.desired_on = on
            self.tolerated = False
        elif not self.synced:
            self.synced = True
            if self.control_active and on != self.desired_on:
                effects += self._send(self.desired_on, now)
        elif previous != on:
            effects += self._turned_on(now) if on else self._turned_off()
        elif returned and on and not self.desired_on and not self.tolerated and self.control_active:
            effects += self._send(False, now)

        if on:
            self._arm_low_power(now)
        else:
            self._reset_off()
        return effects

    def observe_power(self, watts: float | None, now: datetime) -> list[Effect]:
        """Nouvelle mesure de puissance (W) ; None si absente ou illisible."""
        self.power = watts
        if watts is None or not self.is_on:
            self.low_since = None
        elif watts < self.settings.standby_threshold:
            self.low_since = self.low_since or now
        else:
            self.low_since = None
            self.standby = False
        return []

    def set_control(self, active: bool, now: datetime) -> list[Effect]:
        """Interrupteur « Contrôle actif »."""
        if active == self.control_active:
            return []
        self.control_active = active
        if not active:
            self.pending = None
            self._clear_off_failure()
            return []
        self.desired_on = False
        self.tolerated = False
        if self.is_on:
            return self._send(False, now)
        return []

    def command_failed(self, on: bool, now: datetime) -> list[Effect]:
        """L'envoi de la commande a échoué."""
        if self.pending and self.pending.on == on:
            return self._command_timeout(now)
        return []

    def tick(self, now: datetime) -> list[Effect]:
        """Échéance de la minuterie."""
        effects: list[Effect] = []
        if self.pending and now >= self.pending.sent_at + CONFIRM_TIMEOUT:
            effects += self._command_timeout(now)
        if self.next_retry and now >= self.next_retry:
            self.next_retry = None
            if self.control_active and self.is_on and not self.desired_on and not self.tolerated:
                effects += self._send(False, now)
            else:
                self._clear_off_failure()
        if self.off_failing_since and not self.off_alert and now >= self.off_failing_since + ALERT_DELAY:
            self.off_alert = True
        if self.lost_since and not self.grace_expired and now >= self.lost_since + GRACE:
            if not self.lost_reported:
                self.lost_reported = True
                effects.append(PlugLost(self.lost_since))
            self.grace_expired = True
            self.desired_on = False
            self.tolerated = False
            self.synced = False
        if (
            self.low_since
            and not self.standby
            and self.is_on
            and now >= self.low_since + self.settings.standby_delay
        ):
            self.standby = True
            cut = self.control_active and self.settings.standby_cut
            effects.append(Standby(self.power, cut))
            if cut:
                self.desired_on = False
                self.tolerated = False
                effects += self._send(False, now)
        return effects

    def change_plug(self, plug_entity: str) -> None:
        """Nouvelle prise : aucune commande ; l'état souhaité adoptera son état réel."""
        self.plug_entity = plug_entity
        self.available = None
        self.plug_on = None
        self.pending = None
        self._clear_off_failure()
        self.lost_since = None
        self.lost_reported = False
        self.grace_expired = False
        self.low_since = None
        self.standby = False
        self.desired_on = False
        self.tolerated = False
        self.adopt = True

    def update_settings(self, settings: PlugSettings, now: datetime) -> None:
        """Réglages modifiés : aucune commande immédiate."""
        self.settings = settings
        if self.power is not None and self.power >= settings.standby_threshold:
            self.low_since = None
            self.standby = False
        else:
            self._arm_low_power(now)

    # --- interne -------------------------------------------------------------

    def _send(self, on: bool, now: datetime) -> list[Effect]:
        self.pending = Pending(on, now)
        return [Command(on)]

    def _turned_on(self, now: datetime) -> list[Effect]:
        if self.pending and self.pending.on:
            self.pending = None
            return []
        if self.desired_on or self.tolerated or not self.control_active:
            return []
        if self.settings.tolerate_manual:
            self.tolerated = True
            return [Bypass(tolerated=True)]
        return [Bypass(tolerated=False), *self._send(False, now)]

    def _turned_off(self) -> list[Effect]:
        if self.pending and not self.pending.on:
            self.pending = None
        self.desired_on = False
        self.tolerated = False
        return []

    def _reset_off(self) -> None:
        if self.pending and not self.pending.on:
            self.pending = None
        self._clear_off_failure()
        self.low_since = None
        self.standby = False

    def _clear_off_failure(self) -> None:
        self.off_failing_since = None
        self.off_alert = False
        self.next_retry = None

    def _arm_low_power(self, now: datetime) -> None:
        if self.is_on and self.power is not None and self.power < self.settings.standby_threshold:
            self.low_since = self.low_since or now

    def _command_timeout(self, now: datetime) -> list[Effect]:
        pending, self.pending = self.pending, None
        if pending is None:
            return []
        if pending.on:
            self.desired_on = False
            return self._send(False, now) if self.is_on else []
        self.off_failing_since = self.off_failing_since or pending.sent_at
        self.next_retry = now + RETRY_INTERVAL
        return []
