# ============================================
# TigerEx Unified Backend Dockerfile
# Production-ready with multi-stage build
# ============================================

# ------------------------------------------------------------------------------
# Stage 1: Base image with Python dependencies
# ------------------------------------------------------------------------------
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONFAULTHANDLER=1

WORKDIR /app

# Install system dependencies required for building some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# ------------------------------------------------------------------------------
# Stage 2: Install Python dependencies
# ------------------------------------------------------------------------------
FROM base AS builder

RUN pip wheel --no-cache-dir --wheel-dir /wheelhouse -r requirements.txt

# ------------------------------------------------------------------------------
# Stage 3: Production image
# ------------------------------------------------------------------------------
FROM base

# Create non-root user for security
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/false --create-home appuser

# Install built wheels
COPY --from=builder /wheelhouse /wheelhouse
RUN pip install --no-cache-dir --find-links /wheelhouse -r requirements.txt && \
    rm -rf /wheelhouse

# Copy application code
COPY --chown=appuser:appgroup . .

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8005

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl --fail http://localhost:8005/health || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "complete_admin_system:app", "--host", "0.0.0.0", "--port", "8005", "--workers", "4"]
