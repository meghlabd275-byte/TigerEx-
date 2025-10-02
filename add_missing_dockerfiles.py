#!/usr/bin/env python3
"""
Script to add missing Dockerfiles to services
"""

import os
import json

# Service types and their corresponding Dockerfile templates
DOCKERFILE_TEMPLATES = {
    "python": """FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    libffi-dev \\
    libssl-dev \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Expose port
EXPOSE {port}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:{port}/health || exit 1

# Run the application
CMD ["python", "src/main.py"]
""",
    
    "node": """FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package.json .
COPY package-lock.json .

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY src/ ./src/

# Expose port
EXPOSE {port}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:{port}/health || exit 1

# Run the application
CMD ["node", "src/server.js"]
""",
    
    "rust": """FROM rust:1.75-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    pkg-config \\
    libssl-dev \\
    && rm -rf /var/lib/apt/lists/*

# Copy source code
COPY src/ ./src/
COPY Cargo.toml .
COPY Cargo.lock .

# Build the application
RUN cargo build --release

# Runtime stage
FROM debian:stable-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy the binary from builder stage
COPY --from=builder /app/target/release/spot-trading .

# Expose port
EXPOSE {port}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:{port}/health || exit 1

# Run the application
CMD ["./spot-trading"]
""",
    
    "go": """FROM golang:1.21-alpine as builder

WORKDIR /app

# Install system dependencies
RUN apk add --no-cache \\
    curl \\
    gcc \\
    musl-dev

# Copy go mod files
COPY go.mod .
COPY go.sum .

# Download dependencies
RUN go mod download

# Copy source code
COPY src/ ./src/

# Build the application
RUN go build -o service ./src

# Runtime stage
FROM alpine:latest

WORKDIR /app

# Install runtime dependencies
RUN apk add --no-cache curl

# Copy the binary from builder stage
COPY --from=builder /app/service .

# Expose port
EXPOSE {port}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:{port}/health || exit 1

# Run the application
CMD ["./service"]
""",
    
    "cpp": """FROM gcc:11 as builder

WORKDIR /app

# Copy source code
COPY src/ ./src/

# Build the application
RUN g++ -std=c++17 -O3 -o service ./src/main.cpp

# Runtime stage
FROM debian:stable-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy the binary from builder stage
COPY --from=builder /app/service .

# Expose port
EXPOSE {port}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:{port}/health || exit 1

# Run the application
CMD ["./service"]
"""
}

def detect_service_type(service_path):
    """Detect the service type based on files in the directory"""
    if os.path.exists(os.path.join(service_path, "requirements.txt")) or \
       os.path.exists(os.path.join(service_path, "src", "main.py")):
        return "python"
    
    if os.path.exists(os.path.join(service_path, "package.json")) or \
       os.path.exists(os.path.join(service_path, "src", "server.js")):
        return "node"
    
    if os.path.exists(os.path.join(service_path, "Cargo.toml")) or \
       os.path.exists(os.path.join(service_path, "src", "main.rs")):
        return "rust"
    
    if os.path.exists(os.path.join(service_path, "go.mod")):
        return "go"
    
    if os.path.exists(os.path.join(service_path, "src", "main.cpp")):
        return "cpp"
    
    return None

def add_dockerfile(service_path, service_type, port):
    """Add a Dockerfile to a service"""
    dockerfile_path = os.path.join(service_path, "Dockerfile")
    
    if os.path.exists(dockerfile_path):
        return False
    
    if service_type in DOCKERFILE_TEMPLATES:
        dockerfile_content = DOCKERFILE_TEMPLATES[service_type].format(port=port)
        
        with open(dockerfile_path, "w") as f:
            f.write(dockerfile_content)
        
        return True
    
    return False

def add_missing_dockerfiles():
    """Add missing Dockerfiles to all services"""
    services_dir = "backend"
    
    # Get all service directories
    service_dirs = [d for d in os.listdir(services_dir) 
                   if os.path.isdir(os.path.join(services_dir, d))]
    
    services_with_dockerfiles_added = []
    
    # Port mapping for services (this would typically be in a config file)
    port_mapping = {}
    current_port = 8000
    
    for service_dir in service_dirs:
        service_path = os.path.join(services_dir, service_dir)
        dockerfile_path = os.path.join(service_path, "Dockerfile")
        
        # If Dockerfile doesn't exist, add one
        if not os.path.exists(dockerfile_path):
            service_type = detect_service_type(service_path)
            if service_type:
                # Assign a port if not already assigned
                if service_dir not in port_mapping:
                    port_mapping[service_dir] = current_port
                    current_port += 1
                
                port = port_mapping[service_dir]
                
                if add_dockerfile(service_path, service_type, port):
                    services_with_dockerfiles_added.append(service_dir)
    
    print(f"Added Dockerfiles to {len(services_with_dockerfiles_added)} services:")
    for service in services_with_dockerfiles_added:
        print(f"  - {service}")
    
    return services_with_dockerfiles_added

def main():
    """Main function"""
    added_services = add_missing_dockerfiles()
    print(f"Dockerfile implementation completed! Added {len(added_services)} Dockerfiles.")

if __name__ == "__main__":
    main()