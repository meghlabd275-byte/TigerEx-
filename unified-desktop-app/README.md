# TigerEx Unified Desktop Application

## Overview
Consolidated desktop application combining the best features from all TigerEx desktop variants.

## Features
- Multi-window support
- Advanced security with context isolation
- Auto-updater integration
- Hardware wallet support
- System tray integration
- Comprehensive menu system
- IPC communication layer
- Cross-platform support (Windows, macOS, Linux)

## Installation

```bash
cd unified-desktop-app
npm install
```

## Development

```bash
# Start in development mode
npm run dev

# Start with web app
npm run start:web
```

## Build

```bash
# Build for current platform
npm run build

# Build for specific platforms
npm run build:win
npm run build:mac
npm run build:linux
```

## Architecture

### Security Features
- Context isolation enabled
- Node integration disabled
- Secure IPC communication
- Input validation
- External link handling

### Multi-Window Support
- Main trading window
- Chart windows
- Order entry windows
- Settings windows
- Modal dialogs

### IPC Communication
- Settings management
- Session handling
- API requests
- File operations
- Real-time updates

## Configuration

Environment variables:
- `API_URL`: Backend API URL
- `WS_URL`: WebSocket URL
- `NODE_ENV`: Development mode

## Icons

Place platform-specific icons in `assets/`:
- `icon.png` (Linux)
- `icon.ico` (Windows)
- `icon.icns` (macOS)

## License
MIT