"""iNELS light."""
from __future__ import annotations

from typing import Any, cast

from inelsmqtt.devices import Device

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_TRANSITION,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .base_class import InelsBaseEntity
from .const import DEVICES, DOMAIN, ICON_FLASH, ICON_LIGHT, LOGGER


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Load iNELS lights from config entry."""
    device_list: list[Device] = hass.data[DOMAIN][config_entry.entry_id][DEVICES]

    entities: list[InelsBaseEntity] = []
    for device in device_list:
        dev_val = device.get_value()
        if "out" in dev_val.ha_value.__dict__:
            for k in range(len(dev_val.ha_value.out)):
                entities.append(
                    InelsLight(
                        device,
                        key="out",
                        index=k,
                        description=InelsLightDescription(
                            icon=ICON_LIGHT,
                            name="Light",
                        ),
                    )
                )
        if "dali" in dev_val.ha_value.__dict__:
            for k in range(len(dev_val.ha_value.dali)):
                entities.append(
                    InelsLight(
                        device,
                        key="dali",
                        index=k,
                        description=InelsLightDescription(
                            icon=ICON_LIGHT,
                            name="DALI",
                        ),
                    )
                )
        if "aout" in dev_val.ha_value.__dict__:
            for k in range(len(dev_val.ha_value.aout)):
                entities.append(
                    InelsLight(
                        device,
                        key="aout",
                        index=k,
                        description=InelsLightDescription(
                            icon=ICON_FLASH,
                            name="Analog output",
                        ),
                    )
                )

    async_add_entities(entities)


class InelsLightDescription:
    """iNELS light description."""

    def __init__(self, icon: str, name: str) -> None:
        """Initialize description."""
        self.icon = icon
        self.name = name


class InelsLight(InelsBaseEntity, LightEntity):
    """Light class for HA."""

    _entity_description: InelsLightDescription

    def __init__(
        self,
        device: Device,
        key: str,
        index: int,
        description: InelsLightDescription,
    ) -> None:
        """Initialize a light."""
        super().__init__(
            device=device,
            key=key,
            index=index,
        )
        self._entity_description = description

        self._attr_unique_id = f"{self._attr_unique_id}-{description.name}-{self.index}"

        self._attr_name = f"{self._attr_name} {description.name} {self.index + 1}"

        self._attr_supported_color_modes: set[ColorMode] = set()
        self._attr_supported_color_modes.add(ColorMode.BRIGHTNESS)

    @property
    def available(self) -> bool:
        """If it is available."""
        if self.key == "out":
            if "toa" in self._device.state.__dict__:
                if self._device.state.toa[self.index]:
                    LOGGER.warning("Thermal overload on light %s", self.name)
                    return False
            if "coa" in self._device.state.__dict__:
                if self._device.state.coa[self.index]:
                    LOGGER.warning("Current overload on light %s", self.name)
                    return False
        elif self.key == "dali":
            if "alert_dali_power" in self._device.state.__dict__:
                if self._device.state.alert_dali_power:
                    LOGGER.warning("Alert dali power")
                    return False
            if "alert_dali_communication" in self._device.state.__dict__:
                if self._device.state.alert_dali_communication:
                    LOGGER.warning("Alert dali communication")
                    return False

        return super().available

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self._device.state.__dict__[self.key][self.index] > 0

    @property
    def icon(self) -> str | None:
        """Light icon."""
        return self._entity_description.icon

    @property
    def brightness(self) -> int | None:
        """Light brightness."""
        return cast(
            int,
            self._device.state.__dict__[self.key][self.index] * 2.55,
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Light to turn off."""
        if not self._device:
            return

        transition = None
        if ATTR_TRANSITION in kwargs:
            transition = int(kwargs[ATTR_TRANSITION]) / 0.065
            print(transition)
        else:
            # mount device ha value
            ha_val = self._device.get_value().ha_value
            ha_val.__dict__[self.key][self.index] = 0
            await self.hass.async_add_executor_job(self._device.set_ha_value, ha_val)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Light to turn on."""
        if not self._device:
            return

        if ATTR_BRIGHTNESS in kwargs:
            brightness = int(kwargs[ATTR_BRIGHTNESS] / 2.55)
            brightness = min(brightness, 100)

            ha_val = self._device.get_value().ha_value
            ha_val.__dict__[self.key][self.index] = brightness

            await self.hass.async_add_executor_job(self._device.set_ha_value, ha_val)
        else:
            ha_val = self._device.get_value().ha_value

            last_val = self._device.last_values.ha_value

            # uses previously observed value if it isn't 0
            ha_val.__dict__[self.key][self.index] = (
                100
                if last_val.__dict__[self.key][self.index] == 0
                else last_val.__dict__[self.key][self.index]
            )

            await self.hass.async_add_executor_job(self._device.set_ha_value, ha_val)
