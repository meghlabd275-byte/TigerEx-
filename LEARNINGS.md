# TigerEx Documentation
# @file LEARNINGS.md
# @description TigerEx project documentation
# @author TigerEx Development Team

# TigerEx Implementation Learnings

## Multi-Exchange Integration
- Standardized microservice pattern (`{exchange}-advanced-service`) using FastAPI.
- Consistent endpoint naming (`/market/ticker/{symbol}`, `/trade`, `/health`) allows for easy aggregation.

## Unified Admin Control
- Centralized RBAC implementation using JWT and persistent JSON storage.
- Real-time service control (PAUSE, HALT) implemented via a unified status management layer.

## Social Login
- Handled via a centralized `auth-service` that supports account linking (connecting Google/FB/etc IDs to existing email accounts).

## High Performance
- Use of C++ for the core matching engine and Rust for high-throughput data processing ensures sub-millisecond execution times.
