# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-01-02

### Added
- **Global Registry:** Centralized `.env` management across all stacks.
- **Deep Search:** Search engine for stacks, containers, and aliases.
- **Smart URL Discovery:** Automatic link generation for Caddy and Traefik labels.
- **Visibility Toggle:** Ability to hide/unhide specific containers and stacks.
- **System Metrics:** Real-time CPU, RAM, and Temperature monitoring.

### Changed
- **Editor UI:** Variable titles are now case-sensitive to match YAML syntax.
- **Mobile Experience:** Redesigned header and dropdown menus for touch devices.
- **Terminal:** Improved log streaming stability using Xterm.js.

### Security
- Implemented Bcrypt password hashing for master access.
- Added JWT-based session authorization.
