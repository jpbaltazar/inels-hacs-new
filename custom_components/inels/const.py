"""Constants for the iNels integration."""
import logging
from homeassistant.components.binary_sensor import BinarySensorDeviceClass

from homeassistant.const import (
    LIGHT_LUX,
    PERCENTAGE,
    Platform,
    UnitOfElectricPotential,
    UnitOfTemperature,
)
from homeassistant.helpers.entity import EntityCategory

from inelsmqtt.const import (
    TEMP_IN,
    TEMP_OUT,
)

DOMAIN = "inels"

BROKER_CONFIG = "inels_mqtt_broker_config"
BROKER = "inels_mqtt_broker"
DEVICES = "devices"

CONF_DISCOVERY_PREFIX = "discovery_prefix"

TITLE = "iNELS"
DESCRIPTION = ""
INELS_VERSION = 1
LOGGER = logging.getLogger(__package__)

DEFAULT_MIN_TEMP = 10.0  # °C
DEFAULT_MAX_TEMP = 50.0  # °C

ICON_TEMPERATURE = "mdi:thermometer"
ICON_BATTERY = "mdi:battery-50"
ICON_SWITCH = "mdi:power-socket-eu"
ICON_LIGHT = "mdi:lightbulb"
ICON_SHUTTER_CLOSED = "mdi:window-shutter"
ICON_SHUTTER_OPEN = "mdi:window-shutter-open"
ICON_BUTTON = "mdi:button-pointer"
ICON_LIGHT_IN = "mdi:brightness-4"
ICON_HUMIDITY = "mdi:water-percent"
ICON_DEW_POINT = "mdi:tailwind"
ICON_PLUS = "mdi:plus"
ICON_MINUS = "mdi:minus"
ICON_ALERT = "mdi:alert"
ICON_PROXIMITY = "mdi:contactless-payment"
ICON_BINARY_INPUT = "mdi:ab-testing"
ICON_FLASH = "mdi:flash"
ICON_FAN = "mdi:fan"
ICON_HEAT_WAVE = "mdi:heat-wave"
ICON_VALVE = "mdi:valve"

ICON_WATER_HEATER_DICT = {
    "on": "mdi:valve-open",
    "off": "mdi:valve-closed",
}

ICON_RELAY_DICT = {
    "on": "mdi:flash",
    "off": "mdi:flash-outline",
}
ICON_TWOCHANNELDIMMER = "mdi:lightbulb-multiple"
ICON_THERMOSTAT = "mdi:home-thermometer-outline"
ICON_BUTTONARRAY = "mdi:button-pointer"

ICONS = {
    Platform.SWITCH: ICON_SWITCH,
    Platform.SENSOR: ICON_TEMPERATURE,
    Platform.BUTTON: ICON_BUTTON,
    Platform.LIGHT: ICON_LIGHT,
}

MANUAL_SETUP = "manual"

BUTTON_PRESS_STATE = "press"
BUTTON_NO_ACTION_STATE = "no_action"

FAN_SPEED_OPTIONS: list[str] = ["Off", "Speed 1", "Speed 2", "Speed 3"]
FAN_SPEED_DICT = {"Off": 0, "Speed 1": 1, "Speed 2": 2, "Speed 3": 3}

SELECT_OPTIONS_DICT = {
    "fan_speed": FAN_SPEED_OPTIONS,
}

SELECT_OPTIONS_ICON = {"fan_speed": ICON_FAN}

SELECT_DICT = {"fan_speed": FAN_SPEED_DICT}

# DESCRIPTION KEYWORDS
BINARY_INPUT = "binary_input"
INDEXED = "indexed"
NAME = "name"
ICON = "icon"
DEVICE_CLASS = "device_class"
ENTITY_CATEGORY = "entity_category"
OPTIONS = "options"
OPTIONS_DICT = "options_dict"
UNIT = "unit"
OVERFLOW = "overflow"

