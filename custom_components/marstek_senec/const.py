DOMAIN = "marstek_senec"

CONF_POWER_SENSOR = "power_sensor"
CONF_SOC_SENSOR = "soc_sensor"
CONF_MODE_SENSOR = "mode_sensor"
CONF_AUTO_SCRIPT = "auto_script"
CONF_MANUAL_SCRIPT = "manual_script"
CONF_CHARGE_THRESHOLD = "charge_threshold"
CONF_SOC_EMPTY_THRESHOLD = "soc_empty_threshold"
CONF_SOC_FULL_THRESHOLD = "soc_full_threshold"
CONF_CHECK_INTERVAL = "check_interval"

DEFAULT_CHARGE_THRESHOLD = 2300.0
DEFAULT_SOC_EMPTY_THRESHOLD = 5.0
DEFAULT_SOC_FULL_THRESHOLD = 100.0
DEFAULT_CHECK_INTERVAL = 60

MODE_AUTO = "auto"
MODE_MANUAL = "manual"
INVALID_STATES = {"unknown", "unavailable", "none", ""}
