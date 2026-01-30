"""Config flow for Tado Local integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
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


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tado Local."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            # Check if already configured
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()
            
            # Get values with defaults
            host = user_input.get(CONF_HOST, "localhost")
            port = user_input.get(CONF_PORT, DEFAULT_PORT)
            bridge_ip = user_input.get(CONF_BRIDGE_IP, "")
            pin = user_input.get(CONF_PIN, "")
            auto_start = user_input.get(CONF_AUTO_START, False)
            
            return self.async_create_entry(
                title=DEFAULT_NAME,
                data={
                    CONF_HOST: host,
                    CONF_PORT: port,
                    CONF_API_URL: f"http://{host}:{port}",
                    CONF_BRIDGE_IP: bridge_ip if bridge_ip else None,
                    CONF_PIN: pin if pin else None,
                    CONF_AUTO_START: auto_start,
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_BRIDGE_IP, default=""): cv.string,
                    vol.Optional(CONF_PIN, default=""): cv.string,
                    vol.Optional(CONF_HOST, default="localhost"): cv.string,
                    vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
                    vol.Optional(CONF_AUTO_START, default=False): cv.boolean,
                }
            ),
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OptionsFlowHandler:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Tado Local."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            # Update config entry
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data={
                    CONF_HOST: user_input[CONF_HOST],
                    CONF_PORT: user_input[CONF_PORT],
                    CONF_API_URL: f"http://{user_input[CONF_HOST]}:{user_input[CONF_PORT]}",
                    CONF_BRIDGE_IP: user_input.get(CONF_BRIDGE_IP) or None,
                    CONF_PIN: user_input.get(CONF_PIN) or None,
                    CONF_AUTO_START: user_input.get(CONF_AUTO_START, False),
                },
            )
            
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOST,
                        default=self.config_entry.data.get(CONF_HOST, "localhost"),
                    ): cv.string,
                    vol.Required(
                        CONF_PORT,
                        default=self.config_entry.data.get(CONF_PORT, DEFAULT_PORT),
                    ): cv.port,
                    vol.Optional(
                        CONF_BRIDGE_IP,
                        default=self.config_entry.data.get(CONF_BRIDGE_IP, ""),
                    ): cv.string,
                    vol.Optional(
                        CONF_PIN,
                        default=self.config_entry.data.get(CONF_PIN, ""),
                    ): cv.string,
                    vol.Optional(
                        CONF_AUTO_START,
                        default=self.config_entry.data.get(CONF_AUTO_START, False),
                    ): cv.boolean,
                }
            ),
        )
