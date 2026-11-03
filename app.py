import os
import secrets
from flask import Flask, session, request, g, make_response, render_template

from database import init_db, get_db
from core.config import UPLOAD_FOLDER, BAN_COOKIE_NAME, DEFAULT_SITE_SETTINGS
from core.helpers import (
    get_settings_dict, row_to_product, row_to_post,
    render_markdown_prose, log_audit_event, compute_analytics_summary
)
from core.security import (
    check_is_banned_db, generate_ban_crypto_token,
    enforce_security_and_bans, apply_security_headers,
    get_current_user, get_current_admin,
    login_required, admin_required, master_admin_required
)
from routes import register_all_routes

# ==========================================
# FLASK APPLICATION FACTORY & CONFIGURATION
# ==========================================

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "cyber_zeroday_vault_secret_key_2026_super_hard_to_guess_x991")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
init_db()


# ==========================================
# SECURITY GATES & MIDDLEWARE HOOKS
# ==========================================

@app.before_request
def before_request_hook():
    return enforce_security_and_bans()


@app.after_request
def after_request_hook(response):
    return apply_security_headers(response)


# ==========================================
# TEMPLATE CONTEXT PROCESSOR
# ==========================================

@app.context_processor
def inject_globals():
    conn = get_db()
    settings = get_settings_dict(conn)
    current_user = get_current_user(conn)
    current_admin = get_current_admin(conn)
    prods = [row_to_product(r) for r in conn.execute("SELECT * FROM products ORDER BY featured DESC, id ASC").fetchall()]
    conn.close()
    return {
        "site_settings": settings,
        "current_user": current_user,
        "current_admin": current_admin,
        "global_products": prods,
        "csrf_token": session.get("csrf_token", "")
    }


# ==========================================
# FEATURE-SPECIFIC ROUTE REGISTRATION
# ==========================================

register_all_routes(app)


# ==========================================
# SERVER ENTRY POINT
# ==========================================

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
