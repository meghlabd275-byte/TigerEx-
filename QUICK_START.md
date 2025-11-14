# 🚀 TigerEx - Quick Start Guide

**Get your TigerEx trading platform running in minutes!**

## 📋 **Prerequisites**

### System Requirements
- **Node.js**: 18.0 or higher
- **Python**: 3.11 or higher
- **Docker**: 20.10+ and Docker Compose 2.0+
- **PostgreSQL**: 14.0+ (or use Docker)
- **Redis**: 7.0+ (or use Docker)
- **Git**: Latest version

### Hardware Requirements
- **Minimum**: 4GB RAM, 2 CPU cores, 10GB storage
- **Recommended**: 8GB RAM, 4 CPU cores, 50GB storage
- **Production**: 16GB RAM, 8 CPU cores, 100GB+ SSD

---

## ⚡ **Quick Start (Docker - Recommended)**

### 🐳 **One-Command Setup**
```bash
# Clone the repository
git clone https://github.com/meghlabd275-byte/TigerEx-.git
cd TigerEx-

# Copy environment configuration
cp .env.example .env

# Start all services (this may take 5-10 minutes first time)
docker-compose up -d

# Access the platform
open http://localhost:3000
```

### 🎯 **What's Included?**
- ✅ Frontend application (Next.js)
- ✅ Backend API services (FastAPI)
- ✅ PostgreSQL database
- ✅ Redis cache
- ✅ Nginx load balancer
- ✅ SSL certificates

---

## 🛠️ **Manual Setup**

### 1. **Clone and Setup**
```bash
git clone https://github.com/meghlabd275-byte/TigerEx-.git
cd TigerEx-
cp .env.example .env
```

### 2. **Configure Environment**
```bash
# Edit the .env file with your configuration
nano .env
```

**Key Environment Variables:**
```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/tigerex
REDIS_URL=redis://localhost:6379

# API Keys (get from exchanges)
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET_KEY=your_binance_secret_key

# Security
JWT_SECRET=your_super_secret_jwt_key
ENCRYPTION_KEY=your_encryption_key

# Application
NODE_ENV=development
PORT=3000
API_PORT=8000
```

### 3. **Install Frontend Dependencies**
```bash
cd frontend
npm install
```

### 4. **Install Backend Dependencies**
```bash
cd ../backend
pip install -r requirements.txt
```

### 5. **Setup Database**
```bash
# Initialize database
python -c "
from database.enhanced_database_schema import init_database
init_database()
"

# Run migrations (if any)
python manage.py migrate
```

### 6. **Start Development Servers**
```bash
# Terminal 1: Start frontend
cd frontend
npm run dev

# Terminal 2: Start backend
cd backend
python main.py

# Terminal 3: Start Redis (if not using Docker)
redis-server

# Terminal 4: Start PostgreSQL (if not using Docker)
# This depends on your system - see PostgreSQL docs
```

---

## 🌐 **Access Your Platform**

### 🖥️ **Web Application**
- **Main Platform**: http://localhost:3000
- **Trading Interface**: http://localhost:3000/trading
- **Markets**: http://localhost:3000/markets
- **Portfolio**: http://localhost:3000/assets
- **Admin Dashboard**: http://localhost:3000/admin

### 🔧 **API & Services**
- **API Documentation**: http://localhost:8000/docs
- **Admin API**: http://localhost:8000/admin
- **Health Check**: http://localhost:8000/health

### 📱 **Mobile Development**
```bash
# React Native Mobile App
cd mobile
npm install
npm run start  # Start Metro bundler
npm run android  # Run on Android
npm run ios      # Run on iOS (macOS only)
```

---

## 🔑 **Default Credentials**

### 👤 **Default Admin Account**
- **Username**: admin
- **Password**: admin123
- **Email**: admin@tigerex.com

### 🏦 **Default Test Account**
- **Username**: trader
- **Password**: trader123
- **Email**: trader@tigerex.com

**⚠️ Security Note**: Change default passwords immediately in production!

---

## 🎯 **Quick Verification**

### ✅ **Check if Everything Works**
```bash
# Test frontend
curl http://localhost:3000

# Test backend API
curl http://localhost:8000/health

# Check database connection
python -c "
import psycopg2
conn = psycopg2.connect('postgresql://user:password@localhost:5432/tigerex')
print('Database connection successful!')
"

# Check Redis
redis-cli ping
```

### 🌊 **Test Trading Features**
1. Open http://localhost:3000
2. Register a new account or login with test credentials
3. Navigate to the trading page
4. Place a test order (if testnet is configured)
5. Check your portfolio page

---

## 🛠️ **Common Setup Issues**

### 🔧 **Port Conflicts**
```bash
# Check what's using ports 3000 and 8000
lsof -i :3000
lsof -i :8000

# Kill processes if needed
kill -9 <PID>
```

### 🗄️ **Database Issues**
```bash
# Reset database (WARNING: This deletes all data)
docker-compose down -v
docker-compose up -d

# Or manually reset PostgreSQL
sudo -u postgres psql -c "DROP DATABASE IF EXISTS tigerex;"
sudo -u postgres psql -c "CREATE DATABASE tigerex;"
```

