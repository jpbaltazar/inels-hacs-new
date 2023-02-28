"""iNELS binary sensor entity."""
from __future__ import annotations

from dataclasses import dataclass

from inelsmqtt.devices import Device

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .base_class import InelsBaseEntity
from .const import (
    BINARY_INPUT,
    DEVICE_CLASS,
    DEVICES,
    DOMAIN,
    ICON,
    INELS_BINARY_SENSOR_TYPES,
    LOGGER,
    INDEXED,
    NAME,
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

    items = INELS_BINARY_SENSOR_TYPES.items()

    for device in device_list:
        for key, type_dict in items:
            if hasattr(device.state, key):
                if type_dict[BINARY_INPUT]:
                    binary_sensor_type = InelsBinaryInputSensor
                else:
                    binary_sensor_type = InelsBinarySensor

                if not type_dict[INDEXED]:
                    entities.append(
                        binary_sensor_type(
                            device=device,
                            key=key,
                            index=-1,
                            description=InelsBinarySensorEntityDescription(
                                key=key,
                                name=type_dict[NAME],
                                icon=type_dict[ICON],
                                device_class=type_dict[DEVICE_CLASS],
                            ),
                        )
                    )
                else:
                    for k in range(len(device.state.__dict__[key])):
                        entities.append(
                            binary_sensor_type(
                                device=device,
                                key=key,
                                index=k,
                                description=InelsBinarySensorEntityDescription(
                                    key=f"{key}{k}",
                                    name=f"{type_dict[NAME]} {k+1}",
                                    icon=type_dict[ICON],
                                    device_class=type_dict[DEVICE_CLASS],
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

        self._attr_unique_id = f"{self._attr_unique_id}-{self.entity_description.key}"
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

        self._attr_unique_id = f"{self._attr_unique_id}-{self.entity_description.key}"
        self._attr_name = f"{self._attr_name} {self.entity_description.name}"

    @property
    def available(self) -> bool:
        """Return availability of device."""

        val = self._device.values.ha_value.__dict__[self.key]
        last_val = self._device.last_values.ha_value.__dict__[self.key]
        if self.index != -1:
            val = val[self.index]
            last_val = last_val[self.index]

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
        if self.index != -1:
            LOGGER.info(self._device.values.ha_value.__dict__[self.key][self.index])
            return self._device.values.ha_value.__dict__[self.key][self.index] == 1
        return self._device.values.ha_value.__dict__[self.key] == 1
