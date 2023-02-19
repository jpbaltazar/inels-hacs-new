"""iNELS cover entity."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from inelsmqtt.const import Shutter_state
from inelsmqtt.devices import Device

from homeassistant.components.cover import (
    CoverDeviceClass,
    CoverEntity,
    CoverEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .base_class import InelsBaseEntity
from .const import DEVICES, DOMAIN, ICON_SHUTTER_CLOSED, ICON_SHUTTER_OPEN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Load iNELS cover from config entry."""
    device_list: list[Device] = hass.data[DOMAIN][config_entry.entry_id][DEVICES]

    entities: list[InelsBaseEntity] = []
    for device in device_list:
        if hasattr(device.state, "shutters"):
            if len(device.state.shutters) == 1:
                entities.append(
                    InelsCover(
                        device=device,
                        key="shutters",
                        index=0,
                        description=InelsCoverEntityDescription(
                            key="shutter",
                            name="Shutter",
                        ),
                    )
                )
            else:
                for k in range(len(device.state.shutters)):
                    entities.append(
                        InelsCover(
                            device=device,
                            key="shutters",
                            index=k,
                            description=InelsCoverEntityDescription(
                                key=f"shutter{k}", name=f"Shutter {k+1}"
                            ),
                        )
                    )

    async_add_entities(entities, False)


@dataclass
class InelsCoverEntityDescription(CoverEntityDescription):
    """Class for description inels entities."""

    name: str = ""


class InelsCover(InelsBaseEntity, CoverEntity):
    """Cover class for Home Assistant."""

    entity_description: InelsCoverEntityDescription

    def __init__(
        self,
        device: Device,
        key: str,
        index: int,
        description: InelsCoverEntityDescription,
    ) -> None:
        super().__init__(device=device, key=key, index=index)
        self.entity_description = description

        self._attr_device_class = CoverDeviceClass.SHUTTER

        self._attr_unique_id = f"{self._attr_unique_id}-{description.key}"
        self._attr_name = f"{self._attr_name} {description.name}"

    @property
    def icon(self) -> str | None:
        """Cover icon."""
        return ICON_SHUTTER_CLOSED if self.is_closed is True else ICON_SHUTTER_OPEN

    @property
    def is_closed(self) -> bool | None:
        """Cover is closed."""
        is_closed = (
            self._device.state.__dict__[self.key][self.index] == Shutter_state.Closed
        )
        return is_closed

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Open cover."""
        ha_val = self._device.state
        ha_val.__dict__[self.key][self.index] = Shutter_state.Open
        await self.hass.async_add_executor_job(self._device.set_ha_value, ha_val)

    async def async_close_cover(self, **kwargs) -> None:
        """Close cover."""
        ha_val = self._device.state
        ha_val.__dict__[self.key][self.index] = Shutter_state.Closed
        await self.hass.async_add_executor_job(self._device.set_ha_value, ha_val)

    async def async_stop_cover(self, **kwargs: Any) -> None:
        """Stop cover."""
        ha_val = self._device.state
        ha_val.__dict__[self.key][self.index] = (
            Shutter_state.Stop_up if self.is_closed else Shutter_state.Stop_down
        )
        await self.hass.async_add_executor_job(self._device.set_ha_value, ha_val)
