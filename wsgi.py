"""
=================================================================
ZERODAY // ARSENAL & INTEL - WSGI APPLICATION RUNNER
=================================================================
Production WSGI entrypoint for Gunicorn, Waitress, uWSGI, and mod_wsgi.

Usage examples:
  1. Direct execution (Auto-detects Waitress or Flask):
     python3 wsgi.py

  2. Gunicorn (Linux/macOS):
     gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app

  3. Waitress CLI (Cross-Platform):
     waitress-serve --host=0.0.0.0 --port=5000 wsgi:app
=================================================================
"""

import os
import sys

# Ensure project root directory is first in sys.path
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

# Import the configured Flask instance
from app import app, init_db

# Ensure schema and initial tables are verified
init_db()

# Standard WSGI callable references
application = app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")

    # Prefer production-grade Waitress WSGI server if available
    try:
        from waitress import serve
        print(f"[*] Serving ZERODAY WSGI application via Waitress on http://{host}:{port} ...")
        serve(application, host=host, port=port, threads=8)
    except ImportError:
        print(f"[*] Serving ZERODAY WSGI application via Werkzeug on http://{host}:{port} ...")
        application.run(host=host, port=port, debug=False)
