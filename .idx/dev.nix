# Enhanced TigerEx Development Environment Configuration
# Complete development setup for cryptocurrency exchange platform
{ pkgs, ... }: {
  # Which nixpkgs channel to use.
  channel = "stable-24.05";

  # Use https://search.nixos.org/packages to find packages
  packages = [
    # Core Development Tools
    pkgs.go
    pkgs.rust
    pkgs.cargo
    pkgs.python312
    pkgs.python312Packages.pip
    pkgs.python312Packages.virtualenv
    
    # Backend Dependencies
    pkgs.python312Packages.fastapi
    pkgs.python312Packages.uvicorn
    pkgs.python312Packages.sqlalchemy
    pkgs.python312Packages.psycopg2
    pkgs.python312Packages.redis
    pkgs.python312Packages.celery
    pkgs.python312Packages.pydantic
    pkgs.python312Packages.python-jose
    pkgs.python312Packages.passlib
    pkgs.python312Packages.bcrypt
    pkgs.python312Packages.python-multipart
    pkgs.python312Packages.websockets
    pkgs.python312Packages.aiofiles
    pkgs.python312Packages.aiohttp
    pkgs.python312Packages.asyncpg
    
    # Security & Crypto
    pkgs.python312Packages.cryptography
    pkgs.python312Packages.pillow
    pkgs.python312Packages.qrcode
    pkgs.python312Packages.python-dotenv
    
    # Data Processing & Analytics
    pkgs.python312Packages.requests
    pkgs.python312Packages.beautifulsoup4
    pkgs.python312Packages.selenium
    pkgs.python312Packages.pandas
    pkgs.python312Packages.numpy
    pkgs.python312Packages.matplotlib
    pkgs.python312Packages.plotly
    pkgs.python312Packages.scikit-learn
    pkgs.python312Packages.tensorflow
    pkgs.python312Packages.torch
    
    # Frontend Dependencies
    pkgs.nodejs_22
    pkgs.nodePackages.nodemon
    pkgs.nodePackages.typescript
    pkgs.nodePackages.yarn
    pkgs.nodePackages.pnpm
    pkgs.nodePackages.react-native-cli
    pkgs.nodePackages.expo-cli
    
    # Database & Infrastructure
    pkgs.docker
    pkgs.docker-compose
    pkgs.nginx
    pkgs.redis
    pkgs.postgresql_16
    pkgs.mongodb
    pkgs.elasticsearch
    
    # Development Tools
    pkgs.git
    pkgs.curl
    pkgs.wget
    pkgs.jq
    pkgs.helix
    pkgs.ripgrep
    pkgs.fd
    pkgs.bat
    pkgs.eza
    pkgs.tree
    pkgs.htop
    pkgs.netcat
    
    # Security Tools
    pkgs.openssl
    pkgs.gnupg
    pkgs.audit
    pkgs.nmap
    
    # Monitoring & Debugging
    pkgs.postman
    pkgs.insomnia
    pkgs.grpcurl
    pkgs.k6
    
    # Build Tools
    pkgs.cmake
    pkgs.gcc
    pkgs.make
    pkgs.pkg-config
  ];

  # Enhanced environment variables in the workspace
  env = {
    NODE_ENV = "development";
    PYTHONPATH = ".";
    PYTHONPATH = "./unified-backend:./backend:.";
    DATABASE_URL = "postgresql://tigerex:tigerex123@localhost:5432/tigerex_db";
    REDIS_URL = "redis://localhost:6379";
    JWT_SECRET = "development-jwt-secret-change-in-production";
    ENCRYPTION_KEY = "development-encryption-key-change-in-production";
    WEB3_PROVIDER = "https://mainnet.infura.io/v3/YOUR_INFURA_KEY";
    DEBUG = "true";
    LOG_LEVEL = "DEBUG";
    CORS_ORIGINS = "http://localhost:3000,http://localhost:8081";
    ENABLE_ADMIN_PANEL = "true";
    ENABLE_MOBILE_API = "true";
    ENABLE_DESKTOP_API = "true";
    EXCHANGE_API_MODE = "sandbox";
    BLOCKCHAIN_NETWORK = "testnet";
  };

  idx = {
    # Enhanced VS Code extensions for complete development experience
    extensions = [
      # Python Development
      "ms-python.python"
      "ms-python.flake8"
      "ms-python.black-formatter"
      "ms-python.isort"
      "ms-python.debugpy"
      "ms-python.pylint"
      
      # Frontend Development
      "bradlc.vscode-tailwindcss"
      "esbenp.prettier-vscode"
      "dbaeumer.vscode-eslint"
      "ms-vscode.vscode-typescript-next"
      "formulahendry.auto-rename-tag"
      "christian-kohler.path-intellisense"
      "ms-vscode.vscode-json"
      
      # Web3 & Blockchain
      "juanblanco.solidity"
      "nomicfoundation.hardhat-solidity"
      "tintinweb.solidity-visual-auditor"
      
      # Docker & DevOps
      "ms-azuretools.vscode-docker"
      "redhat.vscode-yaml"
      "ms-kubernetes-tools.vscode-kubernetes-tools"
      "ms-vscode-remote.remote-containers"
      
      # Database
      "ms-mssql.mssql"
      "cweijan.vscode-redis-client"
      "mtxr.sqltools"
      
      # API & Testing
      "humao.rest-client"
      "ms-vscode.vscode-postgresql"
      
      # Security
      "ms-vscode.vscode-security-scan"
      
      # Productivity
      "ms-vscode.vscode-todo-highlight"
      "gruntfuggly.todo-tree"
      "github.copilot"
      "github.copilot-chat"
      
      # Git & Collaboration
      "eamodio.gitlens"
      "github.vscode-pull-request-github"
      
      # Documentation
      "yzhang.markdown-all-in-one"
      "shd101wyy.markdown-preview-enhanced"
    ];

    # Enable previews
    previews = {
      enable = true;
      previews = {
        web = {
          command = ["npm" "run" "dev"];
          manager = "web";
          env = {
            PORT = "$PORT";
          };
        };
        backend = {
          command = ["python" "-m" "uvicorn" "main:app" "--host" "0.0.0.0" "--port" "$PORT"];
          manager = "web";
          env = {
            PORT = "$PORT";
          };
        };
      };
    };

    # Workspace lifecycle hooks
    workspace = {
      # Runs when a workspace is first created
      onCreate = {
        npm-install = "npm install";
        pip-install = "pip install -r requirements.txt";
        db-setup = "python scripts/setup_database.py";
      };
      # Runs when the workspace is (re)started
      onStart = {
        start-backend = "python -m uvicorn main:app --host 0.0.0.0 --port 8000";
        start-frontend = "npm run dev";
        start-redis = "redis-server --daemonize yes";
      };
    };
  };
}
