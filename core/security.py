import re
import time
import hmac
import hashlib
import secrets
import threading
import functools
from urllib.parse import urlencode
from datetime import datetime, timedelta
from flask import request, session, g, make_response, render_template, redirect, url_for, jsonify, current_app

from database import get_db
from core.config import BAN_COOKIE_NAME
from core.helpers import get_settings_dict

# ==========================================
# CUSTOMIZABLE ADMIN PANEL PATH HELPERS
# ==========================================

RESERVED_PUBLIC_SLUGS = {
    "shop", "arsenal", "product", "products", "journal", "intel", "post", "posts",
    "about", "request", "request-tool", "orders", "login", "register", "logout",
    "vault", "api", "static", "uploads", "favicon.ico", "robots.txt", "sitemap.xml",
    "404-preview-live", "403-preview-live", "429-preview-live"
}


def validate_admin_custom_path(raw_slug):
    """
    Validates and normalizes a custom admin panel URL path slug.
    Returns (is_valid: bool, cleaned_slug: str, error_msg: str or None)
    """
    slug = str(raw_slug or "").strip().strip("/").strip()
    if not slug:
        return False, "admin", "Admin panel path cannot be empty."
    slug_lower = slug.lower()
    if not re.match(r"^[a-zA-Z0-9_-]{2,64}$", slug):
        return False, "admin", "Admin path must be 2–64 characters using only letters, numbers, hyphens (-), or underscores (_)."
    if slug_lower in RESERVED_PUBLIC_SLUGS:
        return False, "admin", f"'/{slug_lower}' is a reserved storefront route. Please choose a unique path slug."
    return True, slug_lower, None


def get_admin_custom_path_from_settings(settings_dict):
    raw = (settings_dict or {}).get("admin_custom_path", "admin")
    ok, cleaned, _ = validate_admin_custom_path(raw)
    return cleaned if ok else "admin"


def get_admin_custom_path(conn=None):
    settings = get_settings_dict(conn)
    return get_admin_custom_path_from_settings(settings)


def get_admin_panel_url(conn=None):
    return f"/{get_admin_custom_path(conn)}"


def get_admin_login_url(next_url=None, conn=None):
    base = f"/{get_admin_custom_path(conn)}/login"
    if next_url:
        return f"{base}?{urlencode({'next': next_url})}"
    return base


def get_admin_logout_url(conn=None):
    return f"/{get_admin_custom_path(conn)}/logout"


# ==========================================
# CONFIGURABLE RATE LIMITING ENGINE
# ==========================================

_RATE_LIMIT_LOCK = threading.Lock()
_RATE_LIMIT_BUCKETS = {}  # Key: (client_ip, scope) -> {"timestamps": [float], "blocked_until": float, "last_path": str}
_RATE_LIMIT_STATS = {
    "total_throttled": 0,
    "recent_events": []  # List of dicts: {ip, scope, path, retry_after, timestamp}
}