# BINARY SENSOR PLATFORM
INELS_BINARY_SENSOR_TYPES = {
    "low_battery": {
        BINARY_INPUT: False,
        INDEXED: False,
        NAME: "Battery",
        ICON: ICON_BATTERY,
        DEVICE_CLASS: BinarySensorDeviceClass.BATTERY,
    },
    "prox": {
        BINARY_INPUT: False,
        INDEXED: False,
        NAME: "Proximity Sensor",
        ICON: ICON_PROXIMITY,
        DEVICE_CLASS: BinarySensorDeviceClass.MOVING,
    },
    "input": {
        BINARY_INPUT: True,
        INDEXED: True,
        NAME: "Binary input sensor",
        ICON: ICON_BINARY_INPUT,
        DEVICE_CLASS: None,
    },
    "heating_out": {
        BINARY_INPUT: False,
        INDEXED: False,
        NAME: "Heating output",
        ICON: ICON_HEAT_WAVE,
        DEVICE_CLASS: None,
    },
}

# BUTTON PLATFORM
INELS_BUTTON_TYPES = {
    "btn": {
        NAME: "Button",
        ICON: ICON_BUTTON,
        ENTITY_CATEGORY: EntityCategory.CONFIG,
    },
    "din": {
        NAME: "Digital input",
        ICON: ICON_BUTTON,
        ENTITY_CATEGORY: EntityCategory.CONFIG,
    },
    "sw": {
        NAME: "Switch",
        ICON: ICON_BUTTON,
        ENTITY_CATEGORY: EntityCategory.CONFIG,
    },
    "plus": {
        NAME: "Plus",
        ICON: ICON_PLUS,
        ENTITY_CATEGORY: EntityCategory.CONFIG,
    },
    "minus": {
        NAME: "Minus",
        ICON: ICON_MINUS,
        ENTITY_CATEGORY: EntityCategory.CONFIG,
    },
}

# CLIMATE PLATFORM
INELS_CLIMATE_TYPES = {"climate": {INDEXED: False, NAME: "Thermovalve"}}

# SHUTTERS PLATFORM
INELS_SHUTTERS_TYPES = {"shutters": {NAME: "Shutter"}}

# LIGHT PLATFORM
INELS_LIGHT_TYPES = {
    "out": {ICON: ICON_LIGHT, NAME: "Light"},
    "dali": {ICON: ICON_LIGHT, NAME: "DALI"},
    "aout": {ICON: ICON_FLASH, NAME: "Analog output"},
}

# SELECT PLATFORM
INELS_SELECT_TYPES = {
    "fan_speed": {
        NAME: "Fan speed",
        ICON: ICON_FAN,
        OPTIONS: ["Off", "Speed 1", "Speed 2", "Speed 3"],
        OPTIONS_DICT: {"Off": 0, "Speed 1": 1, "Speed 2": 2, "Speed 3": 3},
    }
}

# SENSOR PLATFORM
INELS_SENSOR_TYPES = {
    TEMP_IN: {
        INDEXED: False,
        NAME: "Internal temperature sensor",
        ICON: ICON_TEMPERATURE,
        UNIT: UnitOfTemperature.CELSIUS,
    },
    TEMP_OUT: {
        INDEXED: False,
        NAME: "External temperature sensor",
        ICON: ICON_TEMPERATURE,
        UNIT: UnitOfTemperature.CELSIUS,
    },
    "light_in": {
        INDEXED: False,
        NAME: "Light intensity",
        ICON: ICON_LIGHT_IN,
        UNIT: LIGHT_LUX,
    },
    "ain": {
        INDEXED: False,
        NAME: "Analog temperature sensor",
        ICON: ICON_TEMPERATURE,
        UNIT: UnitOfTemperature.CELSIUS,
    },
    "humidity": {
        INDEXED: False,
        NAME: "Humidity",
        ICON: ICON_HUMIDITY,
        UNIT: PERCENTAGE,
    },
    "dewpoint": {
        INDEXED: False,
        NAME: "Dew point",
        ICON: ICON_DEW_POINT,
        UNIT: UnitOfTemperature.CELSIUS,
    },
    "temps": {
        INDEXED: True,
        NAME: "Temperature sensor",
        ICON: ICON_TEMPERATURE,
        UNIT: UnitOfTemperature.CELSIUS,
    },
    "ains": {
        INDEXED: True,
        NAME: "Analog input",
        ICON: ICON_FLASH,
        UNIT: UnitOfElectricPotential.VOLT,
    },
}

# SWITCH PLATFORM
INELS_SWITCH_TYPES = {
    "re": {NAME: "Relay", ICON: ICON_SWITCH, OVERFLOW: "relay_overflow"},
    "valve": {NAME: "Valve", ICON: ICON_VALVE, OVERFLOW: None},
}
