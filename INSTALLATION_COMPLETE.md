# TigerEx Complete Platform Installation Guide

## Table of Contents
1. [Web App Installation](#web-app-installation)
2. [Desktop App Installation](#desktop-app-installation)
3. [Android App Installation](#android-app-installation)
4. [iOS App Installation](#ios-app-installation)
5. [Frontend Installation](#frontend-installation)
6. [Backend Installation](#backend-installation)

---

## 1. Web App Installation

### Prerequisites
- Node.js 18+ or PHP 8.0+
- MySQL 8.0+ or PostgreSQL 14+
- Nginx or Apache

### Option A: PHP Web App
```bash
# Upload to web server
cd /var/www/html
git clone https://github.com/meghlabd275-byte/TigerEx-.git
cd TigerEx-/web/php

# Configure database
cp ../../.env.example .env
nano .env  # Set DB credentials

# Set permissions
chown -R www-data:www-data .
chmod -R 755 .

# Import database
mysql -u root -p tigerex < database/schema.sql
```

### Option B: Node.js Web App
```bash
# Install dependencies
cd /var/www/html/TigerEx-/web/node
npm install

# Configure
cp ../../.env.example .env
nano .env

# Start server
pm2 start server.js
```

### Option C: React/Vue/Angular
```bash
# Install
cd web/apps/react
npm install

# Build
npm run build

# Deploy dist/ to web server
```

---

## 2. Desktop App Installation

### Windows
```powershell
# Prerequisites
- Windows 10/11
- .NET 6.0 SDK
- Visual Studio 2022

# Build
cd web/desktop/users-app/Windows
dotnet build -c Release

# Output in bin/Release/
# Run .exe
```

### macOS
```bash
# Prerequisites
- macOS 12+
- Xcode 15+
- .NET 6.0 SDK

# Build
cd web/desktop/users-app/macOS
dotnet build -c Release

# Creates .app bundle
open bin/Release/
```

### Linux
```bash
# Prerequisites
- Ubuntu 22.04+ or similar
- .NET 6.0 SDK

# Build
cd web/desktop/users-app/Linux
dotnet build -c Release

# Run
./bin/Release/tigerex
```

---

## 3. Android App Installation

### Prerequisites
- Android Studio Flamingo+
- Java 17 JDK
- Android SDK 34

### Build APK
```bash
# Open in Android Studio
cd web/android
open users-app/Android/app

# Or build via CLI
./gradlew assembleRelease

# Output: app/build/outputs/apk/release/
```

### Install on Device
```bash
adb install app/build/outputs/apk/release/tigerex.apk
```

---

## 4. iOS App Installation

### Prerequisites
- Xcode 15+
- macOS 14+
- Apple Developer Account

### Build
```bash
# Open in Xcode
cd web/ios/users-app
open Tigerex.xcworkspace

# Build for simulator
xcodebuild -scheme Tigerex -configuration Debug -destination 'platform=iOS Simulator'

# Build for device (requires signing)
xcodebuild -scheme Tigerex -configuration Release -archive
```

---

## 5. Frontend Installation (Domain/Cloud)

### AWS/Amazon Lightsail
```bash
# Launch instance (Ubuntu 22.04)
# Connect via SSH

# Install Nginx
sudo apt update
sudo apt install nginx php-fpm mysql-client

# Upload files
sudo cp -r /root/TigerEx-/web/php/* /var/www/html/
sudo chown -R www-data:www-data /var/www/html

# Configure Nginx
sudo nano /etc/nginx/sites-available/tigerex
# Add server block with domain

# Enable site
sudo ln -s /etc/nginx/sites-available/tigerex /etc/nginx/sites-enabled/

# Restart
sudo systemctl restart nginx
```

### DigitalOcean/Vultr
```bash
# One-click LAMP/LEMP stack
# Upload files to /var/www/html

# Domain DNS A record -> Server IP
```

---

## 6. Backend Installation (VM/Cloud)

### Single Server Setup
```bash
# Launch Ubuntu 22.04 VM
ssh user@server-ip

# Install LAMP stack
sudo apt update
sudo apt install lamp-server^

# Create database
mysql -u root -p
CREATE DATABASE tigerex;
CREATE USER 'tigerex'@'localhost' IDENTIFIED BY 'strongpassword';
GRANT ALL PRIVILEGES ON tigerex.* TO 'tigerex'@'localhost';
FLUSH PRIVILEGES;

# Upload backend
cd /var/www/html
git clone https://github.com/meghlabd275-byte/TigerEx-.git
cp backend/.env.example backend/.env
nano backend/.env

# Start services
sudo systemctl restart apache2
sudo systemctl enable apache2
```

### Docker Setup (Recommended)
```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Pull and run
docker run -d -p 80:80 -p 443:443 \
  -e DB_HOST=localhost \
  -e DB_NAME=tigerex \
  tigerex/backend:latest
```

---

## Environment Variables

Create `.env` file:
```env
# Database
DB_HOST=localhost
DB_PORT=3306
DB_NAME=tigerex
DB_USER=tigerex_user
DB_PASSWORD=your_secure_password

# API
API_URL=https://api.tigerex.com
JWT_SECRET=your_jwt_secret_key

# Mail
MAIL_HOST=smtp.example.com
MAIL_PORT=587
MAIL_USER=noreply@tigerex.com
MAIL_PASSWORD=mail_password

# Security
ENCRYPTION_KEY=your_32_char_encryption_key
```

---

## Quick Start Commands

### Full Deployment on AWS EC2
```bash
#!/bin/bash
# Run as: sudo bash deploy.sh

# Update
apt update && apt upgrade -y

# Install
apt install -y apache2 php mysql-server php-mysql

# Database
mysql -u root -e "CREATE DATABASE tigerex;"

# Upload
cp -r /home/ubuntu/TigerEx-/web/php/* /var/www/html/

# Permissions
chown -R www-data:www-data /var/www/html

# Restart
systemctl restart apache2
systemctl restart mysql
```

---

## Support
- Email: support@tigerex.com
- GitHub Issues: https://github.com/meghlabd275-byte/TigerEx-/issues