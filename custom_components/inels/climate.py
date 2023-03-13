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
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import InelsBaseEntity
from .const import (
    DEFAULT_MAX_TEMP,
    DEFAULT_MIN_TEMP,
    DEVICES,
    DOMAIN,
)

OPERATION_LIST = [
    STATE_OFF,
    STATE_ON,
]

SUPPORT_FLAGS_CLIMATE = ClimateEntityFeature.TARGET_TEMPERATURE

# CLIMATE PLATFORM
@dataclass
class InelsClimateType:
    """Climate type property description"""

    name: str


INELS_CLIMATE_TYPES: dict[str, InelsClimateType] = {
    "climate": InelsClimateType(name="Thermovalve")
}

# INELS_CLIMATE_TYPES = {"climate": {INDEXED: False, NAME: "Thermovalve"}}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Load iNELS water heater from config entry."""
    device_list: list[Device] = hass.data[DOMAIN][config_entry.entry_id][DEVICES]
    entities: list[InelsBaseEntity] = []

    items = INELS_CLIMATE_TYPES.items()

    for device in device_list:
        for key, type_dict in items:
            if hasattr(device.state, key):
                entities.append(
                    InelsClimate(
                        device=device,
                        key=key,
                        index=-1,
                        description=InelsClimateDescription(
                            key=key, name=type_dict.name
                        ),
                    )
                )

    async_add_entities(entities)


@dataclass
class InelsClimateDescription(ClimateEntityDescription):
    """Inels Climate entity description class"""

    name: str = "Climate"


class InelsClimate(InelsBaseEntity, ClimateEntity):
    """Inels Climate entity for HA."""

    _attr_supported_features: ClimateEntityFeature = SUPPORT_FLAGS_CLIMATE
    _attr_hvac_modes: list[HVACMode] = [HVACMode.OFF, HVACMode.HEAT]
    _attr_temperature_unit: str = UnitOfTemperature.CELSIUS

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
        return self._device.state.__dict__[self.key].current

    @property
    def target_temperature(self) -> float | None:
        """Get target temperature."""
        return self._device.state.__dict__[self.key].required

    @property
    def hvac_mode(self) -> HVACMode | str | None:
        val = self._device.state.__dict__[self.key]

        if val.current < val.required:
            return HVACMode.HEAT
        return HVACMode.OFF

    async def async_set_temperature(self, **kwargs) -> None:
        """Set the required temperature."""
        ha_val = self._device.state
        ha_val.__dict__[self.key].required = kwargs.get(ATTR_TEMPERATURE)

        await self.hass.async_add_executor_job(self._device.set_ha_value, ha_val)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        if self.hvac_mode != hvac_mode:
            ha_val = self._device.state
            if hvac_mode == HVACMode.OFF:
                ha_val.__dict__[self.key].required = 0
            elif hvac_mode == HVACMode.HEAT:
                ha_val.__dict__[self.key].required = (
                    ha_val.__dict__[self.key].current + 2
                )

            return await self.hass.async_add_executor_job(
                self._device.set_ha_value, ha_val
            )
        return None
