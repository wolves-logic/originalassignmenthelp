#!/bin/bash
# entrypoint.sh — Runs inside the container before Gunicorn starts.
#
# Steps:
#   0. Wait for the RDS database to accept connections (if USE_RDS=True)
#   1. Apply any pending database migrations
#   2. Collect static files to the staticfiles/ volume
#   3. Start Gunicorn
#
# All steps must succeed (set -e) — a failure prevents a broken container
# from starting and causing the health check to fail, which triggers
# automatic rollback in the deploy script.
set -euo pipefail

echo "──────────────────────────────────────────"
echo " OAH Container Starting"
echo " $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "──────────────────────────────────────────"

# ── Step 0: Wait for RDS to be reachable (max 60 s) ────────────────────────
# Skipped if USE_RDS is not True (local dev / CI with SQLite)
python - <<'PYEOF'
import os, socket, sys, time

use_rds = os.environ.get("USE_RDS", "False").strip().lower() == "true"
host    = os.environ.get("RDS_DB_HOST", "")
port    = int(os.environ.get("RDS_DB_PORT", "5432"))

if not use_rds or not host:
    print("[0/3] Database wait skipped (USE_RDS=False or no host set)")
    sys.exit(0)

print(f"[0/3] Waiting for RDS at {host}:{port} ...")
for attempt in range(1, 13):   # 12 × 5 s = 60 s max
    try:
        with socket.create_connection((host, port), timeout=5):
            print(f"[0/3] RDS reachable on attempt {attempt}/12 ✔")
            sys.exit(0)
    except OSError as e:
        print(f"      attempt {attempt}/12 failed: {e}")
        time.sleep(5)

print("[0/3] ERROR: RDS not reachable after 60 s — aborting startup")
sys.exit(1)
PYEOF

echo "[1/3] Running database migrations..."
python manage.py migrate --noinput

echo "[2/3] Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "[2.5/3] Creating superuser (if not exists)..."
# Uses DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_PASSWORD, DJANGO_SUPERUSER_EMAIL env vars.
# We wrap it in a try/except or similar to make it idempotent.
python manage.py createsuperuser --noinput || echo "Superuser creation skipped (already exists or variables missing)"

echo "[3/3] Starting Gunicorn..."
exec gunicorn orignalassignmenthelp.wsgi:application -c gunicorn.conf.py
