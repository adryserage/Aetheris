# Aetheris Worker - Railway Deployment
# Multi-stage build for smaller image

FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Install additional worker dependencies
RUN pip install --no-cache-dir --user \
    fastapi \
    uvicorn[standard] \
    httpx

# Install aetheris from current source
COPY . .
RUN pip install --no-cache-dir --user -e .

# Production image
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Environment variables (set in Railway dashboard)
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8080/health')" || exit 1

# Run the worker
CMD ["python", "-m", "uvicorn", "worker.app:app", "--host", "0.0.0.0", "--port", "8080"]
