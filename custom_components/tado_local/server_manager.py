"""Tado Local Server Manager."""
from __future__ import annotations

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Any

_LOGGER = logging.getLogger(__name__)


class TadoLocalServerManager:
    """Manage the Tado Local server process."""

    def __init__(self, hass, config: dict[str, Any]) -> None:
        """Initialize the server manager."""
        self.hass = hass
        self.config = config
        self.process: asyncio.subprocess.Process | None = None
        self._stopping = False

    async def start_server(self) -> bool:
        """Start the Tado Local server."""
        if self.process and self.process.returncode is None:
            _LOGGER.info("Server already running")
            return True

        bridge_ip = self.config.get("bridge_ip")
        pin = self.config.get("pin")
        port = self.config.get("port", 8000)

        if not bridge_ip or not pin:
            _LOGGER.error("Bridge IP and PIN required to start server")
            return False

        # Find the tado_local module path
        integration_path = Path(__file__).parent.parent.parent
        tado_local_path = integration_path / "tado_local"
        
        if not tado_local_path.exists():
            _LOGGER.error("tado_local module not found at %s", tado_local_path)
            return False

        # Build command
        cmd = [
            sys.executable,
            "-m",
            "tado_local",
            "--bridge-ip", bridge_ip,
            "--pin", pin,
            "--port", str(port),
        ]

        _LOGGER.info("Starting Tado Local server: %s", " ".join(cmd[2:]))

        try:
            # Set PYTHONPATH to include the integration directory
            env = os.environ.copy()
            env["PYTHONPATH"] = str(integration_path) + ":" + env.get("PYTHONPATH", "")
            
            self.process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
            )

            # Start log readers
            asyncio.create_task(self._read_logs())

            # Wait a bit to see if it starts successfully
            await asyncio.sleep(2)

            if self.process.returncode is not None:
                _LOGGER.error("Server failed to start, exit code: %s", self.process.returncode)
                return False

            _LOGGER.info("Tado Local server started successfully on port %s", port)
            return True

        except Exception as e:
            _LOGGER.exception("Failed to start server: %s", e)
            return False

    async def stop_server(self) -> None:
        """Stop the Tado Local server."""
        if not self.process or self.process.returncode is not None:
            _LOGGER.debug("Server not running")
            return

        self._stopping = True
        _LOGGER.info("Stopping Tado Local server")

        try:
            self.process.terminate()
            try:
                await asyncio.wait_for(self.process.wait(), timeout=10)
            except asyncio.TimeoutError:
                _LOGGER.warning("Server did not stop gracefully, killing")
                self.process.kill()
                await self.process.wait()

            _LOGGER.info("Tado Local server stopped")

        except Exception as e:
            _LOGGER.exception("Error stopping server: %s", e)
        finally:
            self.process = None
            self._stopping = False

    async def restart_server(self) -> bool:
        """Restart the server."""
        await self.stop_server()
        await asyncio.sleep(1)
        return await self.start_server()

    def is_running(self) -> bool:
        """Check if server is running."""
        return self.process is not None and self.process.returncode is None

    async def _read_logs(self) -> None:
        """Read and log server output."""
        if not self.process:
            return

        async def read_stream(stream, level):
            while True:
                try:
                    line = await stream.readline()
                    if not line:
                        break
                    text = line.decode().strip()
                    if text:
                        _LOGGER.log(level, "Tado Local Server: %s", text)
                except Exception:
                    break

        await asyncio.gather(
            read_stream(self.process.stdout, logging.INFO),
            read_stream(self.process.stderr, logging.WARNING),
            return_exceptions=True,
        )
