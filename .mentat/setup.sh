#!/bin/bash

# Install dependencies for root (Next.js app)
npm install

# Install dependencies for client (React + Vite)
cd client && npm install && cd ..

# Install dependencies for server (Express + TypeScript)
cd server && npm install && cd ..
