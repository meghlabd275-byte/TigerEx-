# matching-engine

**Version:** 3.0.0  
**Status:** Production Ready

## Features

- Complete admin controls with RBAC
- Health monitoring endpoints
- Configuration management
- Audit logging
- Emergency controls

## Admin Endpoints

- `GET /admin/health` - Service health check
- `GET /admin/status` - Detailed service status
- `GET /admin/config` - Get configuration
- `PUT /admin/config` - Update configuration
- `GET /admin/metrics` - Service metrics
- `GET /admin/logs` - Service logs

## Running

```bash
# Install dependencies
pip install -r requirements.txt  # For Python
go mod download                   # For Go
cargo build                       # For Rust

# Run service
python src/main.py               # For Python
go run main.go                   # For Go
cargo run                        # For Rust
```

## Version History

- v3.0.0 - Complete admin controls implementation
