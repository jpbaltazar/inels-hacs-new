"""iNELS sensor entity."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from inelsmqtt.const import (  # Data types
    BATTERY,
    TEMP_IN,
    TEMP_OUT,
    BUS_SENSOR_ERRORS,
)
from inelsmqtt.devices import Device

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    LIGHT_LUX,
    PERCENTAGE,
    UnitOfElectricPotential,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .base_class import InelsBaseEntity
from .const import (
    DEVICES,
    DOMAIN,
    ICON_BATTERY,
    ICON_DEW_POINT,
    ICON_FLASH,
    ICON_HUMIDITY,
    ICON_LIGHT_IN,
    ICON_TEMPERATURE,
    LOGGER,
)


@dataclass
class InelsSensorDescriptionMixin:
    """Mixin keys."""


@dataclass
class InelsSensorDescription(SensorEntityDescription, InelsSensorDescriptionMixin):
    """Class for describing iNELS entities."""


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
        if last == "A":
            return "Sensor not calibrated"
        if last == "B":
            return "No value"
        if last == "C":
            return "Sensor not configured"
        if last == "D":
            return "Sensor value out of range"
        if last == "E":
            return "Sensor measurement error"
        if last == "F":
            return "No sensor connected"
        return "ERROR"

    return f"{float(int(val, 16))/100}"


def _process_value_2(val: str) -> tuple[str, bool]:
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
        last = int(last, 16)
        error = BUS_SENSOR_ERRORS.get(last)
        if error is not None:
            LOGGER.warning(error)
            return (float(int(val, 16)) / 100, True)

    return (float(int(val, 16)) / 100, False)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Load iNELS switch.."""
    device_list: list[Device] = hass.data[DOMAIN][config_entry.entry_id][DEVICES]

    entities: list[InelsBaseEntity] = []

    for device in device_list:
        val = device.get_value()
        if BATTERY in val.ha_value.__dict__:
            entities.append(
                InelsSensor(
                    device,
                    key="battery",
                    index=-1,
                    description=InelsSensorDescription(
                        key="battery",
                        name="Battery",
                        icon=ICON_BATTERY,
                        native_unit_of_measurement=PERCENTAGE,
                    ),
                )
            )
        if TEMP_IN in val.ha_value.__dict__:
            entities.append(
                InelsSensor(
                    device,
                    key="temp_in",
                    index=-1,
                    description=InelsSensorDescription(
                        key="temp_in",
                        name="Internal temperature sensor",
                        icon=ICON_TEMPERATURE,
                        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
                    ),
                )
            )
        if TEMP_OUT in val.ha_value.__dict__:
            entities.append(
                InelsSensor(
                    device,
                    key="temp_out",
                    index=-1,
                    description=InelsSensorDescription(
                        key="temp_out",
                        name="External temperature sensor",
                        icon=ICON_TEMPERATURE,
                        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
                    ),
                )
            )
        if "light_in" in val.ha_value.__dict__:
            entities.append(
                InelsSensor(
                    device,
                    key="light_in",
                    index=-1,
                    description=InelsSensorDescription(
                        key="light_in",
                        name="Light intensity",
                        icon=ICON_LIGHT_IN,
                        native_unit_of_measurement=LIGHT_LUX,
                    ),
                )
            )
        if "ain" in val.ha_value.__dict__:
            entities.append(
                InelsSensor(
                    device,
                    key="ain",
                    index=-1,
                    description=InelsSensorDescription(
                        key="ain",
                        name="Analog temperature",
                        icon=ICON_TEMPERATURE,
                        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
                    ),
                )
            )
        if "humidity" in val.ha_value.__dict__:
            entities.append(
                InelsSensor(
                    device,
                    key="humidity",
                    index=-1,
                    description=InelsSensorDescription(
                        key="humidity",
                        name="Humidity",
                        icon=ICON_HUMIDITY,
                        native_unit_of_measurement=PERCENTAGE,
                    ),
                )
            )
        if "dewpoint" in val.ha_value.__dict__:
            entities.append(
                InelsSensor(
                    device,
                    key="dewpoint",
                    index=-1,
                    description=InelsSensorDescription(
                        key="dewpoint",
                        name="Dew point",
                        icon=ICON_DEW_POINT,
                        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
                    ),
                )
            )
        if "temps" in val.ha_value.__dict__:
            for k in range(len(val.ha_value.temps)):
                entities.append(
                    InelsSensor(
                        device,
                        key="temps",
                        index=k,
                        description=InelsSensorDescription(
                            key=f"temp{k}",
                            name="Temperature",
                            icon=ICON_TEMPERATURE,
                            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
                        ),
                    )
                )
        if "ains" in val.ha_value.__dict__:
            for k in range(len(val.ha_value.ains)):
                entities.append(
                    InelsSensor(
                        device,
                        key="ains",
                        index=k,
                        description=InelsSensorDescription(
                            key=f"ain{k}",
                            name="Analog input",
                            icon=ICON_FLASH,
                            native_unit_of_measurement=UnitOfElectricPotential.VOLT,
                        ),
                    )
                )
    async_add_entities(entities, True)


class InelsSensor(InelsBaseEntity, SensorEntity):
    """Platform class for Home assistant, bus version."""

    entity_description: InelsSensorDescription
    sensor_error: bool = False

    def __init__(
        self,
        device: Device,
        key: str,
        index: int,
        description: InelsSensorDescription,
    ) -> None:
        """Initialize bus sensor."""
        super().__init__(device=device, key=key, index=index)

        self.entity_description = description
        self._attr_unique_id = f"{self._attr_unique_id}-{description.key}"
        if self.index != -1:
            self._attr_unique_id += f"-{self.index}"

        if description.name:
            self._attr_name = f"{self._attr_name} {description.name}"
            if self.index != -1:
                self._attr_name += f" {self.index + 1}"

        if self.index != -1:  # with index
            val = self._device.state.__dict__[self.key][self.index]
        else:
            val = self._device.state.__dict__[self.key]

        if isinstance(val, str):
            # val = _process_value(val)
            val, self.sensor_error = _process_value_2(val)

        self._attr_native_value = val

    def _callback(self, new_value: Any) -> None:
        """Refresh data."""
        super()._callback(new_value)

        if self.index != -1:  # with index
            val = self._device.state.__dict__[self.key][self.index]
        else:
            val = self._device.state.__dict__[self.key]

        if isinstance(val, str):
            # val = _process_value(val)
            val, self.sensor_error = _process_value_2(val)

        self._attr_native_value = val

    @property
    def available(self) -> bool:
        return not self.sensor_error and super().available
