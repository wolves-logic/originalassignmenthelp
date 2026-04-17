# ── Stage 1: Build dependencies ───────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# System libs needed to compile psycopg2 (PostgreSQL driver)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies into a prefix so we can copy them cleanly
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: Runtime image ────────────────────────────────────────────────────
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1

WORKDIR /app

# Only the runtime PostgreSQL client library — no compiler
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder stage
COPY --from=builder /install /usr/local

# Copy application source (respects .dockerignore)
COPY . .

# Create a non-root user so the container does not run as root
# Must happen BEFORE chmod so the non-root user owns the dirs.
RUN addgroup --system app && adduser --system --ingroup app app \
    && mkdir -p /app/staticfiles /app/logs \
    && chmod +x /app/entrypoint.sh \
    && chown -R app:app /app

USER app

# Gunicorn will listen on this port; Nginx proxies to it
EXPOSE 8000

# Health check — used by Docker engine and the blue/green deploy script.
# Polls /health/ which returns 200 {"status": "ok"} when Gunicorn is ready.
HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=5 \
    CMD curl -sf http://localhost:8000/health/ || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]