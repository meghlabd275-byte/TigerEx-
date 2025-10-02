FROM gcc:11 as builder

WORKDIR /app

# Copy source code
COPY src/ ./src/

# Build the application
RUN g++ -std=c++17 -O3 -o service ./src/main.cpp

# Runtime stage
FROM debian:stable-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the binary from builder stage
COPY --from=builder /app/service .

# Expose port
EXPOSE 8005

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8005/health || exit 1

# Run the application
CMD ["./service"]
