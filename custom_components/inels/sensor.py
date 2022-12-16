"""Inels sensor entity."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from operator import itemgetter
from typing import Any

from inelsmqtt.const import (
    # Data types
    BATTERY,
    TEMP_IN,
    TEMP_OUT,
    RFTI_10B,
    SA3_01B,
    DA3_22M,
    GTR3_50,
)
from inelsmqtt.devices import Device

from inelsmqtt.const import (
    INELS_DEVICE_TYPE_DATA_STRUCT_DATA,
)

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, TEMP_CELSIUS, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .base_class import InelsBaseEntity
from .const import (
    DEVICES,
    DOMAIN,
    ICON_BATTERY,
    ICON_TEMPERATURE,
    ICON_HUMIDITY,
    ICON_DEW_POINT,
    ICON_LIGHT_IN,
)


@dataclass
class InelsSensorEntityDescriptionMixin:
    """Mixin keys."""

    value: Callable[[Device], Any | None]


@dataclass
class InelsSensorEntityDescription(
    SensorEntityDescription, InelsSensorEntityDescriptionMixin
):
    """Class for describing inels entities."""


def _process_data(data: str, indexes: list) -> str:
    """Process data for specific type of measurements."""
    array = data.split("\n")[:-1]
    data_range = itemgetter(*indexes)(array)
    range_joined = "".join(data_range)

    return f"0x{range_joined}"


def _process_value(val: str) -> str:
    middle_fs = True
    for k in val[1:-1]:
        if k.capitalize() != "F":
            middle_fs = False

    if (
        middle_fs
        and val[0] == "7"
        and ((val[-1] <= "F" and val[-1] >= "A") or val[-1] == "9")
    ):
        last = val[-1]
        if last == "9":
            return "Sensor not communicating"
        elif last == "A":
            return "Sensor not calibrated"
        elif last == "B":
            return "No value"
        elif last == "C":
            return "Sensor not configured"
        elif last == "D":
            return "Sensor value out of range"
        elif last == "E":
            return "Sensor measurement error"
        elif last == "F":
            return "No sensor connected"
        else:
            return "ERROR"
    else:
        return f"{float(int(val, 16))/100}"


def __get_battery_level(device: Device) -> int | None:
    """Get battery level of the device."""
    if device.is_available is False:
        return None

    # then get calculate the battery. In our case is 100 or 0
    return (
        100
        if int(
            _process_data(
                device.state,
                INELS_DEVICE_TYPE_DATA_STRUCT_DATA[device.inels_type][BATTERY],
            ),
            16,
        )
        == 0
        else 0
    )


def __get_temperature_in(device: Device) -> float | None:
    """Get temperature inside."""
    if device.is_available is False:
        return None

    return (
        int(
            _process_data(
                device.state,
                INELS_DEVICE_TYPE_DATA_STRUCT_DATA[device.inels_type][TEMP_IN],
            ),
            16,
        )
        / 100
    )


def __get_temperature_out(device: Device) -> float | None:
    """Get temperature outside."""
    if device.is_available is False:
        return None

    return (
        int(
            _process_data(
                device.state,
                INELS_DEVICE_TYPE_DATA_STRUCT_DATA[device.inels_type][TEMP_OUT],
            ),
            16,
        )
        / 100
    )


# BUS


def __get_temperature_bus(device: Device) -> str | None:
    """Get temperature from state field temp_in"""
    if device.is_available is False:
        return None

    return _process_value(device.state.temp_in)


def __get_light_in_bus(device: Device) -> str | None:
    if device.is_available is False:
        return None

    return _process_value(device.state.light_in)


def __get_analog_temperature_bus(device: Device) -> str | None:
    if device.is_available is False:
        return None
    return _process_value(device.state.ain)


def __get_humidity_bus(device: Device) -> str | None:
    if device.is_available is False:
        return None

    return _process_value(device.state.humidity)


def __get_dew_point_bus(device: Device) -> str | None:
    if device.is_available is False:
        return None

    return _process_value(device.state.dewpoint)


# RFTI_10B

SENSOR_DESCRIPTION_TEMPERATURE: "tuple[InelsSensorEntityDescription, ...]" = (
    InelsSensorEntityDescription(
        key="battery_level",
        name="Battery",
        device_class=SensorDeviceClass.BATTERY,
        icon=ICON_BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        value=__get_battery_level,
    ),
    InelsSensorEntityDescription(
        key="temp_in",
        name="Temperature In",
        device_class=SensorDeviceClass.TEMPERATURE,
        icon=ICON_TEMPERATURE,
        native_unit_of_measurement=TEMP_CELSIUS,
        value=__get_temperature_in,
    ),
    InelsSensorEntityDescription(
        key="temp_out",
        name="Temperature Out",
        device_class=SensorDeviceClass.TEMPERATURE,
        icon=ICON_TEMPERATURE,
        native_unit_of_measurement=TEMP_CELSIUS,
        value=__get_temperature_out,
    ),
)

# SA3_01B
# DA3_22M
SENSOR_DESCRIPTION_TEMPERATURE_GENERIC: "tuple[InelsSensorEntityDescription, ...]" = (
    InelsSensorEntityDescription(
        key="temp_in",
        name="Temperature",
        # device_class=SensorDeviceClass.TEMPERATURE,
        icon=ICON_TEMPERATURE,
        native_unit_of_measurement=TEMP_CELSIUS,
        value=__get_temperature_bus,
    ),
)

# GTR3_50
# GSB3_90SX
SENSOR_DESCRIPTION_MULTISENSOR: "tuple[InelsSensorEntityDescription, ...]" = (
    InelsSensorEntityDescription(
        key="temp_in",
        name="Temperature",
        # device_class=SensorDeviceClass.TEMPERATURE,
        icon=ICON_TEMPERATURE,
        native_unit_of_measurement=TEMP_CELSIUS,
        value=__get_temperature_bus,
    ),
    InelsSensorEntityDescription(
        key="light_in",
        name="Light intensity",
        # device_class=SensorDeviceClass.ILLUMINANCE,
        icon=ICON_LIGHT_IN,
        native_unit_of_measurement="lux",
        value=__get_light_in_bus,
    ),
    InelsSensorEntityDescription(
        key="ain",
        name="Analog temperature",
        # device_class=SensorDeviceClass.TEMPERATURE,
        icon=ICON_TEMPERATURE,
        native_unit_of_measurement=TEMP_CELSIUS,
        value=__get_analog_temperature_bus,
    ),
    InelsSensorEntityDescription(
        key="humidity",
        name="Humidity",
        # device_class=SensorDeviceClass.HUMIDITY,
        icon=ICON_HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        value=__get_humidity_bus,
    ),
    InelsSensorEntityDescription(
        key="dewpoint",
        name="Dew point",
        # device_class=SensorDeviceClass.TEMPERATURE,
        icon=ICON_DEW_POINT,
        native_unit_of_measurement=TEMP_CELSIUS,
        value=__get_dew_point_bus,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Load Inels switch.."""
    device_list: "list[Device]" = hass.data[DOMAIN][config_entry.entry_id][DEVICES]

    entities: "list[InelsSensor]" = []

    for device in device_list:
        if device.device_type == Platform.SENSOR:
            if device.inels_type == RFTI_10B:
                descriptions = SENSOR_DESCRIPTION_TEMPERATURE

                for description in descriptions:
                    entities.append(InelsSensor(device, description=description))
            elif device.inels_type == GTR3_50:
                descriptions = SENSOR_DESCRIPTION_MULTISENSOR
                for description in descriptions:
                    entities.append(
                        InelsSensor(
                            device,
                            description=description,
                        )
                    )
            else:
                continue
        elif device.device_type == Platform.LIGHT:
            if device.inels_type == DA3_22M:
                descriptions = SENSOR_DESCRIPTION_TEMPERATURE_GENERIC
                for description in descriptions:
                    entities.append(InelsSensor(device, description=description))
        elif device.device_type == Platform.SWITCH:
            if device.inels_type == SA3_01B:
                descriptions = SENSOR_DESCRIPTION_TEMPERATURE_GENERIC
                for description in descriptions:
                    entities.append(InelsSensor(device, description=description))

    async_add_entities(entities, True)


class InelsSensor(InelsBaseEntity, SensorEntity):
    """The platform class required by Home Assistant."""

    entity_description: InelsSensorEntityDescription

    def __init__(
        self,
        device: Device,
        description: InelsSensorEntityDescription,
    ) -> None:
        """Initialize a sensor."""
        super().__init__(device=device)

        self.entity_description = description
        self._attr_unique_id = f"{self._attr_unique_id}-{description.key}"

        if description.name:
            self._attr_name = f"{self._attr_name}-{description.name}"

        self._attr_native_value = self.entity_description.value(self._device)

    def _callback(self, new_value: Any) -> None:
        """Refresh data."""
        super()._callback(new_value)
        self._attr_native_value = self.entity_description.value(self._device)
