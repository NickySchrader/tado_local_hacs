"""Sensor platform for Tado Local integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any
from datetime import timedelta

import aiohttp

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import CONF_API_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=30)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Tado Local sensor entities."""
    api_url = config_entry.data.get(CONF_API_URL, "http://localhost:8000")
    
    # Create coordinator for server status updates
    async def async_update_data():
        """Fetch data from API."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{api_url}/status",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status in (200, 503):
                        return await response.json()
                    return {"status": "error", "error": f"HTTP {response.status}"}
    async_add_entities(entities, True)


class TadoLocalServerStatusSensor(CoordinatorEntity, SensorEntity):
    """Sensor showing Tado Local Server status."""

    _attr_has_entity_name = True
    _attr_name = "Server Status"
    _attr_icon = "mdi:server-network"

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_status"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
        }

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return "Unbekannt"
        
        status = self.coordinator.data.get("status", "unknown")
        
        status_map = {
            "ready": "Online",
            "initializing": "Initialisierung",
            "waiting_for_auth": "Warte auf OAuth",
            "offline": "Offline",
            "timeout": "Timeout",
            "error": "Fehler",
        }
        
        return status_map.get(status, status.title())

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        if not self.coordinator.data:
            return {}
        
        attrs = {
            "api_url": self._config_entry.data.get(CONF_API_URL),
            "raw_status": self.coordinator.data.get("status"),
        }
        
        # Add error if present
        if "error" in self.coordinator.data:
            attrs["error"] = self.coordinator.data["error"]
        
        # Add additional info from status response
        for key in ["bridge_connected", "homekit_paired", "cloud_authenticated"]:
            if key in self.coordinator.data:
                attrs[key] = self.coordinator.data[key]
        
        return attrs


        except aiohttp.ClientConnectorError:
            return {"status": "offline", "error": "Server nicht erreichbar"}
        except asyncio.TimeoutError:
            return {"status": "timeout", "error": "Timeout"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="tado_local_status",
        update_method=async_update_data,
        update_interval=SCAN_INTERVAL,
    )
    
    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()
    
    # Add status sensor
    entities = [
        TadoLocalServerStatusSensor(coordinator, config_entry),
    ]
    
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
