# TigerEx Complete Build & Deployment Guide

## Table of Contents
1. [Project Overview](#project-overview)
2. [Frontend Build Guide](#frontend-build-guide)
3. [Backend Setup Guide](#backend-setup-guide)
4. [Deployment Guide](#deployment-guide)
5. [Server Configuration](#server-configuration)

---

## Project Overview

TigerEx is a complete cryptocurrency exchange platform with:
- **User Apps**: Web, Android, iOS, Desktop (Windows/Mac/Linux)
- **Admin Apps**: Web, Android, iOS, Desktop
- **Backend**: REST API (Node.js + Python/Flask)
- **Features**: Login, Register, KYC, 2FA, Trading, Wallet

---

## PART 1: FRONTEND BUILD GUIDE

### 1.1 Web App (User & Admin)

#### Requirements
- Node.js 18+
- npm or yarn

#### Build Steps

```bash
# Navigate to project
cd /workspace/project/TigerEx-

# Install dependencies
npm install

# Build for production
npm run build

# Output will be in /dist folder
```

#### Files Structure
```
Web App Files:
├── login.html          # User login
├── register.html      # User registration
├── forgot-password.html
├── index.html         # Main landing
├── kyc-verification/  # KYC pages
├── 2fa-reset-verification/
├── test-demo/         # Testing
├── desktop-app/       # Desktop version
└── assets/           # CSS, JS, images
```

---

### 1.2 Android App

#### Option A: React Native (Recommended)

```bash
# Install Expo
npm install -g expo-cli

# Create new project
npx create-expo-app TigerExMobile
cd TigerExMobile

# Copy source files from mobile/ folder

# Install dependencies
npm install
npx expo install expo-camera expo-location expo-google-app-auth

# Build Android APK
npx expo build:android

# Or build with EAS
eas build -p android
```

#### Option B: Native Android (Kotlin/Java)

```bash
# Install Android Studio
# Import project from mobile/android/

# Build APK
./gradlew assembleDebug

# Output: app/build/outputs/apk/debug/
```

#### Option C: Flutter

```bash
# Install Flutter SDK
flutter create tigerex_app
cd tigerex_app

# Copy files from mobile/flutter/

# Build APK
flutter build apk --debug

# Output: build/app/outputs/flutter-apk/
```

---

### 1.3 iOS App

#### Option A: React Native with Expo

```bash
# Build for iOS
npx expo build:ios

# Or with EAS
eas build -p ios

# Note: Requires Apple Developer Account
```

#### Option B: Flutter

```bash
# Build for iOS (requires macOS)
flutter build ios --debug

# For App Store
flutter build ios --release
```

---

### 1.4 Desktop App (Windows/Mac/Linux)

#### Option A: Electron

```bash
# Install Electron
npm install electron electron-builder -g

# Build for current OS
npm run electron .

# Build for all platforms
electron-builder --win --mac --linux
```

#### Option B: Progressive Web App (PWA)

```bash
# PWA is already included in web app
# Just serve with HTTPS
# Works on all desktop browsers
```

---

## PART 2: BACKEND SETUP GUIDE

### 2.1 Node.js Server (Recommended)

```bash
# Navigate to Node server
cd /workspace/project/TigerEx-/server/node

# Install dependencies
npm install

# Start server
npm start

# Server runs on port 3000
```

#### Production Setup with PM2

```bash
# Install PM2
npm install -g pm2

# Start with PM2
pm2 start server.js --name tigerex-api

# Auto-start on boot
pm2 startup
pm2 save
```

---

### 2.2 Python/Flask Server

```bash
# Navigate to Flask server
cd /workspace/project/TigerEx-/server

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install flask flask-cors flask-jwt-extended

# Run server
python app.py

# Server runs on port 5000
```

---

### 2.3 Environment Variables

Create `.env` file:

```env
# Server Configuration
PORT=3000
NODE_ENV=production

# JWT Secret (generate: openssl rand -base64 32)
JWT_SECRET=your-super-secret-jwt-key

# Database (optional - for production)
DATABASE_URL=postgresql://user:pass@localhost:5432/tigerex

# OAuth (for social login)
GOOGLE_CLIENT_ID=your-google-id
GOOGLE_CLIENT_SECRET=your-google-secret
FACEBOOK_APP_ID=your-fb-id
FACEBOOK_APP_SECRET=your-fb-secret
GITHUB_CLIENT_ID=your-github-id
GITHUB_CLIENT_SECRET=your-github-secret

# Email (for OTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

# SMS (for phone OTP)
TWILIO_ACCOUNT_SID=your-sid
TWILIO_AUTH_TOKEN=your-token
TWILIO_PHONE_NUMBER=+1234567890
```

---

## PART 3: DEPLOYMENT GUIDE

### 3.1 Web Deployment (Apache/Nginx)

#### Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /var/www/tigerex;
    index index.html;

    # Frontend static files
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Backend API proxy
    location /api/ {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # SSL (using Certbot)
    listen 443 ssl http2;
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
}
```

#### Apache Configuration

```apache
<VirtualHost *:443>
    ServerName your-domain.com
    DocumentRoot /var/www/tigerex

    <Directory /var/www/tigerex>
        RewriteEngine On
        RewriteCond %{REQUEST_FILENAME} !-f
        RewriteCond %{REQUEST_FILENAME} !-d
        RewriteRule ^ /index.html [L]
    </Directory>

    ProxyPreserveHost On
    ProxyPass /api/ http://localhost:3000/
    ProxyPassReverse /api/ http://localhost:3000/

    SSLEngine on
    SSLCertificateFile /etc/ssl/certs/server.crt
    SSLCertificateKeyFile /etc/ssl/private/server.key
</VirtualHost>
```

---

### 3.2 Cloud Deployment

#### AWS EC2

```bash
# Launch EC2 instance (Ubuntu 20.04)

# SSH into instance
ssh -i key.pem ubuntu@your-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Nginx
sudo apt install -y nginx

# Deploy frontend
sudo cp -r /path/to/dist/* /var/www/tigerex/

# Start backend
cd /path/to/server/node
pm2 start server.js

# Configure Nginx (see above)
```

#### Google Cloud Platform

```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash
gcloud init

# Create instance
gcloud compute instances create tigerex-server \
    --zone=us-central1-a \
    --machine-type=e2-medium \
    --image-family=ubuntu-2004 \
    --image-project=ubuntu-os-cloud

# Deploy using Cloud Run or Compute Engine
```

#### Azure

```bash
# Install Azure CLI
az login

# Create resource group
az group create --name tigerex-rg --location eastus

# Create VM
az vm create \
    --resource-group tigerex-rg \
    --name tigerex-vm \
    --image UbuntuLTS \
    --admin-username azureuser \
    --ssh-key-values @~/.ssh/id_rsa.pub
```

#### DigitalOcean

```bash
# Create Droplet via CLI
doctl compute droplet create tigerex \
    --region nyc1 \
    --size s-4vcpu-8gb \
    --image ubuntu-20-04-x64 \
    --ssh-keys your-ssh-key-id

# Or use Terraform
```

---

### 3.3 Docker Deployment

#### Dockerfile (Frontend)

```dockerfile
FROM nginx:alpine
COPY dist/ /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### Dockerfile (Backend)

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY server/node/ .
RUN npm install --production
EXPOSE 3000
CMD ["node", "server.js"]
```

#### Docker Compose

```yaml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend

  backend:
    build: ./server/node
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - JWT_SECRET=your-secret
    depends_on:
      - db

  db:
    image: postgres:14
    environment:
      POSTGRES_USER: tigerex
      POSTGRES_PASSWORD: password
      POSTGRES_DB: tigerex
    volumes:
      - db-data:/var/lib/postgresql/data

volumes:
  db-data:
```

#### Deploy with Docker

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Update and rebuild
docker-compose pull
docker-compose up -d
```

---

### 3.4 Hosting Platforms

#### Vercel (Frontend)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod

# Or connect GitHub repo in Vercel dashboard
```

#### Netlify (Frontend)

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
netlify deploy --prod --dir=dist

# Or drag and drop dist folder in Netlify dashboard
```

#### Heroku (Backend)

```bash
# Install Heroku CLI
npm install -g heroku

# Login
heroku login

# Create app
heroku create tigerex-api

# Set environment
heroku config:set JWT_SECRET=your-secret

# Deploy
git push heroku main
```

#### Railway (Backend)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Create project
railway init

# Deploy
railway up
```

---

## PART 4: SERVER CONFIGURATION

### 4.1 Domain & SSL

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### 4.2 Security Setup

```bash
# Firewall
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable

# Fail2ban (prevent brute force)
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

### 4.3 Monitoring

```bash
# PM2 monitoring
pm2 install pm2-logrotation
pm2 monitor

# Log management
pm2 logs --lines 100

# System monitoring
htop
```

---

## QUICK START COMMANDS

### For Users

```bash
# Start Node.js server
cd server/node
npm install
npm start

# Access at: http://localhost:3000
# API: http://localhost:3000/api
```

### For Admin

```bash
# Same backend serves admin
# Add /admin path in frontend

# Access admin panel: http://your-domain.com/admin
```

### Complete Stack

```bash
# 1. Start Database (optional)
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password postgres:14

# 2. Start Backend
cd server/node
npm install
JWT_SECRET=secret pm2 start server.js

# 3. Deploy Frontend
# Copy dist/ to web server

# 4. Configure Nginx (see section 3.1)
```

---

## PORT REFERENCE

| Service | Port |
|---------|------|
| Node.js API | 3000 |
| Flask API | 5000 |
| Frontend (dev) | 8080 |
| PostgreSQL | 5432 |
| MongoDB | 27017 |
| Redis | 6379 |

---

## ENVIRONMENT FILES NEEDED

### Frontend (.env)
```env
VITE_API_URL=http://localhost:3000/api
VITE_WS_URL=ws://localhost:3000
```

### Backend (.env)
```env
NODE_ENV=production
PORT=3000
JWT_SECRET=generate-random-secret
DATABASE_URL=postgresql://user:pass@localhost:5432/tigerex
```

---

## DEPLOYMENT CHECKLIST

- [ ] Domain purchased
- [ ] SSL certificate installed
- [ ] Frontend built and deployed
- [ ] Backend running with PM2
- [ ] Database configured (optional)
- [ ] Environment variables set
- [ ] Firewall configured
- [ ] Monitoring setup
- [ ] Backup configured
- [ ] Domain pointing to server IP

---

## SUPPORTED PLATFORMS

### Frontend
- [x] Web Browser (Chrome, Firefox, Safari, Edge, Opera)
- [x] Android (APK, Play Store)
- [x] iOS (IPA, App Store)
- [x] Windows (Desktop, PWA)
- [x] macOS (Desktop, PWA)
- [x] Linux (Desktop, PWA)

### Backend
- [x] Node.js (Production ready)
- [x] Python/Flask (Production ready)
- [x] Docker (All platforms)

---

## PART 5: VERIFICATION

### Test All Features

1. **Open Test Demo**: `your-domain.com/test-demo/`
2. **Use Test Code**: `727752`
3. **Test All Platforms**: Web, Mobile, Desktop

### Test Endpoints

```bash
# Login
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"identifier":"test@tigerex.com","password":"password"}'

# Markets
curl http://localhost:3000/api/trading/markets
```

---

## CONTACT & SUPPORT

For issues or questions, please refer to the main README.md or open an issue on GitHub.

---

*Last Updated: 2026-04-24*
*Version: 1.0.0*
*TigerEx Exchange Platform*
