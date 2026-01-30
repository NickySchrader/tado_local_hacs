# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.6] - 2026-01-30

### Fixed
- Fixed hacs.json configuration for proper version detection in HACS
- Removed unnecessary fields that prevented version updates from showing

## [0.0.5] - 2026-01-30

### Fixed

- Fixed async_get_options_flow type annotation for better compatibility
- Improved config flow handler initialization

## [0.0.4] - 2026-01-30

### Fixed

- Fixed missing asyncio import in diagnostics.py causing "Invalid handler specified" error
- Fixed config flow loading issue

## [0.0.3] - 2026-01-30

### Added

- **Integrated Server Management**: Integration can now start and manage the Tado Local server
- Server auto-start option during installation
- Bridge IP and PIN configuration in config flow
- Server control services: start_server, stop_server, restart_server
- Live server status sensor with automatic updates every 30 seconds
- Server logs are now visible in Home Assistant logs

### Changed

- Config flow now accepts Bridge IP and PIN for server management
- Options flow extended with Bridge configuration and auto-start toggle
- Improved server status monitoring with detailed attributes

### Notes

- Server auto-start requires Bridge IP and HomeKit PIN
- Server runs as subprocess managed by Home Assistant
- All server output is logged to Home Assistant logs

## [0.0.2] - 2026-01-30

### Changed

- Installation now possible without configuration input
- Configuration can be done via Options after installation
- Improved config flow with better error messages and logging

### Added

- Options flow for post-installation configuration
- Diagnostics support with detailed server status
- Device registration with configuration URL
- Service for checking server status

## [0.0.1] - 2026-01-30

### Added

- Initial HACS release
- Home Assistant integration with config flow
- Climate platform support for zone control
- Sensor platform for temperature and humidity
- German and English translations
- Basic connection validation

### Notes

- This is an alpha release
- Requires Tado Local server running separately
- Full API integration to be completed in future releases