def check_and_record_rate_limit(client_ip, scope, max_requests, window_seconds, block_seconds, req_path="/"):
    """
    Sliding-window rate limiter with configurable temporary block duration.
    Returns (is_limited: bool, info_dict: dict)
    """
    now = time.time()
    cutoff = now - window_seconds
    key = (client_ip, scope)

    with _RATE_LIMIT_LOCK:
        bucket = _RATE_LIMIT_BUCKETS.get(key)
        if bucket is None:
            bucket = {"timestamps": [], "blocked_until": 0.0, "last_path": req_path}
            _RATE_LIMIT_BUCKETS[key] = bucket

        # Check if currently in active cooldown block
        if bucket["blocked_until"] > now:
            retry_after = max(1, int(round(bucket["blocked_until"] - now)))
            _RATE_LIMIT_STATS["total_throttled"] += 1
            return True, {
                "scope": scope,
                "limit": max_requests,
                "remaining": 0,
                "retry_after": retry_after,
                "newly_blocked": False
            }

        # Prune expired timestamps outside the 60s window
        ts_list = [t for t in bucket["timestamps"] if t > cutoff]

        if len(ts_list) >= max_requests:
            bucket["timestamps"] = ts_list
            bucket["blocked_until"] = now + block_seconds
            bucket["last_path"] = req_path
            retry_after = max(1, int(block_seconds))
            _RATE_LIMIT_STATS["total_throttled"] += 1
            event_entry = {
                "ip": client_ip,
                "scope": scope,
                "path": req_path,
                "limit": max_requests,
                "retry_after": retry_after,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            _RATE_LIMIT_STATS["recent_events"].insert(0, event_entry)
            if len(_RATE_LIMIT_STATS["recent_events"]) > 40:
                _RATE_LIMIT_STATS["recent_events"] = _RATE_LIMIT_STATS["recent_events"][:40]

            return True, {
                "scope": scope,
                "limit": max_requests,
                "remaining": 0,
                "retry_after": retry_after,
                "newly_blocked": True
            }

        ts_list.append(now)
        bucket["timestamps"] = ts_list
        bucket["last_path"] = req_path
        remaining = max(0, max_requests - len(ts_list))
        return False, {
            "scope": scope,
            "limit": max_requests,
            "remaining": remaining,
            "retry_after": 0,
            "newly_blocked": False
        }


def get_rate_limit_telemetry():
    """Returns live rate-limiting status and active throttled IPs for the Admin Panel."""
    now = time.time()
    cutoff = now - 60.0
    active_blocks = []
    active_buckets_count = 0

    with _RATE_LIMIT_LOCK:
        keys_to_delete = []
        for (ip, scope), b in _RATE_LIMIT_BUCKETS.items():
            b["timestamps"] = [t for t in b["timestamps"] if t > cutoff]
            if b["blocked_until"] > now:
                active_blocks.append({
                    "ip": ip,
                    "scope": scope,
                    "path": b.get("last_path", "/"),
                    "remaining_seconds": max(1, int(round(b["blocked_until"] - now))),
                    "requests_in_window": len(b["timestamps"])
                })
                active_buckets_count += 1
            elif b["timestamps"]:
                active_buckets_count += 1
            else:
                keys_to_delete.append((ip, scope))

        for k in keys_to_delete:
            _RATE_LIMIT_BUCKETS.pop(k, None)

        return {
            "active_blocks_count": len(active_blocks),
            "active_blocks": active_blocks,
            "tracked_buckets_count": active_buckets_count,
            "total_throttled": _RATE_LIMIT_STATS["total_throttled"],
            "recent_events": list(_RATE_LIMIT_STATS["recent_events"][:15])
        }


def reset_rate_limits(target_ip=None):
    """Clears active rate limit buckets and unblocks throttled IPs."""
    with _RATE_LIMIT_LOCK:
        if target_ip:
            to_remove = [k for k in _RATE_LIMIT_BUCKETS if k[0] == target_ip]
            for k in to_remove:
                _RATE_LIMIT_BUCKETS.pop(k, None)
            return len(to_remove)
        else:
            count = len(_RATE_LIMIT_BUCKETS)
            _RATE_LIMIT_BUCKETS.clear()
            _RATE_LIMIT_STATS["recent_events"].clear()
            return count


# ==========================================
# DATABASE BAN & SANCTION CHECKS
# ==========================================

def check_is_banned_db(conn, client_ip, client_hwid, user_id=None):
    """
    Direct SQLite check against cyber.db without relying on any in-memory/RAM sets.
    Checks:
    1. If user_id is provided: checks users table for is_active == 0 or banned_clients table for user_id.
    2. If client_hwid is provided: checks banned_clients and users (is_active == 0) for device_hwid.
    3. If client_ip is provided: checks banned_clients and users (is_active == 0) for ip_address / last_ip (ignoring loopback).
    Returns (is_banned: bool, reason: str or None)
    """
    LOOPBACK_IPS = {"127.0.0.1", "::1", "localhost"}
    client_ip = (client_ip or "").strip()
    client_hwid = (client_hwid or "").strip()

    # Master Administrator ID 1 is NEVER banned
    if user_id == 1:
        return False, None

    # 1. Check User Account
    if user_id:
        u = conn.execute("SELECT id, username, is_active FROM users WHERE id = ?", (user_id,)).fetchone()
        if u and not u["is_active"]:
            return True, "User Account Suspended"
        b_u = conn.execute("SELECT reason FROM banned_clients WHERE user_id = ?", (user_id,)).fetchone()
        if b_u:
            return True, b_u["reason"] or "User Account Blacklisted"

    # 2. Check Hardware Signature (HWID)
    if client_hwid:
        b_hw = conn.execute("SELECT reason FROM banned_clients WHERE device_hwid = ? AND device_hwid != ''", (client_hwid,)).fetchone()
        if b_hw:
            return True, b_hw["reason"] or "Hardware Identifier Blacklisted"
        u_hw = conn.execute("SELECT username FROM users WHERE device_hwid = ? AND device_hwid != '' AND is_active = 0", (client_hwid,)).fetchone()
        if u_hw:
            return True, "Associated Hardware Signature Deactivated"

    # 3. Check Network IP (excluding local loopback development IPs)
    if client_ip and client_ip not in LOOPBACK_IPS:
        b_ip = conn.execute("SELECT reason FROM banned_clients WHERE ip_address = ? AND ip_address != ''", (client_ip,)).fetchone()
        if b_ip:
            return True, b_ip["reason"] or "Network Origin Blacklisted"
        u_ip = conn.execute("SELECT username FROM users WHERE last_ip = ? AND last_ip != '' AND is_active = 0", (client_ip,)).fetchone()
        if u_ip:
            return True, "Associated Network IP Deactivated"

    return False, None


def generate_ban_crypto_token(client_hwid="", client_ip="", secret_key=None):
    """
    Generates a high-entropy cryptographic HMAC-SHA256 signature token (70 characters)
    for banned clients, preventing simple 1/0 or cookie spoofing.
    """
    if secret_key is None:
        secret_key = current_app.secret_key
    key = secret_key.encode("utf-8") if isinstance(secret_key, str) else secret_key
    raw_payload = f"CYBER_SANCTION_V2::{client_hwid}::{client_ip}::{secrets.token_hex(16)}"
    sig = hmac.new(key, raw_payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"SANCT_{sig}"


VISITOR_COOKIE_NAME = "zf_visitor_id"
SESSION_COOKIE_NAME = "zf_session_id"
VISITOR_COOKIE_MAX_AGE = 1800  # 30 minutes sliding window on every visit


def generate_cryptographic_token():
    """Generates a high-entropy 256-bit cryptographic token for client-side cookies."""
    return secrets.token_hex(32)


def hash_cookie_token(token_str):
    """Generates SHA-256 hash digest of cookie token to prevent storing raw tokens."""
    return hashlib.sha256(str(token_str).encode("utf-8")).hexdigest()


def generate_numeric_id():
    """Generates a numeric sequence identifier for backwards compatibility."""
    return str(secrets.randbelow(9000000000) + 1000000000)


def resolve_visitor_number(conn, raw_cookie_token):
    """
    Cryptographic cookie mapper:
    Maps incoming cryptographic cookie to a clean visitor number.
    Does NOT store the full cookie in analytics — counts how many cookies were used as visitors.
    Returns: (visitor_number_str, is_new_cookie, active_crypto_token)
    """
    now = datetime.now()
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")
    window_cutoff = (now - timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S")

    # Clean storage: auto-clean registry entries older than 7 days
    try:
        clean_cutoff = (now - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
        conn.execute("DELETE FROM visitor_cookie_registry WHERE last_seen < ?", (clean_cutoff,))
    except Exception:
        pass

    raw_token = str(raw_cookie_token or "").strip()
    if len(raw_token) >= 16:
        c_hash = hash_cookie_token(raw_token)
        row = conn.execute("""
            SELECT visitor_number, last_seen
            FROM visitor_cookie_registry
            WHERE cookie_hash = ?
        """, (c_hash,)).fetchone()

        if row:
            if row["last_seen"] >= window_cutoff:
                conn.execute("""
                    UPDATE visitor_cookie_registry
                    SET last_seen = ?
                    WHERE cookie_hash = ?
                """, (now_str, c_hash))
                conn.commit()
                return str(row["visitor_number"]), False, raw_token

    # New or expired 30-min session: generate new cryptographic cookie
    # and assign next sequential visitor number (counting how many cookies were used)
    new_token = generate_cryptographic_token()
    new_hash = hash_cookie_token(new_token)
    max_row = conn.execute("SELECT COALESCE(MAX(visitor_number), 0) FROM visitor_cookie_registry").fetchone()
    next_num = int(max_row[0] or 0) + 1

    conn.execute("""
        INSERT INTO visitor_cookie_registry (cookie_hash, visitor_number, created_at, last_seen)
        VALUES (?, ?, ?, ?)
    """, (new_hash, next_num, now_str, now_str))
    conn.commit()

    return str(next_num), True, new_token


def get_client_ip(req=None):
    """
    Extracts the true client original IP address.
    Prioritizes Cloudflare CDN headers, proxy chains, and reverse proxy headers:
    1. CF-Connecting-IP (Standard Cloudflare CDN header for original visitor IP)
    2. True-Client-IP (Cloudflare Enterprise / Akamai header)
    3. X-Forwarded-For (First / leftmost address in comma-separated proxy list)
    4. X-Real-IP (Standard Nginx / Traefik / reverse proxy header)
    5. req.remote_addr (Direct socket connection IP)
    """
    if req is None:
        req = request

    # 1. Cloudflare primary client IP
    cf_ip = req.headers.get("CF-Connecting-IP")
    if cf_ip and cf_ip.strip():
        return cf_ip.strip()

    # 2. Cloudflare Enterprise / True-Client-IP
    true_ip = req.headers.get("True-Client-IP")
    if true_ip and true_ip.strip():
        return true_ip.strip()

    # 3. X-Forwarded-For (first IP in chain is the real client)
    xff = req.headers.get("X-Forwarded-For")
    if xff and xff.strip():
        first_ip = xff.split(",")[0].strip()
        if first_ip:
            return first_ip

    # 4. X-Real-IP
    x_real = req.headers.get("X-Real-IP")
    if x_real and x_real.strip():
        return x_real.strip()

    # 5. Fallback to direct connection IP
    return (req.remote_addr or "127.0.0.1").strip()


def get_client_user_agent(req=None):
    """Extracts raw client User-Agent string from request headers."""
    if req is None:
        req = request
    ua = req.headers.get("User-Agent") or ""
    return ua.strip()


def _parse_int_setting(settings, key, default_val, min_val=1, max_val=100000):
    try:
        v = int(str(settings.get(key, default_val)).strip())
        return max(min_val, min(max_val, v))
    except Exception:
        return default_val


def is_safe_redirect_url(target_url):
    """Prevents Open Redirect vulnerabilities by ensuring target_url is a local relative path."""
    if not target_url or not isinstance(target_url, str):
        return False
    u = target_url.strip()
    if not u.startswith("/") or u.startswith("//") or u.startswith("/\\") or "://" in u or "\n" in u or "\r" in u:
        return False
    return True


def enforce_security_and_bans():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(24)

    # Always bypass static assets and favicon
    if request.path.startswith("/static/") or request.path == "/favicon.ico":
        return

    # Cross-Origin CSRF Defense on state-changing requests
    if request.method in ("POST", "PUT", "DELETE", "PATCH"):
        origin = (request.headers.get("Origin") or "").strip()
        if origin and origin != "null":
            from urllib.parse import urlparse
            parsed_origin = urlparse(origin)
            req_host = (request.host or "").strip().lower()
            origin_host = (parsed_origin.netloc or "").strip().lower()
            if origin_host and req_host and origin_host != req_host:
                return jsonify({"ok": False, "error": "Forbidden: Cross-origin request blocked by CSRF policy."}), 403

        # Form CSRF Token Verification when csrf_token field is present in form submission
        if request.form and "csrf_token" in request.form:
            form_token = (request.form.get("csrf_token") or "").strip()
            sess_token = (session.get("csrf_token") or "").strip()
            if not form_token or not sess_token or not hmac.compare_digest(form_token, sess_token):
                return jsonify({"ok": False, "error": "Forbidden: Invalid or expired CSRF security token."}), 403

    req_path = request.path.rstrip("/") or "/"
    client_ip = get_client_ip(request)
    conn = get_db()
    settings = get_settings_dict(conn)
    admin_slug = get_admin_custom_path_from_settings(settings)
    g.admin_custom_path = admin_slug

    # =========================================================================
    # 1. CONFIGURABLE RATE LIMITING (LOGIN, API & EVERY PAGE)
    # =========================================================================
    rl_enabled = str(settings.get("rate_limit_enabled", "1")).strip() not in ("0", "false", "False", "off")
    is_admin_session = bool(session.get("admin_id"))
    is_admin_console_route = (
        req_path.startswith("/api/admin/")
        or req_path in (f"/{admin_slug}", f"/{admin_slug}/logout", "/admin/logout")
    )
    is_exempt_telemetry = req_path in ("/api/security/device-verify", "/api/telemetry/ping")

    if rl_enabled and not (is_admin_session and is_admin_console_route) and not is_exempt_telemetry:
        login_max = _parse_int_setting(settings, "rate_limit_login_max", 8, min_val=1, max_val=10000)
        page_max = _parse_int_setting(settings, "rate_limit_page_max", 120, min_val=1, max_val=100000)
        api_max = _parse_int_setting(settings, "rate_limit_api_max", 60, min_val=1, max_val=100000)
        block_seconds = _parse_int_setting(settings, "rate_limit_block_seconds", 60, min_val=1, max_val=86400)

        is_auth_gateway = (
            req_path in ("/login", "/register", f"/{admin_slug}/login", "/admin/login")
        )

        if is_auth_gateway:
            # For admin login GET requests, apply page limit so opening the login screen is smooth,
            # while POST login attempts and /login or /register hits use the strict login rate limit
            if req_path in (f"/{admin_slug}/login", "/admin/login") and request.method == "GET":
                scope = "LOGIN_VIEW"
                scope_label = "AUTHENTICATION GATEWAY PROTECTION"
                limit_val = max(login_max * 2, 10)
            else:
                scope = "LOGIN"
                scope_label = "LOGIN & AUTHENTICATION BRUTE-FORCE DEFENSE"
                limit_val = login_max
        elif req_path.startswith("/api/"):
            scope = "API"
            scope_label = "API ENDPOINT RATE LIMIT"
            limit_val = api_max
        else:
            scope = "PAGE"
            scope_label = "GLOBAL PAGE FLOOD PROTECTION"
            limit_val = page_max

        is_limited, rl_info = check_and_record_rate_limit(
            client_ip=client_ip,
            scope=scope,
            max_requests=limit_val,
            window_seconds=60,
            block_seconds=block_seconds,
            req_path=req_path
        )
        g.rate_limit_info = rl_info

        if is_limited:
            if rl_info.get("newly_blocked"):
                try:
                    log_audit_event(
                        conn,
                        session.get("user_id"),
                        "RATE_LIMITER",
                        "RATE_LIMIT_TRIGGERED",
                        f"Scope={scope}, Path={req_path}, Limit={limit_val}/min, Cooldown={block_seconds}s"
                    )
                    conn.commit()
                except Exception:
                    pass
            conn.close()
            retry_after = rl_info["retry_after"]
            if req_path.startswith("/api/") or request.headers.get("Accept", "").startswith("application/json"):
                resp = make_response(jsonify({
                    "ok": False,
                    "error": f"RATE LIMIT EXCEEDED: Too many requests ({limit_val}/min). Please wait {retry_after}s before trying again.",
                    "retry_after": retry_after,
                    "scope": scope,
                    "status": 429
                }), 429)
            else:
                resp = make_response(render_template(
                    "429.html",
                    site_settings=settings,
                    retry_after=retry_after,
                    rate_limit_scope=scope_label,
                    rate_limit_max=limit_val
                ), 429)
            resp.headers["Retry-After"] = str(retry_after)
            resp.headers["X-RateLimit-Limit"] = str(limit_val)
            resp.headers["X-RateLimit-Remaining"] = "0"
            return resp

    # =========================================================================
    # 2. DEVICE & IP BAN ENFORCEMENT
    # =========================================================================
    if req_path == "/api/security/device-verify" or req_path in (f"/{admin_slug}/login", "/admin/login"):
        conn.close()
        return

    # Master Admin is never subject to device bans
    if session.get("admin_id") == 1:
        conn.close()
        return

    # Cryptographic visitor cookie & visitor number mapping
    raw_cookie = request.cookies.get(VISITOR_COOKIE_NAME) or request.cookies.get("zf_visitor_token")
    vis_num, is_new, crypto_token = resolve_visitor_number(conn, raw_cookie)

    g.visitor_id = vis_num
    g.session_id = vis_num
    g.is_new_visitor = is_new
    g.crypto_visitor_cookie = crypto_token

    client_hwid = (request.cookies.get("zd_hwid") or request.headers.get("X-Device-HWID") or "").strip()
    user_id = session.get("user_id")

    is_banned, _ = check_is_banned_db(conn, client_ip, client_hwid, user_id)

    if is_banned:
        session.clear()
        conn.close()
        resp = make_response(render_template(
            "banned_banner.html",
            site_settings=settings
        ), 403)
        ban_crypto_token = generate_ban_crypto_token(client_hwid, client_ip)
        resp.set_cookie(BAN_COOKIE_NAME, ban_crypto_token, max_age=315360000, path="/", httponly=True, samesite="Lax")
        resp.delete_cookie("zd_allow_token", path="/")
        resp.delete_cookie("zd_banned", path="/")
        return resp

    conn.close()

    if request.cookies.get(BAN_COOKIE_NAME) or request.cookies.get("zd_banned"):
        g.clear_stale_ban_cookie = True


def apply_security_headers(response):
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

    rl_info = getattr(g, "rate_limit_info", None)
    if rl_info and "X-RateLimit-Limit" not in response.headers:
        response.headers["X-RateLimit-Limit"] = str(rl_info.get("limit", 120))
        response.headers["X-RateLimit-Remaining"] = str(rl_info.get("remaining", 0))

    if getattr(g, "clear_stale_ban_cookie", False):
        response.delete_cookie(BAN_COOKIE_NAME, path="/")
        response.delete_cookie("zd_banned", path="/")

    crypto_token = getattr(g, "crypto_visitor_cookie", None)
    if crypto_token and not request.path.startswith("/static/"):
        response.set_cookie(
            VISITOR_COOKIE_NAME,
            crypto_token,
            max_age=VISITOR_COOKIE_MAX_AGE,
            path="/",
            httponly=True,
            samesite="Lax"
        )
        response.set_cookie(
            SESSION_COOKIE_NAME,
            crypto_token,
            max_age=VISITOR_COOKIE_MAX_AGE,
            path="/",
            httponly=True,
            samesite="Lax"
        )
    return response


def get_current_user(conn=None):
    """Returns currently authenticated CUSTOMER on the public web surface."""
    user_id = session.get("user_id")
    if not user_id:
        return None
    close_after = False
    if conn is None:
        conn = get_db()
        close_after = True
    row = conn.execute(
        "SELECT id, username, email, role, telegram_handle, api_token, is_active, last_login_at, created_at, device_hwid, last_ip FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()
    if close_after:
        conn.close()
    if not row or not row["is_active"] or row["role"] != "CUSTOMER" or row["id"] == 1:
        session.pop("user_id", None)
        session.pop("user_role", None)
        return None
    return dict(row)


def get_current_admin(conn=None):
    """Returns currently authenticated STAFF MEMBER (ADMIN or MODERATOR) in the isolated staff console."""
    admin_id = session.get("admin_id")
    if not admin_id:
        return None
    close_after = False
    if conn is None:
        conn = get_db()
        close_after = True
    row = conn.execute(
        "SELECT id, username, email, role, telegram_handle, api_token, is_active, last_login_at, created_at, device_hwid, last_ip FROM users WHERE id = ?",
        (admin_id,)
    ).fetchone()
    if close_after:
        conn.close()
    if not row or not row["is_active"]:
        session.pop("admin_id", None)
        session.pop("admin_role", None)
        session.pop("admin_username", None)
        return None
    if row["role"] == "ADMIN":
        if row["id"] != 1 or row["username"].lower() != "admin":
            session.pop("admin_id", None)
            session.pop("admin_role", None)
            session.pop("admin_username", None)
            return None
    elif row["role"] != "MODERATOR":
        session.pop("admin_id", None)
        session.pop("admin_role", None)
        session.pop("admin_username", None)
        return None
    return dict(row)


def log_audit_event(conn, user_id, username, action, details=""):
    ip_addr = get_client_ip(request)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("""
    INSERT INTO auth_audit_logs (user_id, username, action, ip_address, details, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, username, action, ip_addr, details, now_str))


def login_required(view_func):
    @functools.wraps(view_func)
    def wrapped(*args, **kwargs):
        user = get_current_user()
        if not user:
            if request.path.startswith("/api/"):
                return jsonify({"error": "Unauthorized: Customer authentication required. Access token or customer vault login missing."}), 401
            return redirect(url_for("login_page", next=request.path))
        return view_func(*args, **kwargs)
    return wrapped


def admin_required(view_func):
    """Permits Master Administrator AND Staff Moderators."""
    @functools.wraps(view_func)
    def wrapped(*args, **kwargs):
        admin = get_current_admin()
        if not admin or admin["role"] not in ("ADMIN", "MODERATOR"):
            if request.path.startswith("/api/"):
                return jsonify({"error": "Forbidden: Staff clearance required. Customer accounts cannot access staff APIs."}), 403
            return redirect(get_admin_login_url(next_url=request.path))
        return view_func(*args, **kwargs)
    return wrapped


def master_admin_required(view_func):
    """Permits ONLY the single in-built Master Administrator (ID=1)."""
    @functools.wraps(view_func)
    def wrapped(*args, **kwargs):
        admin = get_current_admin()
        if not admin or admin["role"] != "ADMIN" or admin["id"] != 1:
            if request.path.startswith("/api/"):
                return jsonify({"error": "Forbidden: Master Administrator clearance required. Moderators cannot access this module."}), 403
            return redirect(get_admin_panel_url())
        return view_func(*args, **kwargs)
    return wrapped
