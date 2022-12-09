"""iNels light."""
from __future__ import annotations
from typing import Any, cast

from inelsmqtt.const import RFDAC_71B, DA3_22M  # HERE ?
from inelsmqtt.devices import Device
from inelsmqtt.util import new_object

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_TRANSITION,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from homeassistant.core import logging

from .base_class import InelsBaseEntity
from .const import DEVICES, DOMAIN, ICON_LIGHT, LOGGER

from .coordinator import InelsDeviceUpdateCoordinator2


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Load Inels lights from config entry."""
    device_list: "list[Device]" = hass.data[DOMAIN][config_entry.entry_id][DEVICES]

    entities = []

    for device in device_list:
        if device.device_type == Platform.LIGHT:
            # entities.append(InelsLight(device))
            if device.inels_type == DA3_22M:
                entities.append(
                    InelsLightChannel(
                        device, description=InelsLightChannelDescription(2, 0)
                    )
                )
                entities.append(
                    InelsLightChannel(
                        device, description=InelsLightChannelDescription(2, 1)
                    )
                )

                # COORDINATOR version
                # coordinator = InelsDeviceUpdateCoordinator2(hass=hass, device=device)

                # entities.append(
                #    InelsLightChannel2(
                #        device=device,
                #        coordinator=coordinator,
                #        description=InelsLightChannelDescription(2, 0),
                #    )
                # )
                # entities.append(
                #    InelsLightChannel2(
                #        device=device,
                #        coordinator=coordinator,
                #        description=InelsLightChannelDescription(2, 1),
                #    )
                # )
            else:
                entities.append(InelsLight(device))

    async_add_entities(entities)


class InelsLight(InelsBaseEntity, LightEntity):
    """Light class for HA."""

    def __init__(self, device: Device) -> None:
        """Initialize a light."""
        super().__init__(device=device)

        self._attr_supported_color_modes: set[ColorMode] = set()
        if self._device.inels_type is RFDAC_71B:
            self._attr_supported_color_modes.add(ColorMode.BRIGHTNESS)

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self._device.state > 0

    @property
    def icon(self) -> str | None:
        """Light icon."""
        return ICON_LIGHT

    @property
    def brightness(self) -> int | None:
        """Light brightness."""
        if self._device.inels_type is not RFDAC_71B:
            return None
        return cast(int, self._device.state * 2.55)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Light to turn off."""
        if not self._device:
            return

        transition = None

        if ATTR_TRANSITION in kwargs:
            transition = int(kwargs[ATTR_TRANSITION]) / 0.065
            print(transition)
        else:
            await self.hass.async_add_executor_job(self._device.set_ha_value, 0)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Light to turn on."""
        if not self._device:
            return

        if ATTR_BRIGHTNESS in kwargs:
            brightness = int(kwargs[ATTR_BRIGHTNESS] / 2.55)
            brightness = min(brightness, 100)

            await self.hass.async_add_executor_job(
                self._device.set_ha_value, brightness
            )
        else:
            await self.hass.async_add_executor_job(self._device.set_ha_value, 100)


class InelsLightChannelDescription:
    """Inels light channel description."""

    def __init__(self, channel_number: int, channel_index: int):
        self.channel_number = channel_number
        self.channel_index = channel_index


class InelsLightChannel(InelsBaseEntity, LightEntity):
    """Light Channel class for HA."""

    _entity_description: InelsLightChannelDescription

    def __init__(
        self, device: Device, description: InelsLightChannelDescription
    ) -> None:
        """Initialize a light."""
        super().__init__(device=device)
        self._entity_description = description

        self._attr_unique_id = f"{self._attr_unique_id}-{description.channel_index}"
        self._attr_name = f"{self._attr_name}-{description.channel_index}"

        self._attr_supported_color_modes: set[ColorMode] = set()
        if self._device.inels_type is DA3_22M:
            self._attr_supported_color_modes.add(ColorMode.BRIGHTNESS)

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self._device.state.out[self._entity_description.channel_index] > 0

    @property
    def icon(self) -> str | None:
        """Light icon."""
        return ICON_LIGHT

    @property
    def brightness(self) -> int | None:
        """Light brightness."""
        if self._device.inels_type is not DA3_22M:
            return None
        # return cast(int, self._device.get_value().out[self.entity_description.channel_index])
        return cast(
            int, self._device.state.out[self._entity_description.channel_index] * 2.55
        )

    # async def async_update(self):
    #    """Update state."""
    #    self.state = self._device.get_value().ha_value

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
            ha_val.out[self._entity_description.channel_index] = 0
            await self.hass.async_add_executor_job(self._device.set_ha_value, ha_val)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Light to turn on"""
        if not self._device:
            return

        if ATTR_BRIGHTNESS in kwargs:
            brightness = int(kwargs[ATTR_BRIGHTNESS] / 2.55)
            brightness = min(brightness, 100)

            ha_val = self._device.get_value().ha_value
            ha_val.out[self._entity_description.channel_index] = brightness

            await self.hass.async_add_executor_job(self._device.set_ha_value, ha_val)
        else:
            ha_val = self._device.get_value().ha_value
            ha_val.out[self._entity_description.channel_index] = 100

            await self.hass.async_add_executor_job(self._device.set_ha_value, ha_val)


