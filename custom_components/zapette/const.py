"""Constantes de Zapette."""

DOMAIN = "zapette"

SUBENTRY_CHILD = "child"

CONF_TV_NAME = "tv_name"
CONF_PARENTS = "parents"

# Prise (tranche 1)
CONF_PLUG_ENTITY = "plug_entity"
CONF_POWER_ENTITY = "power_entity"
CONF_TOLERATE_MANUAL = "tolerate_manual"
CONF_STANDBY_THRESHOLD = "standby_threshold"
CONF_STANDBY_DELAY = "standby_delay"

DEFAULT_TOLERATE_MANUAL = False
DEFAULT_STANDBY_THRESHOLD = 15  # W
DEFAULT_STANDBY_DELAY = 3  # min

EVENT_BYPASS = "zapette_bypass_detected"
EVENT_STANDBY = "zapette_standby_detected"
EVENT_PLUG_LOST = "zapette_plug_lost"
EVENT_PLUG_BACK = "zapette_plug_back"

SERVICE_TURN_ON = "turn_on_tv"
SERVICE_TURN_OFF = "turn_off_tv"

# Clavier et codes (tranche 2)
CONF_KEYPAD_TOPIC = "keypad_topic"
CONF_LOCKOUT_FAILURES = "lockout_failures"
CONF_LOCKOUT_WINDOW = "lockout_window"
CONF_LOCKOUT_DURATION = "lockout_duration"
CONF_OFF_KEY = "off_key"

DEFAULT_LOCKOUT_FAILURES = 5
DEFAULT_LOCKOUT_WINDOW = 5  # min
DEFAULT_LOCKOUT_DURATION = 10  # min
DEFAULT_OFF_KEY = "arm_all_zones"  # cadenas du frient KEPZB-110 ; réglable
OFF_KEY_NONE = "none"
BATTERY_LOW = 15  # %

EVENT_ACCESS_GRANTED = "zapette_access_granted"
EVENT_ACCESS_DENIED = "zapette_access_denied"
EVENT_LOCKOUT = "zapette_lockout"
EVENT_KEYPAD_OFF = "zapette_keypad_turn_off"

SERVICE_SUBMIT_CODE = "submit_code"
SERVICE_UNBLOCK_KEYPAD = "unblock_keypad"

# Sessions et quotas (tranche 3)
CONF_WARNING_MINUTES = "warning_minutes"
CONF_WARNING_BEEP = "warning_beep"
CONF_PARENT_MAX_HOURS = "parent_max_hours"

DEFAULT_WARNING_MINUTES = 5  # 0 = pas d'avertissement
DEFAULT_WARNING_BEEP = True
DEFAULT_PARENT_MAX_HOURS = 4  # 0 = jamais

EVENT_SESSION_STARTED = "zapette_session_started"
EVENT_SESSION_WARNING = "zapette_session_warning"
EVENT_SESSION_ENDED = "zapette_session_ended"

SERVICE_START_SESSION = "start_session"
SERVICE_STOP_SESSION = "stop_session"

# Historique d'utilisation (tranche 4)
CONF_STANDBY_CUT = "standby_cut"

DEFAULT_STANDBY_CUT = True  # désactivé : veille détectée sans coupure (réglage de développement)

# Réglages dans le panneau (tranche 5)
KEYPAD_TEST_TIMEOUT = 60  # s : attente du test de saisie (flux et panneau)
