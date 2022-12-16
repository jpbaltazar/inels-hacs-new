"""Inels binary sensor entity."""
from __future__ import annotations

from dataclasses import dataclass

from inelsmqtt.devices import Device
from inelsmqtt.const import GSB3_90SX, DA3_22M

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .base_class import InelsBaseEntity
from .const import DEVICES, DOMAIN, ICON_ALERT, ICON_PROXIMITY


@dataclass
class InelsBinarySensorEntityDescriptionMixin:
    """Mixin keys."""


@dataclass
class InelsBinarySensorEntityDescription(
    BinarySensorEntityDescription, InelsBinarySensorEntityDescriptionMixin
):
    """Class for describing binary sensor inels entities."""

    array: bool = None
    var: str = None
    index: int = None


supported = [GSB3_90SX, DA3_22M]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Load iNELS binary sensor."""
    device_list: "list[Device]" = hass.data[DOMAIN][config_entry.entry_id][DEVICES]
    entities: "list[InelsBinarySensor]" = []

    for device in device_list:
        val = device.get_value()
        if device.inels_type in supported:
            if "toa" in val.ha_value.__dict__:
                for k, v in enumerate(val.ha_value.toa):
                    entities.append(
                        InelsBinarySensor(
                            device=device,
                            description=InelsBinarySensorEntityDescription(
                                key=f"{k+1}",
                                name=f"Thermal overload alarm {k+1}",
                                icon=ICON_ALERT,
                                index=k,
                                var="toa",
                                array=True,
                            ),
                        )
                    )
            if "coa" in val.ha_value.__dict__:
                for k, v in enumerate(val.ha_value.coa):
                    entities.append(
                        InelsBinarySensor(
                            device=device,
                            description=InelsBinarySensorEntityDescription(
                                key=f"{k+1}",
                                name=f"Current overload alarm {k+1}",
                                icon=ICON_ALERT,
                                index=k,
                                var="coa",
                                array=True,
                            ),
                        )
                    )
            if "prox" in val.ha_value.__dict__:
                entities.append(
                    InelsBinarySensor(
                        device=device,
                        description=InelsBinarySensorEntityDescription(
                            key=" ",
                            name="Proximity sensor",
                            icon=ICON_PROXIMITY,
                            var="prox",
                            array=False,
                        ),
                    )
                )
    async_add_entities(entities, True)


class InelsBinarySensor(InelsBaseEntity, BinarySensorEntity):
    """The platform class for binary sensors for home assistant"""

    entity_description: InelsBinarySensorEntityDescription

    def __init__(
        self,
        device: Device,
        description: InelsBinarySensorEntityDescription,
    ) -> None:
        """Initialize a binary sensor."""
        super().__init__(device=device)

        self.entity_description = description

        if self.entity_description.array:
            self._attr_unique_id = f"{self._attr_unique_id}-{self.entity_description.var}-{self.entity_description.index}"  # TODO make sure it doesn't need more info
        else:
            self._attr_unique_id = (
                f"{self._attr_unique_id}-{self.entity_description.var}"
            )

        if self.entity_description.array:
            self._attr_name = f"{self._attr_name}-{self.entity_description.name}-{self.entity_description.index}"
        else:
            self._attr_name = f"{self._attr_name}-{self.entity_description.name}"

    # def _callback(self, new_value: Any) -> None:
    #    """Refresh data for device"""
    #    super()._callback(new_value)
    #       self._attr_native_value = self.entity_description.value(self._device)

    @property
    def unique_id(self) -> str | None:
        return super().unique_id

    @property
    def name(self) -> str | None:
        return super().name

    @property
    def is_on(self):
        """Return true is sensor is on"""
        if self.entity_description.array:
            return self._device.values.ha_value.__dict__[self.entity_description.var][
                self.entity_description.index
            ]
        else:
            return self._device.values.ha_value.__dict__[self.entity_description.var]
