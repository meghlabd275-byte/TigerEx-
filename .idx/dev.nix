# To learn more about how to use Nix to configure your environment
# see: https://firebase.google.com/docs/studio/customize-workspace
{ pkgs, ... }: {
  # Which nixpkgs channel to use.
  channel = "stable-24.05";

  # Use https://search.nixos.org/packages to find packages
  packages = [
    pkgs.go
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.python311Packages.fastapi
    pkgs.python311Packages.uvicorn
    pkgs.python311Packages.sqlalchemy
    pkgs.python311Packages.psycopg2
    pkgs.python311Packages.redis
    pkgs.python311Packages.celery
    pkgs.python311Packages.pydantic
    pkgs.python311Packages.python-jose
    pkgs.python311Packages.passlib
    pkgs.python311Packages.bcrypt
    pkgs.python311Packages.python-multipart
    pkgs.python311Packages.websockets
    pkgs.python311Packages.aiofiles
    pkgs.python311Packages.pillow
    pkgs.python311Packages.qrcode
    pkgs.python311Packages.cryptography
    pkgs.python311Packages.requests
    pkgs.python311Packages.beautifulsoup4
    pkgs.python311Packages.selenium
    pkgs.python311Packages.pandas
    pkgs.python311Packages.numpy
    pkgs.python311Packages.matplotlib
    pkgs.python311Packages.plotly
    pkgs.python311Packages.scikit-learn
    pkgs.python311Packages.tensorflow
    pkgs.python311Packages.torch
    pkgs.nodejs_20
    pkgs.nodePackages.nodemon
    pkgs.nodePackages.typescript
    pkgs.nodePackages.yarn
    pkgs.docker
    pkgs.docker-compose
    pkgs.nginx
    pkgs.redis
    pkgs.postgresql
    pkgs.mongodb
    pkgs.git
    pkgs.curl
    pkgs.wget
    pkgs.jq
  ];

  # Sets environment variables in the workspace
  env = {
    NODE_ENV = "development";
    PYTHONPATH = ".";
    DATABASE_URL = "postgresql://localhost:5432/tigerex";
    REDIS_URL = "redis://localhost:6379";
  };

  idx = {
    # Search for the extensions you want on https://open-vsx.org/ and use "publisher.id"
    extensions = [
      "ms-python.python"
      "ms-python.flake8"
      "ms-python.black-formatter"
      "bradlc.vscode-tailwindcss"
      "esbenp.prettier-vscode"
      "dbaeumer.vscode-eslint"
      "ms-vscode.vscode-typescript-next"
      "formulahendry.auto-rename-tag"
      "christian-kohler.path-intellisense"
      "ms-vscode.vscode-json"
      "redhat.vscode-yaml"
      "ms-kubernetes-tools.vscode-kubernetes-tools"
      "ms-vscode-remote.remote-containers"
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
