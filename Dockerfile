# TigerEx Main Dockerfile
# @file Dockerfile
# @description Main backend API Dockerfile for Render deployment
# @author TigerEx Development Team
# @version v1.0.0

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ /app/backend/
COPY unified-backend/ /app/unified-backend/
COPY src/ /app/src/

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the main application
CMD ["python", "-m", "uvicorn", "backend.src.enhanced_unified_backend:app", "--host", "0.0.0.0", "--port", "8000"]