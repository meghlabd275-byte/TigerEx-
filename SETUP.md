# TigerEx Setup Guide

**Version:** 3.0.0  
**Last Updated:** October 3, 2025

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Backend Setup](#backend-setup)
3. [Frontend Setup](#frontend-setup)
4. [Mobile App Setup](#mobile-app-setup)
5. [Desktop App Setup](#desktop-app-setup)
6. [Database Setup](#database-setup)
7. [Configuration](#configuration)
8. [Running the Platform](#running-the-platform)
9. [Troubleshooting](#troubleshooting)

---

## 1. Prerequisites

### Required Software

- **Node.js:** 18.x or higher
- **Python:** 3.11 or higher
- **Docker:** 20.x or higher
- **Docker Compose:** 2.x or higher
- **PostgreSQL:** 14.x or higher
- **Redis:** 7.x or higher
- **Git:** Latest version

### System Requirements

**Minimum:**
- CPU: 4 cores
- RAM: 8 GB
- Storage: 50 GB SSD

**Recommended:**
- CPU: 8+ cores
- RAM: 16+ GB
- Storage: 100+ GB SSD

---

## 2. Backend Setup

### Step 1: Clone Repository

```bash
git clone https://github.com/meghlabd275-byte/TigerEx-.git
cd TigerEx-
```

### Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

### Step 3: Start Backend Services

**Using Docker Compose (Recommended):**

```bash
cd backend
docker-compose up -d
```

### Step 4: Verify Services

```bash
# Check running services
docker-compose ps

# Check service health
curl http://localhost:8000/health
```

---

## 3. Frontend Setup

### Web Application

```bash
cd frontend/web-app
npm install
npm start
```

**Access:** http://localhost:3000

---

## 4. Mobile App Setup

```bash
cd mobile-app
npm install

# Android
npm run android

# iOS (macOS only)
npm run ios
```

---

## 5. Desktop App Setup

```bash
cd desktop-app
npm install
npm run dev
```

---

## 6. Database Setup

### PostgreSQL

```bash
createdb tigerex
cd backend
python manage.py migrate
```

### Redis

```bash
redis-server
```

---

## 7. Configuration

Edit `backend/config.py` and `frontend/config.js` with your settings.

---

## 8. Running the Platform

### Development Mode

```bash
# Backend
cd backend && docker-compose up

# Frontend
cd frontend/web-app && npm start
```

### Production Mode

```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## 9. Troubleshooting

### Common Issues

- **Port in use:** `lsof -i :8000` and `kill -9 <PID>`
- **Database error:** `systemctl restart postgresql`
- **Docker issues:** `docker-compose down && docker-compose up -d`

### Getting Help

- **Documentation:** https://docs.tigerex.com
- **GitHub Issues:** https://github.com/meghlabd275-byte/TigerEx-/issues
- **Email:** support@tigerex.com

---

**Version:** 3.0.0  
**Status:** Production Ready 🚀