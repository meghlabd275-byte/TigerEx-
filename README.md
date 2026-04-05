# TigerEx - Enterprise Cryptocurrency Exchange Platform

![TigerEx](https://img.shields.io/badge/TigerEx-v2.0-green)
![License](https://img.shields.io/badge/license-MIT-blue)
![Build](https://img.shields.io/badge/build-passing-brightgreen)

## 🏗️ Architecture

### Technology Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | Next.js 14, React 18, TypeScript, Tailwind CSS, React Native |
| **Backend** | Python, FastAPI, Node.js, Express, Go, Rust |
| **Database** | PostgreSQL, MongoDB, Redis, TimescaleDB |
| **Blockchain** | Solidity, Hardhat, Ethers.js, Web3.js |
| **Mobile** | Swift (iOS), Kotlin (Android), React Native |
| **Infrastructure** | Docker, Kubernetes, AWS/GCP, Nginx |

### Core Components

1. **Core Trading Engine (Rust)** - High-performance order matching in `backend/core-engine/`
2. **Social Auth Service (Node.js)** - Complete social authentication in `backend/social-auth-service/`
3. **FIX Protocol Engine (Rust)** - Institutional trading support in `backend/fix-protocol-engine/`
4. **Unified Backend (Python)** - FastAPI services in `backend/unified_backend_v2/`
5. **Frontend (Next.js)** - Web application in `frontend/`
6. **Mobile Apps** - Native apps in `mobile/`
7. **Smart Contracts** - Solidity contracts in `blockchain/smart-contracts/`

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