### 🐳 **Docker Issues**
```bash
# Clear Docker cache
docker system prune -a

# Rebuild containers
docker-compose build --no-cache

# Check container logs
docker-compose logs frontend
docker-compose logs backend
```

### 🔑 **API Key Issues**
```bash
# Test Binance API connection
python -c "
import requests
import os
API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_SECRET_KEY')
if not API_KEY or not API_SECRET:
    print('Please set your Binance API keys in .env file')
"
```

---

## 🚀 **Production Deployment**

### ☁️ **Cloud Deployment (AWS)**
```bash
# Using our deployment script
chmod +x deploy.sh
./deploy.sh aws

# Manual AWS deployment
./deploy-comprehensive.sh
```

### 🌍 **Domain Configuration**
```bash
# Update nginx.conf with your domain
sudo nano nginx.conf

# Reload nginx
sudo nginx -t && sudo nginx -s reload

# Setup SSL (Let's Encrypt)
sudo certbot --nginx -d yourdomain.com
```

### 🔒 **Security Configuration**
```bash
# Generate production secrets
openssl rand -base64 32  # JWT Secret
openssl rand -base64 64  # Encryption Key

# Update .env with production values
nano .env
```

---

## 📊 **Monitoring & Maintenance**

### 🔍 **Health Checks**
```bash
# Application health
curl http://localhost:8000/health

# Database health
python -c "
from database.enhanced_database_schema import check_database_health
print(check_database_health())
"

# Redis health
redis-cli ping
```

### 📈 **Performance Monitoring**
```bash
# Check API response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/markets

# Monitor system resources
docker stats
top
htop
```

### 🧹 **Maintenance Commands**
```bash
# Update dependencies
cd frontend && npm update
cd ../backend && pip install -r requirements.txt --upgrade

# Database maintenance
python -c "
from database.enhanced_database_schema import optimize_database
optimize_database()
"

# Clear Redis cache
redis-cli flushall
```

---

## 🆘 **Getting Help**

### 📚 **Documentation**
- [Full Documentation](./README.md)
- [API Reference](./API_DOCUMENTATION.md)
- [Deployment Guide](./DEPLOYMENT_GUIDE.md)
- [Security Guidelines](./SECURITY_GUIDELINES.md)

### 🐛 **Troubleshooting**
```bash
# Enable debug mode
export DEBUG=true

# Check logs
tail -f logs/app.log
tail -f logs/error.log

# Run health checks
npm run health-check
python health_check.py
```

### 💬 **Support Channels**
- **GitHub Issues**: Create an issue in this repository
- **Documentation**: Check the /docs folder
- **Community**: Join our Discord/Telegram
- **Email**: support@tigerex.com

---

## 🎯 **Next Steps**

### 📈 **After Setup**
1. **Configure API Keys**: Add your exchange API keys
2. **Setup Users**: Create user accounts
3. **Configure Markets**: Enable trading pairs
4. **Set Fees**: Configure trading fees
5. **Test Trading**: Place test orders
6. **Monitor**: Check system performance

### 🔧 **Customization**
- **Branding**: Update logos and colors
- **Features**: Enable/disable specific features
- **API**: Integrate external APIs
- **Notifications**: Setup email/SMS alerts
- **Security**: Configure 2FA, rate limiting

---

## 🏆 **Success Metrics**

### ✅ **You're All Set When:**
- ✅ Frontend loads at http://localhost:3000
- ✅ Backend API responds at http://localhost:8000
- ✅ Database connection is successful
- ✅ Redis is working
- ✅ Can register/login to the platform
- ✅ Trading interface loads correctly
- ✅ Market data is displayed
- ✅ Portfolio shows assets

### 🎯 **Production Ready When:**
- ✅ SSL certificates are installed
- ✅ Security headers are configured
- ✅ Monitoring is active
- ✅ Backups are scheduled
- ✅ Performance is optimized
- ✅ Documentation is updated
- ✅ Support channels are ready

---

## 🚀 **Quick Commands Reference**

```bash
# Start platform
docker-compose up -d

# Stop platform
docker-compose down

# View logs
docker-compose logs -f

# Access containers
docker-compose exec frontend bash
docker-compose exec backend bash

# Database operations
docker-compose exec postgres psql -U postgres -d tigerex

# Redis operations
docker-compose exec redis redis-cli

# Update code
git pull origin main
docker-compose build
docker-compose up -d
```

---

## 🎉 **Congratulations!**

You've successfully set up the TigerEx trading platform! 🚀

### 🌟 **What You Now Have:**
- 🏦 **Complete Trading Platform**
- 📱 **Multi-Device Support**
- 🏛️ **Admin Dashboard**
- 🔒 **Enterprise Security**
- ⚡ **High Performance**
- 🌐 **Global Scalability**

### 🎯 **Ready to:**
- ✅ Start trading
- ✅ Onboard users
- ✅ Configure markets
- ✅ Monitor performance
- ✅ Scale operations

---

**🚀 Welcome to the Future of Cryptocurrency Trading!**

Need help? Check our [documentation](./README.md) or create a [GitHub issue](https://github.com/meghlabd275-byte/TigerEx-/issues).

*Built with ❤️ by the TigerEx Team*