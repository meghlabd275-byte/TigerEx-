# Trading Engine Dockerfile (C++)
FROM gcc:11 as builder

WORKDIR /app

# Install CMake
RUN apt-get update && apt-get install -y \
    cmake \
    make \
    && rm -rf /var/lib/apt/lists/*

# Copy CMake configuration
COPY CMakeLists.txt .

# Copy source code
COPY . .

# Build the application
RUN mkdir build && cd build && \
    cmake .. && \
    make -j$(nproc)

# Runtime stage
FROM debian:bullseye-slim

WORKDIR /app

# Copy built binary from builder
COPY --from=builder /app/build/trading_engine .

# Expose port
EXPOSE 9001

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:9001/health || exit 1

# Start the service
CMD ["./trading_engine"]