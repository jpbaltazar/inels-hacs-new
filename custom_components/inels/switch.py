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
from .const import DEVICES, DOMAIN, ICON_SWITCH, LOGGER


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Load iNELS switch.."""
    device_list: list[Device] = hass.data[DOMAIN][config_entry.entry_id][DEVICES]

    entities: list[InelsBaseEntity] = []
    for device in device_list:
        if device.device_type == Platform.SWITCH:
            if hasattr(device.state, "re"):
                if len(device.state.re) == 1:
                    entities.append(
                        InelsBusSwitch(
                            device=device,
                            key="re",
                            index=0,
                            description=InelsSwitchEntityDescription(
                                key="re",
                                name="Relay",
                                icon=ICON_SWITCH,
                            ),
                        )
                    )
                else:
                    for k in range(len(device.state.re)):
                        entities.append(
                            InelsBusSwitch(
                                device=device,
                                key="re",
                                index=k,
                                description=InelsSwitchEntityDescription(
                                    key=f"re{k}",
                                    name=f"Relay {k+1}",
                                    icon=ICON_SWITCH,
                                ),
                            )
                        )
    async_add_entities(entities, False)


@dataclass
class InelsSwitchEntityDescription(SwitchEntityDescription):
    """Class for description inels entities."""


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
        if "relay_overflow" in self._device.state.__dict__:
            if self._device.state.relay_overflow[self.index]:
                LOGGER.warning(
                    "Relay overflow in relay %d of %d",
                    self.entity_description.key,
                    self._device_id,
                )
                return False
            return super().available
        return super().available

    @property
    def is_on(self) -> bool | None:
        """Return if switch is on."""
        state = self._device.state
        return state.re[self.index]

    @property
    def icon(self) -> str | None:
        """Switch icon."""
        return ICON_SWITCH

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the switch to turn off."""
        if not self._device.is_available:
            return None

        ha_val = self._device.state
        ha_val.re[self.index] = False

        await self.hass.async_add_executor_job(self._device.set_ha_value, ha_val)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Instruct the switch to turn on."""
        if not self._device.is_available:
            return None

        ha_val = self._device.state
        ha_val.re[self.index] = True

        await self.hass.async_add_executor_job(self._device.set_ha_value, ha_val)
