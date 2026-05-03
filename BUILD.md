# TigerEx - Apps Building Guide
## Build Instructions for All Platforms
---
## 📱 Android App (APK)
### Prerequisites
- Android Studio (latest)
- JDK 17+
- Android SDK 34

### Build Steps
```bash
# 1. Open project
cd /workspace/project/TigerEx-/mobile/android

# 2. Build debug APK
./gradlew assembleDebug

# 3. Build release APK (signed)
./gradlew assembleRelease
```

### Output
- Debug APK: `mobile/android/app/build/outputs/apk/debug/app-debug.apk`
- Release APK: `mobile/android/app/build/outputs/apk/release/app-release.apk`

### Notes
- Configure `signingConfigs` in `build.gradle` for release
- Enable ProGuard for code obfuscation
---
## 🍎 iOS App (App Store)
### Prerequisites
- macOS (required for iOS)
- Xcode 15+
- Apple Developer Account

### Build Steps
```bash
# 1. Open in Xcode
open /workspace/project/TigerEx-/mobile/ios/TigerEx.xcworkspace

# 2. Select target device (iPhone/iPad)
# 3. Product → Archive
# 4. Distribute via App Store Connect
```

### Alternative (CLI)
```bash
cd /workspace/project/TigerEx-/mobile/ios
xcodebuild -workspace TigerEx.xcworkspace -scheme TigerEx -configuration Release archive
xcodebuild -exportArchive -exportPath ./build -archivePath ./build/TigerEx.xcarchive -exportOptionsPlist ExportOptions.plist
```

### Notes
- Set App ID in Apple Developer Portal
- Configure certificates and provisioning
- Prepare App Store metadata (screenshots, description)
---
## 🪟 Windows Desktop
### Prerequisites
- Node.18+ 
- Electron Builder
- Windows 10+

### Build Steps
```bash
# 1. Install dependencies
cd /workspace/project/TigerEx-/web/desktop
npm install

# 2. Build for Windows
npm run build:win

# Output: dist/TigerEx-Setup.exe
```

### Using Electron Builder
```json
// package.json
{
  "build": {
    "win": {
      "target": ["nsis", "portable"],
      "icon": "assets/icon.ico"
    }
  }
}
```

---
## 🍎 macOS Desktop
### Prerequisites
- macOS (required)
- Xcode 15+
- Node.js 18+

### Build Steps
```bash
# 1. Install deps
cd /workspace/project/TigerEx-/web/desktop
npm install

# 2. Build for macOS
npm run build:mac

# Output: dist/TigerEx.dmg
```

---
## 🐧 Linux Desktop
### Prerequisites
- Node.js 18+
- Linux (Ubuntu 20.04+)

### Build Steps
```bash
# 1. Install deps
cd /workspace/project/TigerEx-/web/desktop
npm install

# 2. Build for Linux
npm run build:linux

# Output: dist/TigerEx.AppImage
```

---
## 📲 WeChat Mini Program (Weapp)
### Prerequisites
- WeChat DevTools
- WeChat ID (Personal/Enterprise)

### Build Steps
```bash
# 1. Open in WeChat DevTools
# Import project: /workspace/project/TigerEx-/mobile/weapp

# 2. Project Settings
# - App ID: Register at mp.weixin.qq.com

# 3. Build
npm run build:weapp
```

### WeChat DevTools
1. Download from https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html
2. Import project
3. Set App ID
4. Build → Preview/Upload

---
## 🌐 Web (PWA)
### Build Steps
```bash
cd /workspace/project/TigerEx-/frontend

# Install dependencies
npm install

# Development
npm run dev

# Production build
npm run build

# Preview production
npm run preview
```

### Deploy
```bash
# Static hosting (Vercel, Netlify, S3)
npm run build
# Upload dist/ folder to hosting
```

---
## 📦 Docker Containers
### Build Docker Images
```bash
# Backend
docker build -t tigerex/backend ./backend

# Frontend
docker build -t tigerex/frontend ./frontend

# Full stack
docker-compose build
```

---
## 🔧 Troubleshooting
### Android
- **Gradle sync failed**: Clear `~/.gradle/caches` and retry
- **SDK not found**: Set `ANDROID_HOME` environment variable

### iOS
- **Code signing errors**: Check certificates and provisioning profiles
- **Podfile issues**: Run `pod repo update` and `pod install`

### Desktop
- **Native module errors**: Rebuild native modules: `npm rebuild`## TigerEx Wallet API Multi-chain Decentralized Wallet

- **24-word BIP39 seed phrase**
- **Ethereum address** (0x...40 hex)
- **Multi-chain**: ETH, BTC, TRX, BNB
- **User ownership**: USER_OWNS

### Create Wallet
```python
create_wallet()  # Python
createWallet()  # JavaScript
CreateWallet()   // Go
create_wallet()  // Rust
```
