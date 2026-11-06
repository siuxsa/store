import os
import secrets
from urllib.parse import urlencode
from flask import Flask, session, request, g, make_response, render_template, jsonify, url_for as flask_url_for

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
    login_required, admin_required, master_admin_required,
    get_admin_custom_path_from_settings
)
from routes import register_all_routes

# ==========================================
# FLASK APPLICATION FACTORY & CONFIGURATION
# ==========================================

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "cyber_zeroday_vault_secret_key_2026_super_hard_to_guess_x991")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

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
    prods = [row_to_product(r) for r in conn.execute("SELECT * FROM products WHERE status = 'PUBLISHED' ORDER BY featured DESC, id ASC").fetchall()]
    conn.close()

    admin_slug = get_admin_custom_path_from_settings(settings)

    def smart_url_for(endpoint, **values):
        if endpoint in ("admin_panel", "admin_login_page", "admin_logout"):
            values.pop("admin_slug", None)
            if endpoint == "admin_panel":
                base = f"/{admin_slug}"
            elif endpoint == "admin_login_page":
                base = f"/{admin_slug}/login"
            else:
                base = f"/{admin_slug}/logout"
            if values:
                return f"{base}?{urlencode(values)}"
            return base
        return flask_url_for(endpoint, **values)

    return {
        "site_settings": settings,
        "current_user": current_user,
        "current_admin": current_admin,
        "global_products": prods,
        "csrf_token": session.get("csrf_token", ""),
        "admin_custom_path": admin_slug,
        "admin_panel_url": f"/{admin_slug}",
        "admin_login_url": f"/{admin_slug}/login",
        "admin_logout_url": f"/{admin_slug}/logout",
        "url_for": smart_url_for
    }


# ==========================================
# CUSTOM TEMPLATE FILTERS
# ==========================================

@app.template_filter("nl2br")
def nl2br_filter(s):
    if not s:
        return ""
    from markupsafe import Markup, escape
    import re
    escaped = str(escape(s))
    formatted = escaped.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br>")
    formatted = re.sub(r"&lt;br\s*/?&gt;", "<br>", formatted, flags=re.IGNORECASE)
    return Markup(formatted)


# ==========================================
# FEATURE-SPECIFIC ROUTE REGISTRATION
# ==========================================

register_all_routes(app)


# ==========================================
# CUSTOM 403, 404 & 429 ERROR HANDLERS
# ==========================================

@app.errorhandler(403)
def handle_403_forbidden(e):
    if request.path.startswith("/api/"):
        return jsonify({"ok": False, "error": "Access denied", "status": 403}), 403
    site_settings = get_settings_dict()
    return render_template("banned_banner.html", site_settings=site_settings), 403


@app.errorhandler(404)
def handle_404_not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"ok": False, "error": "Endpoint not found", "status": 404}), 404
    site_settings = get_settings_dict()
    return render_template("404.html", site_settings=site_settings), 404


@app.errorhandler(429)
def handle_429_rate_limit(e):
    if request.path.startswith("/api/"):
        return jsonify({"ok": False, "error": "Too many requests", "status": 429}), 429
    site_settings = get_settings_dict()
    return render_template("429.html", site_settings=site_settings, retry_after=60), 429


# ==========================================
# SERVER ENTRY POINT
# ==========================================

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
