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
from .const import DEVICES, DOMAIN, ICON_BUTTON, ICON_MINUS, ICON_PLUS


@dataclass
class InelsButtonDescription(ButtonEntityDescription):
    """A class that describes button entity."""


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Load iNELS buttons from config entry."""
    device_list: list[Device] = hass.data[DOMAIN][config_entry.entry_id][DEVICES]

    entities: list[InelsBaseEntity] = []

    for device in device_list:
        val = device.get_value()
        if hasattr(val.ha_value, "btn"):
            for k in range(len(val.ha_value.btn)):
                entities.append(
                    InelsButton(
                        device=device,
                        key="btn",
                        index=k,
                        description=InelsButtonDescription(
                            key=f"btn{k+1}",
                            name=f"Button {k+1}",
                            icon=ICON_BUTTON,
                            entity_category=EntityCategory.CONFIG,
                        ),
                    )
                )
        if hasattr(val.ha_value, "din"):
            for k in range(len(val.ha_value.din)):
                entities.append(
                    InelsButton(
                        device=device,
                        key="din",
                        index=k,
                        description=InelsButtonDescription(
                            key=f"din{k+1}",
                            name=f"Digital input {k+1}",
                            icon=ICON_BUTTON,
                            entity_category=EntityCategory.CONFIG,
                        ),
                    )
                )
        if hasattr(val.ha_value, "sw"):
            for k in range(len(val.ha_value.sw)):
                entities.append(
                    InelsButton(
                        device=device,
                        key="sw",
                        index=k,
                        description=InelsButtonDescription(
                            key=f"sw{k+1}",
                            name=f"Switch {k+1}",
                            icon=ICON_BUTTON,
                            entity_category=EntityCategory.CONFIG,
                        ),
                    )
                )
        if hasattr(val.ha_value, "plusminus"):
            for k in range(len(val.ha_value.plusminus)):
                entities.append(
                    InelsButton(
                        device=device,
                        key="plusminus",
                        index=k,
                        description=InelsButtonDescription(
                            key=f"plusminus{k+1}",
                            name="Plus" if k == 0 else "Minus",
                            icon=ICON_PLUS if k == 0 else ICON_MINUS,
                            entity_category=EntityCategory.CONFIG,
                        ),
                    )
                )

    async_add_entities(entities)


class InelsButton(InelsBaseEntity, ButtonEntity):
    """Button switch that can be toggled by MQTT. Specific version for Bus devices."""

    entity_description: InelsButtonDescription
    _attr_device_class: ButtonDeviceClass | None = None

    def __init__(
        self, device: Device, key: str, index: int, description: InelsButtonDescription
    ) -> None:
        """Initialize button."""
        super().__init__(device=device, key=key, index=index)
        self.entity_description = description

        self._attr_unique_id = f"{self._attr_unique_id}-{description.name}"

        if description.name:
            self._attr_name = f"{self._attr_name} {description.name}"

    def _callback(self, new_value: Any) -> None:
        super()._callback(new_value)
        key_index = int(self.entity_description.key)
        if self.entity_description.name:
            if self.key != "plusminus":
                entity_id = f"{Platform.BUTTON}.{self._device_id}_{self.entity_description.name.lower().replace(' ', '_')}"
            else:
                name = "plus" if key_index == 1 else "minus"
                entity_id = f"{Platform.BUTTON}.{self._device_id}_{name}"
        else:
            entity_id = f"{Platform.BUTTON}.{self._device_id}_{self.key}_{self.index}"

        curr_val = self._device.state
        last_val = self._device.last_values.ha_value

        if (
            curr_val.__dict__[self.key][self.index]
            and not last_val.__dict__[self.key][self.index]
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
