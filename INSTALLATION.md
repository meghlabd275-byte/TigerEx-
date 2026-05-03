# TigerEx - Installation Guide
## Complete Deployment Instructions
---


## 🖥️ System Requirements
### Minimum (Development)
- CPU: 4 cores
- RAM: 8 GB
- Storage: 100 GB SSD

### Recommended (Production)
- CPU: 8+ cores
- RAM: 32+ GB
- Storage: 500 GB SSD
- Network: 1 Gbps


## 🌐 Domain & DNS Setup


### Step 1: Register Domain
Register at: GoDaddy, Namecheap, Cloudflare, Google Domains
Recommended: `tigerex. exchange` or `tigerex. trade`

### Step 2: DNS Configuration
Add DNS records:
```
A Record:
  - @ (root) → Server IP
  - www → Server IP
  - api → Server IP
  
CNAME:
  - exchange → @ or www
  
MX (if email):
  - @ → mail provider
  
TXT:
  - @ → "v=spf1 include:_spf.provider.com ~all"
``` 

### Step 3: SSL Certificate
```bash
# Using Let's Encrypt (Free)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d tigerex.exchange -d www.tigerex.exchange
# Auto-renew: certbot renew --dry-run
```


## ☁️ Cloud Server Setup


### AWS (Amazon Web Services)
#### 1. Launch EC2 Instance
```
Service: EC2
AMI: Ubuntu 22.04 LTS
Instance Type: t3.large (or larger)
Storage: 200 GB gp3
Security Group: Open SSH(22), HTTP(80), HTTPS(443)
```

#### 2. Install TigerEx
```bash
# Connect to instance
ssh ubuntu@ec2-public-ip

# Clone and install
git clone https://github.comeghlabd275-byte/TigerEx-.git
cd TigerEx-
pip install -r requirements. txt
python start_enhanced_services. py
```

#### 3. Configure Web Server
```bash
sudo apt install nginx
sudo cp nginx.conf /etc/nginx/sites-available/tigerex
sudo ln -s /etc/nginx/sites-available/tigerex /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```


### Google Cloud (GCP)
#### 1. Create VM Instance
```
Machine Type: e2-standard-4
OS: Ubuntu 22.04 LTS
Boot Disk: 200 GB SSD
Firewall: Allow HTTP, HTTPS
```

#### 2. Deployment
```bash
# Similar to AWS steps above
gcloud compute ssh <instance-name>
git clone https://github.com/meghlabd275-byte/TigerEx-.git
cd TigerEx-
pip install -r requirements.txt
```

#### 3. Managed Services (Optional)
- Cloud SQL: PostgreSQL 14
- Memorystore: Redis
- Cloud CDN: Enable on load balancer


### Microsoft Azure
#### 1. Create Virtual Machine
```
Image: Ubuntu Server 22.04
Size: D2s v3 (or larger)
Disks: 200 GB Premium SSD
Networking: Open ports 22, 80, 443
```

#### 2. Azure Services (Optional)
- Azure Database for PostgreSQL
- Azure Cache for Redis
- Azure Blob Storage (for files)


### DigitalOcean
#### 1. Create Droplet
```
Image: Ubuntu 22.04 LTS
Size: s-4vcpu-8gb (or larger)
Block Storage: 100 GB
```

#### 2. One-Click Apps
Or use marketplace:
- LAMP/LEMP stack
- Docker


### Oracle Cloud (Free Tier)
#### 1. Always Free Resources
```
2 x VMs (E2.1 Micro)
50 GB Block Storage
``` 


## 🖥️ Virtual Machine


### VMware / VirtualBox
```
RAM: 8+ GB
CPU: 4 cores
Storage: 200 GB
Network: Bridged adapter
```

### Proxmox / ESXi
Create VM with Ubuntu 22.04 LTS template


### WSL2 (Windows Subsystem)
```powershell
# Enable WSL
wsl --install -d Ubuntu-22.04

# Install TigerEx
wsl -d Ubuntu-22.04
git clone https://github.comeghlabd275-byte/TigerEx-.git
cd TigerEx-
pip install -r requirements.txt
python start_enhanced_services.py
```


## 🏠 Dedicated Server / Self-Hosting


### Bare Metal Setup
#### 1. Install OS
```bash
# Ubuntu 22.04 LTS Server
sudo apt update && sudo apt upgrade -y
``` 

#### 2. Install Dependencies
```bash
# Python and pip
sudo apt install python3 python3-pip python3-venv

# Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs

# Database
sudo apt install postgresql redis-server

# Web server
sudo apt install nginx
``` 

#### 3. Clone and Run
```bash
git clone https://github.comeghlabd275-byte/TigerEx-.git
cd TigerEx-
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start services
python start_enhanced_services.py
``` 

#### 4. Process Manager (PM2)
```bash
sudo npm install -g pm2
pm2 start start_enhanced_services.py --name tigerex
pm2 startup
pm2 save
``` 


## 🌐 Shared Hosting / cPanel


### Compatible Providers
- Hostinger, Bluehost, GoDaddy (with SSH access)

### Requirements
- SSH Access (for full features)
- PHP 8.0+
- Node.js (optional)
- PostgreSQL / MySQL
- Redis (optional)


### Installation (Limited)
```bash
# Use file manager or FTP
# Upload files to public_html

# Database setup via phpMyAdmin
# Import SQL files from /scripts/init-db.sql
``` 


## 🐳 Docker Deployment


### Prerequisites
```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Docker Compose
sudo apt install docker-compose
``` 

### Run with Docker
```bash
# Clone repository
git clone https://github.comeghlabd275-byte/TigerEx-.git
cd TigerEx-

# Start services
docker-compose up -d

# Or build custom
docker build -t tigerex/backend ./backend
docker run -d -p 8000:8000 tigerex/backend
``` 


## 🔒 Security Hardening


### Firewall (UFW)
```bash
sudo ufw default deny incoming
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
``` 

### Fail2Ban
```bash
sudo apt install fail2ban
sudo systemctl enable fail2ban
``` 


## 📊 Monitoring Setup


### Health Checks
```bash
# Create systemd service
sudo nano /etc/systemd/system/tigerex.service
```
```
[Unit]
Description=TigerEx Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/TigerEx-
ExecStart=/home/ubuntu/TigerEx-/venv/bin/python start_enhanced_services.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl daemon-reload
sudo systemctl enable tigerex
sudo systemctl start tigerex
``` 


### Logs
```bash
# View logs
journalctl -u tigerex -f
# Or via PM2
pm2 logs tigerex
``` 


## 🚀 Quick Deployment Scripts


### One-Line Deploy
```bash
curl -fsSL https://raw.githubusercontent.com/meghlabd275-byte/TigerEx-/main/scripts/deploy.sh | bash
``` 


## 🔧 Troubleshooting


### Database Connection Errors
```
# Check PostgreSQL
sudo systemctl status postgresql
# Reset if needed
sudo pg_ctlcluster 14 main restart
```

### Redis Connection Errors
```
# Check Redis
sudo systemctl status redis
# Test connection
redis-cli ping
```

### Port Already in Use
```bash
# Find process using port
sudo lsof -i :8000
# Kill if needed
sudo kill -9 <PID>
```## TigerEx Wallet API Multi-chain Decentralized Wallet

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
