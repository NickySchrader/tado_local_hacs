"""Sensor platform for Tado Local integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Tado Local sensor entities."""
    # TODO: Fetch sensor data from Tado Local API
    # For now, this is a placeholder
    entities = []
    
    # Example:
    # api_client = hass.data[DOMAIN][config_entry.entry_id]
    # zones = await api_client.get_zones()
    # for zone in zones:
    #     entities.append(TadoLocalTemperatureSensor(zone))
    #     entities.append(TadoLocalHumiditySensor(zone))
    
    async_add_entities(entities, True)


class TadoLocalTemperatureSensor(SensorEntity):
    """Representation of a Tado Local temperature sensor."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, zone_data: dict[str, Any]) -> None:
        """Initialize the sensor."""
        self._zone_data = zone_data
        self._attr_unique_id = f"tado_local_temp_{zone_data['id']}"
        self._attr_name = f"{zone_data.get('name', 'Zone')} Temperature"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        # TODO: Get from API
        return None


class TadoLocalHumiditySensor(SensorEntity):
    """Representation of a Tado Local humidity sensor."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, zone_data: dict[str, Any]) -> None:
        """Initialize the sensor."""
        self._zone_data = zone_data
        self._attr_unique_id = f"tado_local_humidity_{zone_data['id']}"
        self._attr_name = f"{zone_data.get('name', 'Zone')} Humidity"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        # TODO: Get from API
        return None
