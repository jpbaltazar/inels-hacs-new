"""iNELS binary sensor entity."""
from __future__ import annotations

from dataclasses import dataclass

from inelsmqtt.devices import Device

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .base_class import InelsBaseEntity
from .const import (
    DEVICES,
    DOMAIN,
    ICON_BINARY_INPUT,
    ICON_HEAT_WAVE,
    ICON_PROXIMITY,
    ICON_BATTERY,
    LOGGER,
)


@dataclass
class InelsBinarySensorEntityDescriptionMixin:
    """Mixin keys."""


@dataclass
class InelsBinarySensorEntityDescription(
    BinarySensorEntityDescription, InelsBinarySensorEntityDescriptionMixin
):
    """Class for describing binary sensor iNELS entities."""


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Load iNELS binary sensor."""
    device_list: list[Device] = hass.data[DOMAIN][config_entry.entry_id][DEVICES]
    entities: list[InelsBaseEntity] = []

    for device in device_list:
        val = device.get_value()
        if "low_battery" in val.ha_value.__dict__:
            entities.append(
                InelsBinarySensor(
                    device=device,
                    key="low_battery",
                    index=-1,
                    description=InelsBinarySensorEntityDescription(
                        key="low_battery",
                        name="Battery",
                        icon=ICON_BATTERY,
                        device_class=BinarySensorDeviceClass.BATTERY,
                    ),
                )
            )
        if "prox" in val.ha_value.__dict__:
            entities.append(
                InelsBinarySensor(
                    device=device,
                    key="prox",
                    index=-1,
                    description=InelsBinarySensorEntityDescription(
                        key="prox",
                        name="Proximity sensor",
                        icon=ICON_PROXIMITY,
                        device_class=BinarySensorDeviceClass.MOVING,
                    ),
                )
            )
        if "input" in val.ha_value.__dict__:
            for k in range(len(val.ha_value.input)):
                entities.append(
                    InelsBinaryInputSensor(
                        device=device,
                        key="input",
                        index=k,
                        description=InelsBinarySensorEntityDescription(
                            key=f"input{k}",
                            name="Binary input sensor",
                            icon=ICON_BINARY_INPUT,
                        ),
                    )
                )
        if "heating_out" in val.ha_value.__dict__:
            entities.append(
                InelsBinaryInputSensor(
                    device=device,
                    key="heating_out",
                    index=-1,
                    description=InelsBinarySensorEntityDescription(
                        key="heating_out",
                        name="Heating output",
                        icon=ICON_HEAT_WAVE,
                    ),
                )
            )

    async_add_entities(entities, True)


class InelsBinarySensor(InelsBaseEntity, BinarySensorEntity):
    """The platform class for binary sensors for home assistant."""

    entity_description: InelsBinarySensorEntityDescription

    def __init__(
        self,
        device: Device,
        key: str,
        index: int,
        description: InelsBinarySensorEntityDescription,
    ) -> None:
        """Initialize a binary sensor."""
        super().__init__(device=device, key=key, index=index)

        self.entity_description = description

        if self.index is not None:
            self._attr_unique_id = f"{self._attr_unique_id}-{self.key}-{self.index}"
        else:
            self._attr_unique_id = f"{self._attr_unique_id}-{self.key}"

        self._attr_name = f"{self._attr_name} {self.entity_description.name}"

    @property
    def unique_id(self) -> str | None:
        """Return unique_id of the entity."""
        return super().unique_id

    @property
    def name(self) -> str | None:
        """Return name of the entity."""
        return super().name

    @property
    def is_on(self) -> bool | None:
        """Return true is sensor is on."""
        if self.index != -1:
            return self._device.values.ha_value.__dict__[self.key][self.index]

        return self._device.values.ha_value.__dict__[self.key]


class InelsBinaryInputSensor(InelsBaseEntity, BinarySensorEntity):
    """The platform class for binary sensors of binary values for home assistant."""

    entity_description: InelsBinarySensorEntityDescription

    def __init__(
        self,
        device: Device,
        key: str,
        index: int,
        description: InelsBinarySensorEntityDescription,
    ) -> None:
        """Initialize a binary sensor."""
        super().__init__(
            device=device,
            key=key,
            index=index,
        )

        self.entity_description = description

        self._attr_unique_id = f"{self._attr_unique_id}-{self.key}"
        if self.index:
            self._attr_unique_id = f"{self._attr_unique_id}-{self.index}"

        self._attr_name = f"{self._attr_name} {self.entity_description.name}"
        if self.index:
            self._attr_name = f"{self._attr_name} {self.index + 1}"

    @property
    def available(self) -> bool:
        """Return availability of device."""
        val = self._device.values.ha_value.__dict__[self.key][self.index]

        last_val = self._device.last_values.ha_value.__dict__[self.key][self.index]

        if val in [0, 1]:
            return True
        if last_val != val:
            if val == 2:
                LOGGER.warning("%s ALERT", self._attr_unique_id)
            elif val == 3:
                LOGGER.warning("%s TAMPER", self._attr_unique_id)
        return False

    @property
    def unique_id(self) -> str | None:
        """Return unique_id of the entity."""
        return super().unique_id

    @property
    def name(self) -> str | None:
        """Return name of the entity."""
        return super().name

    @property
    def is_on(self) -> bool | None:
        """Return true is sensor is on."""
        if self.index is not None:
            LOGGER.info(self._device.values.ha_value.__dict__[self.key][self.index])
            return self._device.values.ha_value.__dict__[self.key][self.index] == 1
        return self._device.values.ha_value.__dict__[self.key] == 1
