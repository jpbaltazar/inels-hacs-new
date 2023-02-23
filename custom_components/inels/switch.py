"""iNELS switch entity."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from inelsmqtt.devices import Device

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .base_class import InelsBaseEntity
from .const import (
    DEVICES,
    DOMAIN,
    ICON,
    INELS_SWITCH_TYPES,
    LOGGER,
    NAME,
    OVERFLOW,
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Load iNELS switch.."""
    device_list: list[Device] = hass.data[DOMAIN][config_entry.entry_id][DEVICES]
    items = INELS_SWITCH_TYPES.items()

    entities: list[InelsBaseEntity] = []
    for device in device_list:
        for key, type_dict in items:
            if hasattr(device.state, key):
                if len(device.state.__dict__[key]) == 1:
                    entities.append(
                        InelsBusSwitch(
                            device=device,
                            key=key,
                            index=0,
                            description=InelsSwitchEntityDescription(
                                key=key,
                                name=type_dict[NAME],
                                icon=type_dict[ICON],
                                overload_key=type_dict[OVERFLOW],
                            ),
                        )
                    )
                else:
                    for k in range(len(device.state.__dict__[key])):
                        entities.append(
                            InelsBusSwitch(
                                device=device,
                                key=key,
                                index=k,
                                description=InelsSwitchEntityDescription(
                                    key=f"{key}{k}",
                                    name=f"{type_dict[NAME]} {k+1}",
                                    icon=type_dict[ICON],
                                    overload_key=type_dict[OVERFLOW],
                                ),
                            )
                        )
    async_add_entities(entities, False)


@dataclass
class InelsSwitchEntityDescription(SwitchEntityDescription):
    """Class for description inels entities."""

    overload_key: str | None = None


class InelsBusSwitch(InelsBaseEntity, SwitchEntity):
    """The platform class required by Home Assistant, bus version."""

    entity_description: InelsSwitchEntityDescription

    def __init__(
        self,
        device: Device,
        key: str,
        index: int,
        description: InelsSwitchEntityDescription,
    ) -> None:
        """Initialize a bus switch."""
        super().__init__(device=device, key=key, index=index)

        self.entity_description = description

        self._attr_unique_id = f"{self._attr_unique_id}-{description.key}"
        self._attr_name = f"{self._attr_name} {description.name}"

    @property
    def available(self) -> bool:
        """Return entity availability."""
        if self.entity_description.overload_key is not None:
            if hasattr(self._device.state, self.entity_description.overload_key):
                if self._device.state.relay_overflow[self.index]:
                    LOGGER.warning(
                        "Relay overflow in %s of %d",
                        self.name,
                        self._device_id,
                    )
                    return False
        return super().available

    @property
    def is_on(self) -> bool | None:
        """Return if switch is on."""
        state = self._device.state
        return state.__dict__[self.key][self.index]

    @property
    def icon(self) -> str | None:
        """Switch icon."""
        return self.entity_description.icon

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the switch to turn off."""
        if not self._device.is_available:
            return None

        ha_val = self._device.state
        ha_val.__dict__[self.key][self.index] = False

        await self.hass.async_add_executor_job(self._device.set_ha_value, ha_val)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Instruct the switch to turn on."""
        if not self._device.is_available:
            return None

        ha_val = self._device.state
        ha_val.__dict__[self.key][self.index] = True

        await self.hass.async_add_executor_job(self._device.set_ha_value, ha_val)
