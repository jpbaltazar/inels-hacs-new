"""Inels selector entity."""
from __future__ import annotations

from dataclasses import dataclass

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
    SELECT_DICT,
)


@dataclass
class InelsSelectEntityDescriptionMixin:
    """Mixin keys."""


@dataclass
class InelsSelectEntityDescription(
    SelectEntityDescription, InelsSelectEntityDescriptionMixin
):
    """Class for describing the inels select entities"""

    var: str = None
    index: int = None


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Load iNELS select entity."""
    device_list: "list[Device]" = hass.data[DOMAIN][config_entry.entry_id][DEVICES]
    entities: "list[InelsSelect]" = []

    for device in device_list:
        val = device.get_value()
        if "fan_speed" in val.ha_value.__dict__:
            entities.append(
                InelsSelect(
                    device,
                    InelsSelectEntityDescription(
                        key="fan_speed",
                        name="Fan speed",
                        var="fan_speed",
                    ),
                )
            )


class InelsSelect(InelsBaseEntity, SelectEntity):
    """The platform class for select for home assistant"""

    entity_description: InelsSelectEntityDescription = None

    def __init__(
        self, device: Device, description: InelsSelectEntityDescription
    ) -> None:
        """Initialize a select entity."""
        super().__init__(device=device)
        self.entity_description = description

    @property
    def unique_id(self) -> str | None:
        return super().unique_id

    @property
    def name(self) -> str | None:
        return super().name

    @property
    def current_option(self) -> str | None:
        state = self._device.state
        if "index" in self.entity_description.__dict__:
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

        if "RF" not in self._device.inels_type:
            if str(self.entity_description.var) in SELECT_DICT:
                dict = SELECT_DICT[self.entity_description.var]
                if option in dict:
                    val = dict[option]
                    if "index" in self.entity_description.__dict__:
                        if option in dict:
                            self._device.state.__dict__[self.entity_description.var][
                                self.entity_description.index
                            ] = val
                    else:
                        if option in dict:
                            self._device.state.__dict__[
                                self.entity_description.var
                            ] = dict[option] = val
