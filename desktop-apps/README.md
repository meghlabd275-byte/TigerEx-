# TigerEx Desktop Applications

Cross-platform desktop applications for Windows, macOS, and Linux built with Electron.

## Features

- **Cross-Platform**: Single codebase for Windows, macOS, and Linux
- **Native Performance**: Built with Electron for native desktop experience
- **Secure**: Context isolation and secure IPC communication
- **Auto-Updates**: Automatic update checking and installation
- **System Tray**: Background operation with system tray icon
- **Keyboard Shortcuts**: Comprehensive keyboard shortcuts for power users
- **Persistent Storage**: Local data storage with electron-store
- **Native Notifications**: Desktop notifications for important events

## Supported Platforms

### Windows
- Windows 10 and later (64-bit)
- Installer formats: NSIS, Portable
- Auto-update support

### macOS
- macOS 10.13 (High Sierra) and later
- Distribution formats: DMG, ZIP
- Code signing and notarization support
- Auto-update support

### Linux
- Ubuntu 18.04 and later
- Debian 10 and later
- Fedora 32 and later
- Distribution formats: AppImage, DEB, RPM
- Auto-update support

## Installation

### Prerequisites
```bash
npm install
```

### Development
```bash
npm start
```

### Building

#### Build for all platforms
```bash
npm run build
```

#### Build for specific platform
```bash
# Windows
npm run build:win

# macOS
npm run build:mac

# Linux
npm run build:linux
```

## Distribution

Built applications will be available in the `dist/` directory:

- **Windows**: `TigerEx Setup.exe`, `TigerEx Portable.exe`
- **macOS**: `TigerEx.dmg`, `TigerEx-mac.zip`
- **Linux**: `TigerEx.AppImage`, `tigerex.deb`, `tigerex.rpm`

## Features by Platform

### Windows-Specific
- Windows installer with custom branding
- Start menu integration
- Desktop shortcut creation
- File association support
- Windows notifications

### macOS-Specific
- DMG with custom background
- Dock integration
- Touch Bar support (MacBook Pro)
- macOS notifications
- Spotlight integration

### Linux-Specific
- AppImage (portable, no installation required)
- DEB package (Debian/Ubuntu)
- RPM package (Fedora/RHEL)
- Desktop file integration
- System tray support

## Keyboard Shortcuts

### Global
- `Ctrl/Cmd + N` - New Order
- `Ctrl/Cmd + ,` - Settings
- `Ctrl/Cmd + Q` - Quit

### Navigation
- `Ctrl/Cmd + 1` - Markets
- `Ctrl/Cmd + 2` - Trading
- `Ctrl/Cmd + 3` - Portfolio
- `Ctrl/Cmd + 4` - Wallet

### View
- `Ctrl/Cmd + R` - Reload
- `Ctrl/Cmd + Shift + R` - Force Reload
- `F11` - Toggle Fullscreen
- `Ctrl/Cmd + +` - Zoom In
- `Ctrl/Cmd + -` - Zoom Out
- `Ctrl/Cmd + 0` - Reset Zoom

## Configuration

### Environment Variables
- `API_URL` - Backend API URL (default: https://api.tigerex.com)
- `NODE_ENV` - Environment (development/production)

### Build Configuration
Edit `package.json` build section to customize:
- App ID
- Product name
- Icons
- File associations
- Auto-update settings

## Security

- **Context Isolation**: Enabled by default
- **Node Integration**: Disabled in renderer
- **Secure IPC**: All communication through preload script
- **Content Security Policy**: Strict CSP headers
- **Code Signing**: Support for Windows and macOS

## Auto-Updates

The application checks for updates on startup and periodically:
- Windows: Uses Squirrel.Windows
- macOS: Uses Squirrel.Mac
- Linux: Uses AppImage update mechanism

## Troubleshooting

### Windows
- If installer fails, run as administrator
- Check Windows Defender exclusions

### macOS
- If app won't open, check Gatekeeper settings
- For unsigned builds: `xattr -cr TigerEx.app`

### Linux
- For AppImage: `chmod +x TigerEx.AppImage`
- For permission issues: Check executable permissions

## Development

### Project Structure
```
desktop-apps/
├── main.js           # Main process
├── preload.js        # Preload script
├── package.json      # Dependencies and build config
├── assets/           # Icons and images
├── renderer/         # Renderer process (UI)
└── dist/            # Built applications
```

### Adding Features
1. Add IPC handlers in `main.js`
2. Expose APIs in `preload.js`
3. Use APIs in renderer process

## License

MIT License - See LICENSE file for details

## Support

- Documentation: https://docs.tigerex.com
- Support: https://support.tigerex.com
- Issues: https://github.com/tigerex/issues