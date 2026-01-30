"""Tado Local integration for Home Assistant."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr

from .const import CONF_API_URL, CONF_AUTO_START, CONF_BRIDGE_IP, CONF_PIN, DOMAIN
from .server_manager import TadoLocalServerManager

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.CLIMATE,
    Platform.SENSOR,
]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up the Tado Local component."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Tado Local from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    Initialize server manager
    server_config = {
        "bridge_ip": entry.data.get(CONF_BRIDGE_IP),
        "pin": entry.data.get(CONF_PIN),
        "port": entry.data.get(CONF_PORT, 8000),
    }
    
    server_manager = TadoLocalServerManager(hass, server_config)
    
    # Auto-start server if configured
    if entry.data.get(CONF_AUTO_START, False):
        if server_config["bridge_ip"] and server_config["pin"]:
            _LOGGER.info("Auto-starting Tado Local server")
            await server_manager.start_server()
        else:
            _LOGGER.warning("Auto-start enabled but Bridge IP or PIN not configured")
    
    # Store config data and server manager
    hass.data[DOMAIN][entry.entry_id] = {
        "config": entry.data,
        "server_manager": server_manager,
    }
    
    # Register device
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.entry_id)},
        name="Tado Local Server",
        manufacturer="Community",
        model="Tado Local Bridge",
        sw_version="0.0.3",
        configuration_url=entry.data.get(CONF_API_URL, f"http://localhost:8000"),
    )
    
    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Register services
    async def start_server_service(call: ServiceCall) -> None:
        """Start the Tado Local server."""
        success = await server_manager.start_server()
        if success:
            _LOGGER.info("Tado Local server started")
        else:
            _LOGGER.error("Failed to start Tado Local server")
    # Stop server if running
    if entry.entry_id in hass.data.get(DOMAIN, {}):
        server_manager = hass.data[DOMAIN][entry.entry_id].get("server_manager")
        if server_manager:
            await server_manager.stop_server()
    
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    # Unregister services if this was the last entry
    if not hass.data[DOMAIN]:
        hass.services.async_remove(DOMAIN, "start_server")
        hass.services.async_remove(DOMAIN, "stop_server")
        hass.services.async_remove(DOMAIN, "restart_server")ocal server."""
        success = await server_manager.restart_server()
        if success:
            _LOGGER.info("Tado Local server restarted")
        else:
            _LOGGER.error("Failed to restart Tado Local server")
    
    async def check_server_status(call: ServiceCall) -> None:
        """Check if Tado Local server is reachable."""
        api_url = entry.data.get(CONF_API_URL, "http://localhost:8000")
        is_running = server_manager.is_running()
        
        _LOGGER.info("Server process running: %s", is_running)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{api_url}/status",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status in (200, 503):
                        status_data = await response.json()
                        _LOGGER.info("Tado Local Server Status: %s", status_data)
                    else:
                        _LOGGER.error("Server returned status %s", response.status)
        except Exception as e:
            _LOGGER.error("Cannot reach Tado Local server: %s", e)
    
    hass.services.async_register(DOMAIN, "start_server", start_server_service)
    hass.services.async_register(DOMAIN, "stop_server", stop_server_service)
    hass.services.async_register(DOMAIN, "restart_server", restart_server_service)        _LOGGER.error("Cannot reach Tado Local server: %s", e)
    
    hass.services.async_register(DOMAIN, "check_server", check_server_status)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    # Unregister services if this was the last entry
    if not hass.data[DOMAIN]:
        hass.services.async_remove(DOMAIN, "check_server")
    
    return unload_ok
