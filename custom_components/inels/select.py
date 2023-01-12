"""Inels selector entity."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


from inelsmqtt.devices import Device
from inelsmqtt.const import (
    FA3_612M,
)

from homeassistant.components.select import (
    SelectEntity,
    SelectEntityDescription,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .base_class import InelsBaseEntity
from .const import (
    DEVICES,
    DOMAIN,
    SELECT_OPTIONS_DICT,
    SELECT_OPTIONS_ICON,
    FAN_SPEED_DICT,
)


@dataclass
class InelsSelectEntityDescriptionMixin:
    """Mixin keys."""


@dataclass
class InelsSelectEntityDescription(
    SelectEntityDescription, InelsSelectEntityDescriptionMixin
):
    """Class for describing the inels select entities"""

    index: int = None
    var: str = None
    value: Callable[[Device, str], Any | None] = None


def __set_fan_speed(device: Device, option: str) -> Any | None:
    """Process option value and set fan speed"""
    ha_val = device.state

    if option in FAN_SPEED_DICT:
        ha_val.fan_speed = FAN_SPEED_DICT[option]

    return ha_val


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Load iNELS select entity."""
    device_list: "list[Device]" = hass.data[DOMAIN][config_entry.entry_id][DEVICES]
    entities: "list[InelsSelect]" = []

    for device in device_list:
        if device.inels_type is FA3_612M:
            val = device.get_value()
            if "fan_speed" in val.ha_value.__dict__:
                entities.append(
                    InelsSelect(
                        device,
                        InelsSelectEntityDescription(
                            key="fan_speed",
                            var="fan_speed",
                            name="Fan speed",
                            value=__set_fan_speed,
                        ),
                    )
                )
    async_add_entities(entities, True)


class InelsSelect(InelsBaseEntity, SelectEntity):
    """The platform class for select for home assistant"""

    entity_description: InelsSelectEntityDescription = None

    def __init__(
        self, device: Device, description: InelsSelectEntityDescription
    ) -> None:
        """Initialize a select entity."""
        super().__init__(device=device)
        self.entity_description = description

        if self.entity_description.index is not None:
            self._attr_unique_id = f"{self._attr_unique_id}-{self.entity_description.var}-{self.entity_description.index}"
            self._attr_name = f"{self._attr_name} {self.entity_description.name} {self.entity_description.index + 1}"
        else:
            self._attr_unique_id = (
                f"{self._attr_unique_id}-{self.entity_description.var}"
            )
            self._attr_name = f"{self._attr_name} {self.entity_description.name}"

    @property
    def unique_id(self) -> str | None:
        return super().unique_id

    @property
    def name(self) -> str | None:
        return super().name

    @property
    def icon(self) -> str | None:
        if self.entity_description.var in SELECT_OPTIONS_ICON:
            return SELECT_OPTIONS_ICON[self.entity_description.var]
        else:
            return super().icon

    @property
    def current_option(self) -> str | None:
        state = self._device.state
        if self.entity_description.index is not None:
            return SELECT_OPTIONS_DICT[self.entity_description.var][
                state.__dict__[self.entity_description.var][
                    self.entity_description.index
                ]
            ]
        else:
            return SELECT_OPTIONS_DICT[self.entity_description.var][
                state.__dict__[self.entity_description.var]
            ]

    @property
    def options(self) -> list[str]:
        if str(self.entity_description.var) in SELECT_OPTIONS_DICT:
            return SELECT_OPTIONS_DICT[self.entity_description.var]
        else:
            return []

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        new_ha_val = self.entity_description.value(self._device, option)

        self.hass.async_add_executor_job(self._device.set_ha_value, new_ha_val)
