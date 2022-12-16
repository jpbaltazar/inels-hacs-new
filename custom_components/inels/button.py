"""Support for iNELS buttons."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from inelsmqtt.devices import Device
from inelsmqtt.const import GTR3_50

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
from .const import DEVICES, DOMAIN, ICON_BUTTON, ICON_PLUS, ICON_MINUS


@dataclass
class InelsButtonDescription(ButtonEntityDescription):
    """A class that describes button entity."""

    var: str = None  # sw, din...
    index: int = None  # 1, 2, 3, 4...


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Load Inels buttons from config entry."""
    device_list: "list[Device]" = hass.data[DOMAIN][config_entry.entry_id][DEVICES]

    entities = []

    for device in device_list:
        if device.device_type == Platform.SENSOR:
            if device.inels_type == GTR3_50:  # 2 DIN, 5 SW
                val = device.get_value()
                if "din" in val.ha_value.__dict__:
                    for k, v in enumerate(val.ha_value.din):
                        entities.append(
                            InelsBusButton(
                                device=device,
                                description=InelsButtonDescription(
                                    key=f"{k+1}",  # starts counting at 1
                                    name=f"DIN {k+1}",
                                    icon=ICON_BUTTON,
                                    entity_category=EntityCategory.CONFIG,
                                    # only if needed
                                    var="din",
                                    index=k,
                                ),
                            )
                        )
                if "sw" in val.ha_value.__dict__:
                    for k, v in enumerate(val.ha_value.sw):
                        entities.append(
                            InelsBusButton(
                                device=device,
                                description=InelsButtonDescription(
                                    key=f"{k+1}",  # starts counting at 1
                                    name=f"SW {k+1}",
                                    icon=ICON_BUTTON,
                                    entity_category=EntityCategory.CONFIG,
                                    # only if needed
                                    var="sw",
                                    index=k,
                                ),
                            )
                        )
                if "plusminus" in val.ha_value.__dict__:
                    for k, v in enumerate(val.ha_value.plusminus):
                        entities.append(
                            InelsBusButton(
                                device=device,
                                description=InelsButtonDescription(
                                    key=f"{k+1}",  # starts counting at 1
                                    name="Plus" if k == 0 else "Minus",
                                    icon=ICON_PLUS if k == 0 else ICON_MINUS,
                                    entity_category=EntityCategory.CONFIG,
                                    # only if needed
                                    var="plusminus",
                                    index=k,
                                ),
                            )
                        )
        elif device.device_type == Platform.BUTTON:
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

        if (
            self._device.values.ha_value.pressing
            and self._device.values.ha_value.number == int(self.entity_description.key)
            # the original implementation didn't have to worry about this ^ because
            # the callbacks all went to the last entity added for the device
        ):
            self.hass.services.call(
                Platform.BUTTON,
                SERVICE_PRESS,
                {ATTR_ENTITY_ID: entity_id},
                True,
                self._context,
            )

    def press(self) -> None:
        """Press the button."""


class InelsBusButton(InelsBaseEntity, ButtonEntity):
    """Button switch that can be toggled by MQTT. Specific version for Bus devices."""

    entity_description: InelsButtonDescription
    _attr_device_class: ButtonDeviceClass = None

    def __init__(self, device: Device, description: InelsButtonDescription) -> None:
        """Initialize button"""
        super().__init__(device=device)
        self.entity_description = description

        self._attr_unique_id = f"{self._attr_unique_id}-{description.name}"

        if description.name:
            self._attr_name = f"{self._attr_name}-{description.name}"

    def _callback(self, new_value: Any) -> None:
        super()._callback(new_value)
        key_index = int(self.entity_description.key)

        entity_id = f"{Platform.BUTTON}.{self._device_id}_{self.entity_description.var}_{key_index}"

        curr_val = self._device.values.ha_value
        last_val = self._device.last_values.ha_value
        if (
            curr_val.__dict__[self.entity_description.var][
                self.entity_description.index
            ]  # is on
            and not last_val.__dict__[self.entity_description.var][
                self.entity_description.index
            ]  # was off
            # on press
        ):
            self.hass.services.call(
                Platform.BUTTON,
                SERVICE_PRESS,
                {ATTR_ENTITY_ID: entity_id},
                True,
                self._context,
            )

    def press(self) -> None:
        """Press the button."""
