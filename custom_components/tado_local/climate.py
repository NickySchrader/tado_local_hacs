"""Climate platform for Tado Local integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Tado Local climate entities."""
    # TODO: Fetch zones from Tado Local API
    # For now, this is a placeholder
    entities = []
    
    # Example:
    # api_client = hass.data[DOMAIN][config_entry.entry_id]
    # zones = await api_client.get_zones()
    # entities = [TadoLocalClimate(zone) for zone in zones]
    
    async_add_entities(entities, True)


class TadoLocalClimate(ClimateEntity):
    """Representation of a Tado Local climate device."""

    _attr_has_entity_name = True
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_OFF
        | ClimateEntityFeature.TURN_ON
    )
    _attr_hvac_modes = [
        HVACMode.HEAT,
        HVACMode.AUTO,
        HVACMode.OFF,
    ]

    def __init__(self, zone_data: dict[str, Any]) -> None:
        """Initialize the climate device."""
        self._zone_data = zone_data
        self._attr_unique_id = f"tado_local_{zone_data['id']}"
        self._attr_name = zone_data.get("name", "Tado Zone")

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        # TODO: Get from API
        return None

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        # TODO: Get from API
        return None

    @property
    def hvac_mode(self) -> HVACMode:
        """Return hvac operation ie. heat, cool mode."""
        # TODO: Get from API
        return HVACMode.AUTO

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
        
        # TODO: Call API to set temperature
        _LOGGER.debug("Setting temperature to %s", temperature)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        # TODO: Call API to set mode
        _LOGGER.debug("Setting HVAC mode to %s", hvac_mode)
