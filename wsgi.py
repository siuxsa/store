"""
=================================================================
ZERO//FORM — HIGH-ASSURANCE WSGI PRODUCTION APPLICATION SERVER
=================================================================
Production WSGI entrypoint for Gunicorn, Waitress, uWSGI, and reverse proxies.

Standard Deployment Commands:
  1. Standalone Production Server (Waitress):
     python3 wsgi.py

  2. Gunicorn WSGI Server (Linux/Unix):
     gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
     # or: gunicorn -w 4 -b 0.0.0.0:5000 wsgi:application

  3. Waitress CLI (Cross-Platform):
     waitress-serve --host=0.0.0.0 --port=5000 wsgi:app
     # or with callable factory:
     waitress-serve --host=0.0.0.0 --port=5000 --call wsgi:create_app
=================================================================
"""

import os
import sys

# Ensure project root directory is first in sys.path
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

# Optional .env support if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(PROJECT_DIR, ".env"))
except ImportError:
    pass

# Import the configured Flask instance and schema initializer
from app import app, init_db

# Ensure SQLite schema and seed integrity on startup
try:
    init_db()
except Exception as e:
    sys.stderr.write(f"[WARNING] Database initialization check: {e}\n")

# Apply Werkzeug ProxyFix middleware to correctly respect reverse proxy headers
# (e.g. X-Forwarded-For, X-Forwarded-Proto, X-Forwarded-Host from Nginx/Cloudflare/Traefik)
enable_proxy_fix = os.environ.get("ENABLE_PROXY_FIX", "1").strip().lower() in ("1", "true", "yes", "on")
if enable_proxy_fix:
    try:
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(
            app.wsgi_app,
            x_for=int(os.environ.get("PROXY_FIX_FOR", 1)),
            x_proto=int(os.environ.get("PROXY_FIX_PROTO", 1)),
            x_host=int(os.environ.get("PROXY_FIX_HOST", 1)),
            x_port=int(os.environ.get("PROXY_FIX_PORT", 1)),
            x_prefix=int(os.environ.get("PROXY_FIX_PREFIX", 1))
        )
    except Exception as e:
        sys.stderr.write(f"[WARNING] Could not apply ProxyFix middleware: {e}\n")

# Standard WSGI callable references
application = app

def create_app():
    """Application factory for WSGI runners that require or prefer a callable factory."""
    return app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    threads = int(os.environ.get("THREADS", os.environ.get("WEB_CONCURRENCY", 8)))

    # Prefer production-grade Waitress multi-threaded WSGI server if available
    try:
        from waitress import serve
        print(f"[*] ZERO//FORM WSGI production server running via Waitress")
        print(f"[*] Bound interface: http://{host}:{port} (Threads: {threads})")
        print(f"[*] Press CTRL+C to shutdown.")
        serve(application, host=host, port=port, threads=threads)
    except ImportError:
        print(f"[*] ZERO//FORM WSGI fallback server running via Werkzeug")
        print(f"[*] Bound interface: http://{host}:{port}")
        application.run(host=host, port=port, debug=False)
    except KeyboardInterrupt:
        print("\n[*] ZERO//FORM WSGI server cleanly terminated.")
        sys.exit(0)

