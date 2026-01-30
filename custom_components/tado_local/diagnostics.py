"""Diagnostics support for Tado Local."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_HOST, CONF_PORT

from .const import CONF_API_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    
    host = entry.data.get(CONF_HOST, "nicht konfiguriert")
    port = entry.data.get(CONF_PORT, "nicht konfiguriert")
    api_url = entry.data.get(CONF_API_URL, "nicht konfiguriert")
    
    diagnostics_data = {
        "config": {
            "host": host,
            "port": port,
            "api_url": api_url,
        },
        "server_status": {
            "reachable": False,
            "status": "Nicht erreichbar",
            "error": None,
        },
        "server_info": {},
        "api_endpoints": {
            "status": f"{api_url}/status",
            "api": f"{api_url}/api",
            "docs": f"{api_url}/docs",
            "accessories": f"{api_url}/accessories",
        }
    }
    
    # Try to get server status
    try:
        async with aiohttp.ClientSession() as session:
            # Get status
            try:
                async with session.get(
                    f"{api_url}/status",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status in (200, 503):
                        diagnostics_data["server_status"]["reachable"] = True
                        try:
                            status_data = await response.json()
                            diagnostics_data["server_status"]["status"] = status_data.get("status", "unknown")
                            diagnostics_data["server_info"]["status_response"] = status_data
                        except Exception as e:
                            diagnostics_data["server_status"]["error"] = f"JSON parse error: {str(e)}"
                    else:
                        diagnostics_data["server_status"]["error"] = f"HTTP {response.status}"
            except aiohttp.ClientConnectorError:
                diagnostics_data["server_status"]["error"] = "Verbindung fehlgeschlagen - Server läuft nicht"
            except asyncio.TimeoutError:
                diagnostics_data["server_status"]["error"] = "Timeout - Server antwortet nicht"
            except Exception as e:
                diagnostics_data["server_status"]["error"] = f"Unerwarteter Fehler: {str(e)}"
            
            # Try to get API info
            if diagnostics_data["server_status"]["reachable"]:
                try:
                    async with session.get(
                        f"{api_url}/api",
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        if response.status == 200:
                            api_data = await response.json()
                            diagnostics_data["server_info"]["api_response"] = api_data
                except Exception as e:
                    _LOGGER.debug("Could not fetch /api endpoint: %s", e)
                
                # Try to get accessories
                try:
                    async with session.get(
                        f"{api_url}/accessories",
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        if response.status == 200:
                            accessories = await response.json()
                            diagnostics_data["server_info"]["accessories_count"] = len(accessories) if isinstance(accessories, list) else 0
                except Exception as e:
                    _LOGGER.debug("Could not fetch /accessories endpoint: %s", e)
                    
    except Exception as e:
        diagnostics_data["server_status"]["error"] = f"Diagnose fehlgeschlagen: {str(e)}"
        _LOGGER.exception("Diagnostics failed")
    
    return diagnostics_data
