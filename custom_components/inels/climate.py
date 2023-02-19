"""iNELS climate entity."""
from __future__ import annotations

from dataclasses import dataclass

from inelsmqtt.devices import Device

from homeassistant.components.climate import (
    STATE_OFF,
    STATE_ON,
    ClimateEntity,
    ClimateEntityDescription,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, Platform, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .base_class import InelsBaseEntity
from .const import DEFAULT_MAX_TEMP, DEFAULT_MIN_TEMP, DEVICES, DOMAIN

OPERATION_LIST = [
    STATE_OFF,
    STATE_ON,
]

SUPPORT_FLAGS_CLIMATE = ClimateEntityFeature.TARGET_TEMPERATURE


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Load iNELS water heater from config entry."""
    device_list: list[Device] = hass.data[DOMAIN][config_entry.entry_id][DEVICES]

    entities: list[InelsBaseEntity] = []

    for device in device_list:
        val = device.get_value()
        if hasattr(val.ha_value, "climate"):
            entities.append(
                InelsClimate(
                    device=device,
                    key="climate",
                    index=-1,
                    description=InelsClimateDescription(
                        key="climate", name="Thermovalve"
                    ),
                )
            )

    async_add_entities(
        [
            # InelsClimate(device)
            InelsClimate(
                device=device,
                key="climate",
                index=-1,
                description=InelsClimateDescription(key="climate", name="Thermovalve"),
            )
            for device in device_list
            if device.device_type == Platform.CLIMATE
        ],
    )


@dataclass
class InelsClimateDescription(ClimateEntityDescription):
    """Inels Climate entity description class"""

    name: str = "Climate"


class InelsClimate(InelsBaseEntity, ClimateEntity):
    """Inels Climate entity for HA."""

    _attr_supported_features: ClimateEntityFeature = SUPPORT_FLAGS_CLIMATE
    _attr_hvac_modes: list[HVACMode] = [HVACMode.OFF, HVACMode.HEAT]
    _attr_temperature_unit: str = UnitOfTemperature.CELSIUS
    _attr_hvac_mode: HVACMode = HVACMode.HEAT  # OFF

    entity_description: InelsClimateDescription

    def __init__(
        self, device: Device, key: str, index: int, description: InelsClimateDescription
    ) -> None:
        """Initialize a climate entity."""
        super().__init__(device=device, key=key, index=index)

        self._attr_max_temp = DEFAULT_MAX_TEMP
        self._attr_min_temp = DEFAULT_MIN_TEMP

        self._attr_unique_id = f"{self._attr_unique_id}-{self.key}"
        self._attr_name = f"{self._attr_name} {description.name}"

    @property
    def current_temperature(self) -> float | None:
        """Get current temperature."""
        if self._device.state is not None:
            if self.index == -1:
                return self._device.state.__dict__[self.key].current
            return self._device.state.__dict__[self.key][self.index].current

        return super().current_temperature

    @property
    def target_temperature(self) -> float | None:
        """Get target temperature."""
        if self._device.state is not None:
            if self.index == -1:
                return self._device.state.__dict__[self.key].required
            return self._device.state.__dict__[self.key][self.index].required

        return super().current_temperature

    @property
    def hvac_mode(self) -> HVACMode | str | None:
        if self.index == -1:
            val = self._device.state.__dict__[self.key]
        else:
            val = self._device.state.__dict__[self.key][self.index]

        if val.current < val.required:
            return HVACMode.HEAT
        return HVACMode.OFF

    async def async_set_temperature(self, **kwargs) -> None:
        """Set the required temperature."""
        ha_val = self._device.state

        if self.index == -1:
            ha_val.__dict__[self.key].required = kwargs.get(ATTR_TEMPERATURE)
        else:
            ha_val.__dict__[self.key][self.index].required = kwargs.get(
                ATTR_TEMPERATURE
            )

        await self.hass.async_add_executor_job(self._device.set_ha_value, ha_val)
