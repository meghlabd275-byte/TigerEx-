# TigerEx - Unified Cryptocurrency Exchange Platform

## 🚀 Project Overview

Welcome to TigerEx, a complete cryptocurrency exchange platform built with a unified backend and a modern frontend. This project consolidates all backend services into a single, high-performance FastAPI application, `unified_backend_v2`, and provides a seamless user experience with a Next.js frontend.

This `README.md` provides a comprehensive guide to understanding, deploying, and developing the TigerEx platform. It serves as the central source of truth for all documentation, replacing outdated files like `API_DOCUMENTATION.md` and `DEPLOYMENT_GUIDE.md`.

## 📚 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [API Documentation](#-api-documentation)
- [Deployment](#-deployment)
- [Local Development](#-local-development)
- [Testing](#-testing)
- [Contributing](#-contributing)

## ✨ Features

- **Unified Backend:** All backend logic is consolidated into a single `unified_backend_v2` service, simplifying development and deployment.
- **Advanced Trading:** Support for stop-loss and take-profit orders.
- **Multi-Chain Wallet:** Deposit and withdraw assets from multiple blockchain networks.
- **Real-Time Market Data:** WebSocket integration for live order book and trade updates.
- **Secure Authentication:** JWT-based authentication with 2FA support.
- **Admin Dashboard:** A comprehensive dashboard for managing users, monitoring platform activity, and more.

## 🏛️ Architecture

The TigerEx platform consists of two main components:

1.  **`unified_backend_v2`:** A FastAPI application that handles all backend logic, including user authentication, trading, wallet management, and market data.
2.  **`frontend`:** A Next.js application that provides the user interface for the exchange.

## 🚀 Deployment

This guide provides instructions for deploying the TigerEx platform in a production environment.

### Prerequisites

- **Docker:** 20.10+
- **Docker Compose:** 1.29+
- **Node.js:** 16+
- **Python:** 3.8+

### 1. Clone the Repository

```bash
git clone https://github.com/meghlabd275-byte/TigerEx-.git
cd TigerEx-
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory and configure the following variables:

```
DATABASE_URL=postgresql://user:password@db/tigerex
REDIS_URL=redis://redis:6379
SECRET_KEY=your_secret_key
```

### 3. Build and Run with Docker Compose

The recommended way to deploy the TigerEx platform is with Docker Compose.

```bash
docker-compose up -d --build
```

This will build and start the `unified_backend_v2`, `frontend`, and all required services.

## 💻 Local Development

For local development, you can run the backend and frontend services separately.

### Backend (`unified_backend_v2`)

1.  **Navigate to the backend directory:**
    ```bash
    cd backend/unified_backend_v2
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the development server:**
    ```bash
    uvicorn main:app --reload
    ```

### Frontend

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

3.  **Run the development server:**
    ```bash
    npm run dev
    ```

## 🧪 Testing

The `unified_backend_v2` includes a comprehensive test suite. To run the tests:

```bash
cd backend/unified_backend_v2
python -m pytest
```
