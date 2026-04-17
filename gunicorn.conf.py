# Gunicorn configuration — loaded via `gunicorn -c gunicorn.conf.py`
import multiprocessing

# ── Binding ────────────────────────────────────────────────────────────────────
bind = "0.0.0.0:8000"

# ── Workers ────────────────────────────────────────────────────────────────────
# (2 × CPU cores) + 1 is the standard recommendation.
# On t2.micro (1 vCPU) → 3 workers.
# On t3.small (2 vCPU) → 5 workers.
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000

# ── Timeouts ───────────────────────────────────────────────────────────────────
timeout = 120          # Kill worker if it takes longer than this
keepalive = 5          # Keep connection alive for 5 s (behind Nginx: fine)
graceful_timeout = 30  # Seconds to finish existing requests on SIGTERM

# ── Logging — write to stdout/stderr so Docker captures them ──────────────────
accesslog  = "-"   # stdout
errorlog   = "-"   # stderr
loglevel   = "info"
access_log_format = '%(h)s "%(r)s" %(s)s %(b)s %(D)sµs'

# ── Process naming ─────────────────────────────────────────────────────────────
proc_name = "oah_gunicorn"
