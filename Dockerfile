# Multi-stage build for optimized production image

# Build stage
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml .
COPY src/ src/
COPY external/ external/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir ./external/ngsidekick && \
    pip install --no-cache-dir .

# Production stage
FROM python:3.12-slim

WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=appuser:appuser src/ src/

# Switch to non-root user
USER appuser

# Expose port (Cloud Run will set PORT env var)
ENV PORT=8000
EXPOSE ${PORT}

# Health check (note: Cloud Run ignores HEALTHCHECK, uses its own mechanism)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://localhost:{os.environ.get(\"PORT\", \"8000\")}/health')"

# Run with gunicorn (bind to PORT env var, which Cloud Run will set)
CMD gunicorn --bind 0.0.0.0:${PORT} --workers 4 --timeout 120 ngsidekick_server.wsgi:app

