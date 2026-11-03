import hmac
import hashlib
import secrets
import functools
from datetime import datetime
from flask import request, session, g, make_response, render_template, redirect, url_for, jsonify, current_app

from database import get_db
from core.config import BAN_COOKIE_NAME
from core.helpers import get_settings_dict

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


def enforce_security_and_bans():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(24)

    # Bypass static files, device verification, and admin authentication portal
    if request.path.startswith("/static/") or request.path == "/api/security/device-verify" or request.path.startswith("/admin/login"):
        return

    # Master Admin is never subject to device bans
    if session.get("admin_id") == 1:
        return

    # Extract client network IP & Hardware Fingerprint
    client_ip = request.headers.get("X-Forwarded-For", request.remote_addr or "127.0.0.1").split(",")[0].strip()
    client_hwid = (request.cookies.get("zd_hwid") or request.headers.get("X-Device-HWID") or "").strip()
    user_id = session.get("user_id")

    # Authoritative database ban verification (Database is the absolute single source of truth)
    conn = get_db()
    is_banned, _ = check_is_banned_db(conn, client_ip, client_hwid, user_id)

    if is_banned:
        session.clear()
        settings = get_settings_dict(conn)
        conn.close()
        # Render clean ban page without leaking any IP, HWID, or root-cause fingerprint details
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

    # If client is NOT banned in the database, clear any stale ban cookies immediately
    if request.cookies.get(BAN_COOKIE_NAME) or request.cookies.get("zd_banned"):
        g.clear_stale_ban_cookie = True


def apply_security_headers(response):
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if getattr(g, "clear_stale_ban_cookie", False):
        response.delete_cookie(BAN_COOKIE_NAME, path="/")
        response.delete_cookie("zd_banned", path="/")
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
    # The master admin is NEVER a customer; only non-admin users with role CUSTOMER and id != 1 are customers
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
    # If role is ADMIN, MUST be id=1 and username='admin'
    if row["role"] == "ADMIN":
        if row["id"] != 1 or row["username"].lower() != "admin":
            session.pop("admin_id", None)
            session.pop("admin_role", None)
            session.pop("admin_username", None)
            return None
    elif row["role"] != "MODERATOR":
        # Customers can NEVER be in staff console
        session.pop("admin_id", None)
        session.pop("admin_role", None)
        session.pop("admin_username", None)
        return None
    return dict(row)


def log_audit_event(conn, user_id, username, action, details=""):
    ip_addr = request.headers.get("X-Forwarded-For", request.remote_addr or "127.0.0.1")
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
            return redirect(url_for("admin_login_page", next=request.path))
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
            return redirect(url_for("admin_panel"))
        return view_func(*args, **kwargs)
    return wrapped