class CoordinatorEntityInheritance(CoordinatorEntity):
    def __init__(self, coordinator, **kw):
        super(CoordinatorEntityInheritance, self).__init__(coordinator)


class InelsBaseEntityInheritance(InelsBaseEntity):
    def __init__(self, device, **kw):
        super(InelsBaseEntityInheritance, self).__init__(device)


class InelsLightChannel2(
    InelsBaseEntityInheritance, CoordinatorEntityInheritance, LightEntity
):
    """Light Channel class for HA. Uses CoordinatorEntity."""

    _entity_description: InelsLightChannelDescription
    coordinator: InelsDeviceUpdateCoordinator2

    def __init__(
        self,
        device: Device,
        description: InelsLightChannelDescription,
        coordinator: InelsDeviceUpdateCoordinator2,
        **kw,
    ) -> None:
        """Initialize a light."""
        super(InelsLightChannel2, self).__init__(device=device, coordinator=coordinator)

        self.coordinator = coordinator
        self._entity_description = description

        self._attr_unique_id = f"{self._attr_unique_id}-{description.channel_index}"
        self._attr_name = f"{self._attr_name}-{description.channel_index}"

        self._attr_supported_color_modes: set[ColorMode] = set()
        if self._device.inels_type is DA3_22M:
            self._attr_supported_color_modes.add(ColorMode.BRIGHTNESS)

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return (
            self.coordinator.device.state.out[self._entity_description.channel_index]
            > 0
        )
        # return self._device.state.out[self._entity_description.channel_index] > 0

    @property
    def icon(self) -> str | None:
        """Light icon."""
        return ICON_LIGHT

    @property
    def brightness(self) -> int | None:
        """Light brightness."""
        if self._device.inels_type is not DA3_22M:
            return None
        # return cast(int, self._device.get_value().out[self.entity_description.channel_index])
        return cast(
            int,
            # self._device.state.out[self._entity_description.channel_index] * 2.55
            self.coordinator.device.state.out[self._entity_description.channel_index]
            * 2.55,
        )

    # async def async_update(self):
    #    """Update state."""
    #    self.state = self._device.get_value().ha_value

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        super()._handle_coordinator_update()
        self._device.get_value()
        self.async_write_ha_state()

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
            # ha_val = self._device.get_value().ha_value
            ha_val = self.coordinator.device.get_value().ha_value
            ha_val.out[self._entity_description.channel_index] = 0
            # await self.hass.async_add_executor_job(self._device.set_ha_value, ha_val)
            await self.hass.async_add_executor_job(
                self.coordinator.device.set_ha_value, ha_val
            )

        LOGGER.warning(
            "Light %d/%d turned off (%s)",
            self._entity_description.channel_index,
            self._entity_description.channel_number,
            # self.coordinator.device.__state.out[self._entity_description.channel_index],
            f"{self.coordinator.device.get_value().inels_value}",
        )

        await self.coordinator.async_request_refresh()

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Light to turn on"""
        if not self._device:
            return

        if ATTR_BRIGHTNESS in kwargs:
            brightness = int(kwargs[ATTR_BRIGHTNESS] / 2.55)
            brightness = min(brightness, 100)

            # ha_val = self._device.get_value().ha_value
            # ha_val.out[self._entity_description.channel_index] = brightness

            # await self.hass.async_add_executor_job(self._device.set_ha_value, ha_val)

            ha_val = self.coordinator.device.get_value().ha_value
            ha_val.out[self._entity_description.channel_index] = brightness
            await self.hass.async_add_executor_job(
                self.coordinator.device.set_ha_value, ha_val
            )

        else:
            # ha_val = self._device.get_value().ha_value
            # ha_val.out[self._entity_description.channel_index] = 100

            # await self.hass.async_add_executor_job(self._device.set_ha_value, ha_val)

            ha_val = self.coordinator.device.get_value().ha_value
            ha_val.out[self._entity_description.channel_index] = 100
            await self.hass.async_add_executor_job(
                self.coordinator.device.set_ha_value, ha_val
            )

        LOGGER.warning(
            "Light %d/%d turned on (%s)",
            self._entity_description.channel_index,
            self._entity_description.channel_number,
            # self.coordinator.device.__state.out[self._entity_description.channel_index],
            f"{self.coordinator.device.get_value().inels_value}",
        )

        await self.coordinator.async_request_refresh()
