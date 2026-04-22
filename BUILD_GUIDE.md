# TigerEx Platform - Complete Build & Installation Guide

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.10+
- Java 17+
- Go 1.21+
- Rust 1.70+
- Android Studio (for Android)
- Xcode 15+ (for iOS)

---

## 1. Web Applications

### React TypeScript Users App
```bash
cd web/apps/react/typescript/users-app

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local with your API URL

# Development
npm run dev

# Production build
npm run build
npm run start
```

### React TypeScript Admin App
```bash
cd web/apps/react/typescript/admin-app

npm install
npm run dev
npm run build
```

### Vue TypeScript Users App
```bash
cd web/apps/vue/typescript/users-app

npm install
npm run dev
npm run build
```

### Vue TypeScript Admin App
```bash
cd web/apps/vue/typescript/admin-app

npm install
npm run dev
npm run build
```

### HTML/JS Users App
```bash
cd web/html/users-app

# Simply open index.html in a browser
# Or serve with any HTTP server:
python -m http.server 8080
# Then visit http://localhost:8080
```

### HTML/JS Admin Dashboard
```bash
cd web/html/admin-app

python -m http.server 8081
# Then visit http://localhost:8081
```

---

## 2. Mobile Applications

### Android Kotlin App (Users)
```bash
cd mobile/android/kotlin/users-app

# Build with Gradle
./gradlew assembleDebug

# Or open in Android Studio and run
```

### Android Kotlin App (Admin)
```bash
cd mobile/android/kotlin/admin-app

./gradlew assembleDebug
```

### iOS Swift App (Users)
```bash
cd mobile/ios/swift/users-app

# Open in Xcode
open TigerExUsers.xcodeproj

# Or build via command line
xcodebuild -project TigerExUsers.xcodeproj -scheme TigerExUsers -sdk iphonesimulator -configuration Debug
```

### iOS Swift App (Admin)
```bash
cd mobile/ios/swift/admin-app

xcodebuild -project TigerExAdmin.xcodeproj -scheme TigerExAdmin -sdk iphonesimulator -configuration Debug
```

---

## 3. Desktop Applications

### Python Desktop App (Users)
```bash
cd desktop/python/users-app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

### Python Desktop App (Admin)
```bash
cd desktop/python/admin-app

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Java Desktop App
```bash
cd desktop/java/users-app

# Build with Maven
mvn clean package

# Run JAR
java -jar target/tigerex-users-app.jar
```

### Go Desktop App
```bash
cd desktop/go/users-app

# Build
go build -o tigerex-users-app ./cmd/users

# Run
./tigerex-users-app
```

### Rust Desktop App
```bash
cd desktop/rust/users-app

# Build
cargo build --release

# Run
./target/release/tigerex-users-app
```

---

## 4. Backend Services Connection

All frontend applications connect to the unified backend:

### Production
```env
API_BASE_URL=https://api.tigerex.com
WS_BASE_URL=wss://stream.tigerex.com
```

### Staging
```env
API_BASE_URL=https://api.staging.tigerex.com
WS_BASE_URL=wss://stream.staging.tigerex.com
```

### Development
```env
API_BASE_URL=http://localhost:8000
WS_BASE_URL=ws://localhost:8001
```

### Database Connections
```yaml
PostgreSQL:
  host: ${DB_HOST}
  port: 5432
  database: tigerex
  username: ${DB_USER}
  password: ${DB_PASSWORD}

Redis:
  host: ${REDIS_HOST}
  port: 6379
```

---

## 5. Docker Deployment

### Build Docker Image
```bash
# React Users App
docker build -t tigerex-users-web ./web/apps/react/typescript/users-app
docker run -p 3000:3000 tigerex-users-web

# React Admin App
docker build -t tigerex-admin-web ./web/apps/react/typescript/admin-app
docker run -p 3001:3000 tigerex-admin-web
```

### Docker Compose
```bash
docker-compose up -d
```

---

## 6. Security Configuration

### Environment Variables (Required)
```env
JWT_SECRET=your-secure-jwt-secret-here
ENCRYPTION_KEY=your-32-char-encryption-key
API_KEY=your-api-key
API_SECRET=your-api-secret
```

### CORS Settings
Configure allowed origins in backend configuration to match your deployment domain.

---

## 7. Troubleshooting

### Common Issues

**Port Already in Use**
```bash
# Find process using port
lsof -i :3000
# Kill the process
kill -9 <PID>
```

**Node Module Issues**
```bash
rm -rf node_modules package-lock.json
npm install
```

**Python Import Errors**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Android Build Issues**
```bash
./gradlew clean
./gradlew --refresh-dependencies
```

---

## 8. API Documentation

- API Base: `https://api.tigerex.com`
- Swagger UI: `https://api.tigerex.com/docs`
- WebSocket: `wss://stream.tigerex.com/ws`

### Key Endpoints
```
POST /api/v1/auth/login
POST /api/v1/auth/register
GET  /api/v1/trading/pairs
GET  /api/v1/trading/orderbook/{pair}
POST /api/v1/trading/orders
GET  /api/v1/wallet/balances
POST /api/v1/wallet/withdrawals
```

---

## 9. Support

- Documentation: https://docs.tigerex.com
- Support Email: support@tigerex.com
- API Support: api-support@tigerex.com