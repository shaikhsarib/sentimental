# SentiFlow V5: Production Container
# ====================================
# Multi-stage build for minimal attack surface.
# Stage 1: Build dependencies in a full Python image
# Stage 2: Copy into a slim image for production

# ── Stage 1: Builder ──
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: Production ──
FROM python:3.12-slim AS production

# Security: Run as non-root user
RUN groupadd -r sentiflow && useradd -r -g sentiflow -s /bin/false sentiflow

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY backend/ .

# Create required directories with proper permissions
RUN mkdir -p /app/data /app/storage /app/chroma_db \
    && chown -R sentiflow:sentiflow /app

# Security: Drop all capabilities
USER sentiflow

# Environment
ENV ENVIRONMENT=production
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

# Run with uvicorn (production settings)
CMD ["uvicorn", "main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "4", \
     "--limit-concurrency", "100", \
     "--timeout-keep-alive", "30", \
     "--access-log"]
