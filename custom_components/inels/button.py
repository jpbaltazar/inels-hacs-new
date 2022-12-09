"""Support for iNELS buttons."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from inelsmqtt.devices import Device

from homeassistant.components.button import (
    SERVICE_PRESS,
    ButtonDeviceClass,
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ENTITY_ID, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .base_class import InelsBaseEntity
from .const import DEVICES, DOMAIN, ICON_BUTTON


@dataclass
class InelsButtonDescription(ButtonEntityDescription):
    """A class that describes button entity."""


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Load Inels water heater from config entry."""
    device_list: "list[Device]" = hass.data[DOMAIN][config_entry.entry_id][DEVICES]

    entities = []

    for device in device_list:
        if device.device_type == Platform.BUTTON:
            index = 1
            val = device.get_value()
            if val.ha_value is not None:
                while index <= val.ha_value.amount:
                    entities.append(
                        InelsButton(
                            device=device,
                            description=InelsButtonDescription(
                                key=f"{index}",
                                name=f"btn {index}",
                                icon=ICON_BUTTON,
                                entity_category=EntityCategory.CONFIG,
                            ),
                        )
                    )
                    index += 1

    async_add_entities(entities)


class InelsButton(InelsBaseEntity, ButtonEntity):
    """Button switch can be toggled using with MQTT."""

    entity_description: InelsButtonDescription
    _attr_device_class: ButtonDeviceClass = None  # ButtonDeviceClass.RESTART

    def __init__(self, device: Device, description: InelsButtonDescription) -> None:
        """Initialize a button."""
        super().__init__(device=device)
        self.entity_description = description

        self._attr_unique_id = f"{self._attr_unique_id}-{description.key}"

        if description.name:
            self._attr_name = f"{self._attr_name}-{description.name}"

    def _callback(self, new_value: Any) -> None:
        super()._callback(new_value)
        # self.__process_state()
        entity_id = f"{Platform.BUTTON}.{self._device_id}_btn_{self._device.values.ha_value.number}"

        if self._device.values.ha_value.pressing:
            self.hass.services.call(
                Platform.BUTTON,
                SERVICE_PRESS,
                {ATTR_ENTITY_ID: entity_id},
                True,
                self._context,
            )

    def press(self) -> None:
        """Press the button."""