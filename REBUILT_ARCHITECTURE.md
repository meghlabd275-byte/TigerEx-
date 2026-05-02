# TigerEx Rebuilt Architecture

This document defines the production-grade architecture for TigerEx.

## Core Stack
- Backend: NestJS (Node.js)
- Matching Engine: Go (high performance)
- Database: PostgreSQL + Redis
- Frontend: Next.js + Tailwind
- Realtime: WebSocket
- Blockchain: Solidity

## Services
- API Gateway
- Auth Service (JWT + RBAC + 2FA)
- User Service
- Trading Engine
- Orderbook სამსახ
- Wallet Service
- Admin Service

## Roles
- Super Admin
- Admin
- Moderator
- User

## Features
- Spot Trading
- Real-time Order Book
- Admin Controls (halt, freeze, ban)
- Wallet System
- Secure Authentication

## Notes
Old multi-language duplicate auth files will be deprecated and replaced by unified backend.
