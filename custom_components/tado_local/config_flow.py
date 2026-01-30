"""Config flow for Tado Local integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_API_URL,
    CONF_AUTO_START,
    CONF_BRIDGE_IP,
    CONF_PIN,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_BRIDGE_IP): cv.string,
        vol.Optional(CONF_PIN): cv.string,
        vol.Optional(CONF_HOST, default="localhost"): cv.string,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
        vol.Optional(CONF_AUTO_START, default=True): cv.boolean,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    host = data[CONF_HOST]
    port = data[CONF_PORT]
    api_url = f"http://{host}:{port}"
    
    _LOGGER.info("Testing connection to Tado Local at %s", api_url)
    
    # Test the connection - Tado Local has /status and /api endpoints
    try:
        async with aiohttp.ClientSession() as session:
            # Try /status endpoint first
            async with session.get(
                f"{api_url}/status", 
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                _LOGGER.debug("Status response: %s", response.status)
                if response.status not in (200, 503):  # 503 is OK if not fully initialized
                    _LOGGER.error("Unexpected status code: %s", response.status)
                    raise CannotConnect
                
                # Try to read response to confirm it's the right service
                try:
                    data = await response.json()
                    _LOGGER.info("Successfully connected to Tado Local. Status: %s", data.get("status"))
                except Exception as e:
                    _LOGGER.warning("Could not parse status response, but connection OK: %s", e)
                    
    except aiohttp.ClientConnectorError as err:
        _LOGGER.error("Cannot connect to %s: Connection refused or host unreachable", api_url)
        raise CannotConnect from err
    except asyncio.TimeoutError as err:
        _LOGGER.error("Connection to %s timed out", api_url)
        raise CannotConnect from err
    except aiohttp.ClientError as err:
        _LOGGER.error("Cannot connect to Tado Local API at %s: %s", api_url, err)
        raise CannotConnect from err
    except Exception as err:
        _LOGGER.error("Unexpected error connecting to %s: %s", api_url, err)
        raise CannotConnect from err

    # Return info that you want to store in the config entry.
    return {"title": DEFAULT_NAME, "api_url": api_url}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tado Local."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - allow installation without configuration."""
        if user_input is not None:
            # Check if there's already an instance
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()
            
            # Create entry with default/provided values
            host = user_input.get(CONF_HOST, "localhost")
            port = user_input.get(CONF_PORT, DEFAULT_PORT)
            api_url = f"http://{host}:{port}"
            bridge_ip = user_input.get(CONF_BRIDGE_IP)
            pin = user_input.get(CONF_PIN)
            auto_start = user_input.get(CONF_AUTO_START, True)
            
            return self.async_create_entry(
                title=DEFAULT_NAME,
                data={
                    CONF_HOST: host,
                    CONF_PORT: port,
                    CONF_API_URL: api_url,
                    CONF_BRIDGE_IP: bridge_ip,
                    CONF_PIN: pin,
                    CONF_AUTO_START: auto_start,
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            description_placeholders={
                "info": "Konfiguration optional. Bridge IP und PIN werden benötigt um den Server zu starten."
            }
        )
    
    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return TadoLocalOptionsFlow(config_entry)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class TadoLocalOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Tado Local."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            # Update config entry
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data={
                    CONF_HOST: user_input[CONF_HOST],
                    CONF_PORT: user_input[CONF_PORT],
                    CONF_API_URL: f"http://{user_input[CONF_HOST]}:{user_input[CONF_PORT]}",
                    CONF_BRIDGE_IP: user_input.get(CONF_BRIDGE_IP),
                    CONF_PIN: user_input.get(CONF_PIN),
                    CONF_AUTO_START: user_input.get(CONF_AUTO_START, False),
                },
            )
            
            # Reload the integration
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOST,
                        default=self.config_entry.data.get(CONF_HOST, "localhost")
                    ): cv.string,
                    vol.Required(
                        CONF_PORT,
                        default=self.config_entry.data.get(CONF_PORT, DEFAULT_PORT)
                    ): cv.port,
                    vol.Optional(
                        CONF_BRIDGE_IP,
                        default=self.config_entry.data.get(CONF_BRIDGE_IP, "")
                    ): cv.string,
                    vol.Optional(
                        CONF_PIN,
                        default=self.config_entry.data.get(CONF_PIN, "")
                    ): cv.string,
                    vol.Optional(
                        CONF_AUTO_START,
                        default=self.config_entry.data.get(CONF_AUTO_START, False)
                    ): cv.boolean,
                }
            ),
            errors=errors,
            description_placeholders={
                "info": "Server-Verwaltung: Bridge IP, PIN und Auto-Start konfigurieren.",
            }
        )
