import re
import json
import secrets
from datetime import datetime
from urllib.parse import quote
from flask import request, session, render_template, redirect, url_for, jsonify, make_response, abort
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_db
from core.config import BAN_COOKIE_NAME
from core.helpers import log_audit_event, get_settings_dict, row_to_product
from core.security import (
    get_current_user, get_current_admin, login_required,
    check_is_banned_db, generate_ban_crypto_token, get_client_ip,
    get_admin_custom_path, get_admin_panel_url, get_admin_login_url,
    is_safe_redirect_url
)

def register_auth_routes(app):
    @app.route("/login", methods=["GET", "POST"])
    def login_page():
        if request.method == "GET":
            user = get_current_user()
            if user:
                return redirect(url_for("user_vault"))
            return render_template(
                "login.html",
                next_url=request.args.get("next", ""),
                error=None,
                page_type="AUTH",
                target_slug="login",
                target_title="Customer Sign In"
            )
    
        identifier = (request.form.get("identifier") or "").strip()
        password = request.form.get("password") or ""
        next_url = (request.form.get("next") or "").strip()
    
        conn = get_db()
        row = conn.execute(
            "SELECT * FROM users WHERE LOWER(username) = LOWER(?) OR LOWER(email) = LOWER(?)",
            (identifier, identifier)
        ).fetchone()
    
        if not row or not check_password_hash(row["password_hash"], password):
            log_audit_event(conn, None, identifier or "unknown", "LOGIN_FAILED", "Invalid customer credentials")
            conn.commit()
            conn.close()
            return render_template(
                "login.html",
                next_url=next_url,
                error="ACCESS DENIED: Invalid customer credentials.",
                page_type="AUTH",
                target_slug="login",
                target_title="Customer Sign In"
            ), 401
    
        if not row["is_active"]:
            log_audit_event(conn, row["id"], row["username"], "LOGIN_BLOCKED", "Customer account suspended")
            conn.commit()
            conn.close()
            return render_template(
                "login.html",
                next_url=next_url,
                error="ACCOUNT SUSPENDED: Contact support desk on Telegram.",
                page_type="AUTH",
                target_slug="login",
                target_title="Customer Sign In"
            ), 403
    
        # ADMIN ACCOUNTS ARE STRICTLY SEPARATE: NO VAULT & NO ACCESS VIA CUSTOMER PORTAL!
        if row["role"] != "CUSTOMER" or row["id"] == 1:
            log_audit_event(conn, row["id"], row["username"], "LOGIN_REJECTED", "Admin attempted customer portal login")
            conn.commit()
            conn.close()
            return render_template(
                "login.html",
                next_url=next_url,
                error="ACCESS RESTRICTED: This portal is exclusively for customer accounts.",
                page_type="AUTH",
                target_slug="login",
                target_title="Customer Sign In"
            ), 403
    
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        client_ip = get_client_ip(request)
        client_hwid = (request.cookies.get("zd_hwid") or "").strip()
        if client_hwid:
            conn.execute("UPDATE users SET last_login_at = ?, last_ip = ?, device_hwid = ? WHERE id = ?", (now_str, client_ip, client_hwid, row["id"]))
        else:
            conn.execute("UPDATE users SET last_login_at = ?, last_ip = ? WHERE id = ?", (now_str, client_ip, row["id"]))
        log_audit_event(conn, row["id"], row["username"], "LOGIN_SUCCESS", "Customer authenticated")
        conn.commit()
        conn.close()
    
        # STRICT SEPARATION: Wipe any administrative session credentials completely
        session.pop("admin_id", None)
        session.pop("admin_username", None)
        session.pop("admin_role", None)
    
        session["user_id"] = row["id"]
        session["user_role"] = "CUSTOMER"
        session["csrf_token"] = secrets.token_hex(24)
    
        if next_url and is_safe_redirect_url(next_url):
            active_admin_path = get_admin_custom_path()
            if not next_url.startswith("/admin") and not next_url.startswith(f"/{active_admin_path}"):
                return redirect(next_url)
        return redirect(url_for("user_vault"))
    
    
    
    
    @app.route("/register", methods=["GET", "POST"])
    def register_page():
        if request.method == "GET":
            user = get_current_user()
            if user:
                return redirect(url_for("user_vault"))
            return render_template(
                "register.html",
                error=None,
                page_type="AUTH",
                target_slug="register",
                target_title="Create Customer Account"
            )
    
        username = (request.form.get("username") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        telegram_handle = (request.form.get("telegram_handle") or "").strip()
        password = request.form.get("password") or ""
        confirm = request.form.get("confirm_password") or ""
    
        if not re.match(r"^[A-Za-z0-9_]{3,28}$", username):
            return render_template(
                "register.html",
                error="Username must be 3-28 characters (letters, numbers, underscore).",
                page_type="AUTH",
                target_slug="register",
                target_title="Register Customer Account"
            ), 400
    
        reserved_names = {"admin", "administrator", "root", "sysadmin", "support", "owner", "moderator", "zeroday"}
        if username.lower() in reserved_names or "admin" in username.lower():
            return render_template(
                "register.html",
                error="This username is reserved. Please choose a standard customer username.",
                page_type="AUTH",
                target_slug="register",
                target_title="Register Customer Account"
            ), 400
    
        if "@" not in email or len(email) < 5:
            return render_template(
                "register.html",
                error="Please provide a valid email address.",
                page_type="AUTH",
                target_slug="register",
                target_title="Create Customer Account"
            ), 400
    
        if len(password) < 6:
            return render_template(
                "register.html",
                error="Password must be at least 6 characters.",
                page_type="AUTH",
                target_slug="register",
                target_title="Create Customer Account"
            ), 400
    
        if password != confirm:
            return render_template(
                "register.html",
                error="Password confirmation does not match.",
                page_type="AUTH",
                target_slug="register",
                target_title="Create Customer Account"
            ), 400
    
        tg_clean = telegram_handle.lstrip("@").strip()
        if not tg_clean or not re.match(r"^[A-Za-z0-9_]{3,32}$", tg_clean) or tg_clean.lower() == "anonymous_operator":
            return render_template(
                "register.html",
                error="A valid Telegram username is required to create an account (e.g. @your_telegram).",
                page_type="AUTH",
                target_slug="register",
                target_title="Create Customer Account"
            ), 400
        telegram_handle = "@" + tg_clean
    
        conn = get_db()
        existing = conn.execute(
            "SELECT id FROM users WHERE LOWER(username) = LOWER(?) OR LOWER(email) = LOWER(?) OR LOWER(telegram_handle) = LOWER(?)",
            (username, email, telegram_handle)
        ).fetchone()
        if existing:
            conn.close()
            return render_template(
                "register.html",
                error="Username, Email, or Telegram username is already registered.",
                page_type="AUTH",
                target_slug="register",
                target_title="Create Customer Account"
            ), 400
    
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        client_ip = get_client_ip(request)
        client_hwid = (request.cookies.get("zd_hwid") or "").strip()
        api_token = "zd_live_op_" + secrets.token_hex(12)
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO users (
            username, email, password_hash, role, telegram_handle,
            api_token, is_active, last_login_at, created_at, device_hwid, last_ip
        ) VALUES (?, ?, ?, 'CUSTOMER', ?, ?, 1, ?, ?, ?, ?)
        """, (
            username, email, generate_password_hash(password),
            telegram_handle, api_token, now_str, now_str, client_hwid, client_ip
        ))
        new_user_id = cur.lastrowid
    
        # Automatically link any existing orders matching their Telegram handle
        if telegram_handle:
            conn.execute(
                "UPDATE orders SET user_id = ? WHERE user_id IS NULL AND LOWER(buyer_telegram) = LOWER(?)",
                (new_user_id, telegram_handle)
            )
    
        log_audit_event(conn, new_user_id, username, "REGISTER_SUCCESS", f"Telegram={telegram_handle}")
        conn.commit()
        conn.close()
    
        # STRICT SEPARATION: Wipe any administrative session credentials completely
        session.pop("admin_id", None)
        session.pop("admin_username", None)
        session.pop("admin_role", None)
    
        session["user_id"] = new_user_id
        session["user_role"] = "CUSTOMER"
        session["csrf_token"] = secrets.token_hex(24)
        return redirect(url_for("user_vault"))
    
    
    
    
    @app.route("/logout")
    def logout_user():
        user = get_current_user()
        if user:
            conn = get_db()
            log_audit_event(conn, user["id"], user["username"], "CUSTOMER_LOGOUT", "Customer signed out")
            conn.commit()
            conn.close()
        session.pop("user_id", None)
        session.pop("user_role", None)
        session.pop("csrf_token", None)
        return redirect(url_for("login_page"))
    
    
    
    
    @app.route("/vault")
    def user_vault():
        admin = get_current_admin()
        if admin:
            # Admin accounts have no client vault! Redirect to admin dashboard
            return redirect(get_admin_panel_url())
        user = get_current_user()
        if not user:
            return redirect(url_for("login_page", next=request.path))
    
        conn = get_db()
        settings = get_settings_dict(conn)

        user_tg = (user.get("telegram_handle") or "").strip()
        if user_tg and user_tg.lower() != "@anonymous_operator":
            conn.execute(
                "UPDATE orders SET user_id = ? WHERE user_id IS NULL AND LOWER(buyer_telegram) = LOWER(?)",
                (user["id"], user_tg)
            )
            conn.commit()
    
        # Fetch orders belonging strictly to this authenticated user
        rows = conn.execute("""
        SELECT * FROM orders
        WHERE user_id = ?
           OR (user_id IS NULL AND LOWER(buyer_telegram) = LOWER(?) AND ? != '' AND LOWER(?) != '@anonymous_operator')
        ORDER BY id DESC
        """, (user["id"], user_tg, user_tg, user_tg)).fetchall()
    
        user_orders = []
        completed_orders = []
        tg_user = settings.get("telegram_user", "ZeroDayMatrixSupport").lstrip("@")
        prefix = settings.get("telegram_msg_prefix", "Hello! I want to purchase:")
    
        for r in rows:
            od = dict(r)
            try:
                od["items"] = json.loads(od.get("items_json") or "[]")
            except Exception:
                od["items"] = []

            if od.get("status") == "COMPLETED":
                try:
                    raw_links = json.loads(od.get("delivery_links_json") or "[]")
                    if not isinstance(raw_links, list):
                        raw_links = []
                except Exception:
                    raw_links = []
                cleaned_links = []
                for lk in raw_links:
                    if isinstance(lk, dict) and (lk.get("url") or "").strip():
                        cleaned_links.append({
                            "label": (lk.get("label") or "").strip() or "Download Package",
                            "url": lk["url"].strip()
                        })
                    elif isinstance(lk, str) and lk.strip():
                        cleaned_links.append({"label": "Download Package", "url": lk.strip()})

                # Fallback to product defaults for legacy completed orders if empty
                if not cleaned_links and not (od.get("delivery_message") or "").strip():
                    seen_urls = set()
                    default_msgs = []
                    for it in od["items"]:
                        sku = (it.get("sku") or "").strip().upper()
                        if sku:
                            pr = conn.execute("SELECT * FROM products WHERE UPPER(sku) = ?", (sku,)).fetchone()
                            if pr:
                                p_priv = row_to_product(pr, include_private=True)
                                for plk in (p_priv.get("delivery_links") or []):
                                    u_s = (plk.get("url") or "").strip()
                                    if u_s and u_s not in seen_urls:
                                        seen_urls.add(u_s)
                                        cleaned_links.append({
                                            "label": plk.get("label") or f"{p_priv['name']} Download",
                                            "url": u_s
                                        })
                                p_m = (p_priv.get("delivery_message") or "").strip()
                                if p_m and p_m not in default_msgs:
                                    default_msgs.append(p_m)
                    if default_msgs and not (od.get("delivery_message") or "").strip():
                        od["delivery_message"] = "\n\n".join(default_msgs)

                od["delivery_links"] = cleaned_links
                od["delivery_message"] = (od.get("delivery_message") or "").strip()
                completed_orders.append(od)
            else:
                # Never expose delivery links, messages, or license info on non-completed orders
                od["delivery_links"] = []
                od["delivery_message"] = ""
                od["fulfilled_license_info"] = ""

            lines = [f"{i.get('qty', 1)}x {i.get('name')} (${float(i.get('price', 0)):.2f})" for i in od["items"]]
            msg = (
                f"{prefix}\n"
                f"Order Ticket: #{od['order_number']}\n"
                f"Operator: {user['username']} ({od['buyer_telegram']})\n"
                f"Items: {', '.join(lines)}\n"
                f"Total: ${float(od['total_amount']):.2f}\n"
                f"Please send payment details to unlock my license/download."
            )
            od["telegram_url"] = f"https://t.me/{tg_user}?text={quote(msg)}"
            user_orders.append(od)
    
        free_tools = [
            row_to_product(r)
            for r in conn.execute("SELECT * FROM products WHERE product_type = 'FREE_TOOL' AND status = 'PUBLISHED'").fetchall()
        ]
        conn.close()
    
        return render_template(
            "vault.html",
            user=user,
            orders=user_orders,
            completed_orders=completed_orders,
            free_tools=free_tools,
            page_type="VAULT",
            target_slug="vault",
            target_title="Vault"
        )


    @app.route("/vault/order/<int:order_id>/download/<int:link_idx>")
    @login_required
    def vault_order_download(order_id, link_idx):
        user = get_current_user()
        if not user:
            return redirect(url_for("login_page", next=request.path))

        conn = get_db()
        user_tg = (user.get("telegram_handle") or "").strip()
        row = conn.execute("""
        SELECT * FROM orders
        WHERE id = ?
          AND status = 'COMPLETED'
          AND (user_id = ? OR (user_id IS NULL AND LOWER(buyer_telegram) = LOWER(?) AND ? != '' AND LOWER(?) != '@anonymous_operator'))
        """, (order_id, user["id"], user_tg, user_tg, user_tg)).fetchone()

        if not row:
            conn.close()
            return jsonify({"error": "Forbidden: You are not authorized to access this order's downloads."}), 403

        od = dict(row)
        try:
            links = json.loads(od.get("delivery_links_json") or "[]")
            if not isinstance(links, list):
                links = []
        except Exception:
            links = []

        if not links:
            try:
                items = json.loads(od.get("items_json") or "[]")
            except Exception:
                items = []
            seen_urls = set()
            for it in items:
                sku = (it.get("sku") or "").strip().upper()
                if sku:
                    pr = conn.execute("SELECT * FROM products WHERE UPPER(sku) = ?", (sku,)).fetchone()
                    if pr:
                        p_priv = row_to_product(pr, include_private=True)
                        for plk in (p_priv.get("delivery_links") or []):
                            u_s = (plk.get("url") or "").strip()
                            if u_s and u_s not in seen_urls:
                                seen_urls.add(u_s)
                                links.append(plk)

        if link_idx < 0 or link_idx >= len(links):
            conn.close()
            return jsonify({"error": "Download link not found."}), 404

        target = links[link_idx]
        target_url = (target.get("url") if isinstance(target, dict) else str(target)).strip()
        if not target_url:
            conn.close()
            return jsonify({"error": "Invalid download URL."}), 404

        # Validate target_url scheme: must be http://, https://, or local relative path starting with /
        if not (target_url.startswith("https://") or target_url.startswith("http://") or (target_url.startswith("/") and not target_url.startswith("//"))):
            conn.close()
            return jsonify({"error": "Insecure download link protocol."}), 400

        log_audit_event(conn, user["id"], user["username"], "ORDER_DOWNLOAD_ACCESSED", f"Order #{od['order_number']} Link #{link_idx + 1}")
        conn.commit()
        conn.close()
        return redirect(target_url)
    
    
    @app.route("/api/vault/profile", methods=["POST"])
    @login_required
    def api_update_vault_profile():
        user = get_current_user()
        data = request.get_json(force=True, silent=True) or {}
        raw_tg = (data.get("telegram_handle") or "").strip()
        new_password = data.get("new_password") or ""
    
        conn = get_db()
        telegram_handle = user.get("telegram_handle") or ""
        if raw_tg:
            tg_clean = raw_tg.lstrip("@").strip()
            if not re.match(r"^[A-Za-z0-9_]{3,32}$", tg_clean) or tg_clean.lower() == "anonymous_operator":
                conn.close()
                return jsonify({"error": "Invalid Telegram handle. Must be 3–32 characters (letters, numbers, underscore)."}), 400
            candidate_tg = "@" + tg_clean
            # Verify uniqueness across other registered users
            existing = conn.execute(
                "SELECT id FROM users WHERE LOWER(telegram_handle) = LOWER(?) AND id != ?",
                (candidate_tg, user["id"])
            ).fetchone()
            if existing:
                conn.close()
                return jsonify({"error": "This Telegram username is already registered to another account."}), 400
            telegram_handle = candidate_tg

        if new_password:
            if len(new_password) < 6:
                conn.close()
                return jsonify({"error": "New password must be at least 6 characters."}), 400
            conn.execute(
                "UPDATE users SET telegram_handle = ?, password_hash = ? WHERE id = ?",
                (telegram_handle, generate_password_hash(new_password), user["id"])
            )
            log_audit_event(conn, user["id"], user["username"], "PASSWORD_CHANGED", "Updated via Operator Vault")
        else:
            conn.execute(
                "UPDATE users SET telegram_handle = ? WHERE id = ?",
                (telegram_handle, user["id"])
            )
            log_audit_event(conn, user["id"], user["username"], "PROFILE_UPDATED", f"Telegram={telegram_handle}")
    
        conn.commit()
        conn.close()
        return jsonify({"ok": True})
    
    
    @app.route("/api/vault/regenerate-token", methods=["POST"])
    @login_required
    def api_regenerate_token():
        user = get_current_user()
        new_tok = f"zd_live_{user['role'].lower()}_{secrets.token_hex(12)}"
        conn = get_db()
        conn.execute("UPDATE users SET api_token = ? WHERE id = ?", (new_tok, user["id"]))
        log_audit_event(conn, user["id"], user["username"], "TOKEN_ROTATED", "Rotated personal API key")
        conn.commit()
        conn.close()
        return jsonify({"ok": True, "api_token": new_tok})
    
    
    # ==========================================
    # FRONTEND SERVER-RENDERED ROUTES
    # ==========================================
    
    
    
    @app.route("/admin/login", defaults={"admin_slug": "admin"}, methods=["GET", "POST"])
    @app.route("/<string:admin_slug>/login", methods=["GET", "POST"])
    def admin_login_page(admin_slug="admin"):
        active_slug = get_admin_custom_path()
        if (admin_slug or "").strip().lower() != active_slug.lower():
            abort(404)

        admin = get_current_admin()
        if admin:
            return redirect(get_admin_panel_url())

        if request.method == "GET":
            return render_template(
                "admin_login.html",
                next_url=request.args.get("next", ""),
                error=None,
                default_identifier="",
                default_password="",
                site_settings=get_settings_dict()
            )

        identifier = (request.form.get("identifier") or "").strip()
        password = request.form.get("password") or ""
        next_url = (request.form.get("next") or "").strip()

        conn = get_db()
        row = conn.execute(
            "SELECT * FROM users WHERE LOWER(username) = LOWER(?) OR LOWER(email) = LOWER(?)",
            (identifier, identifier)
        ).fetchone()

        if not row or not check_password_hash(row["password_hash"], password):
            log_audit_event(conn, None, identifier or "unknown", "ADMIN_LOGIN_FAILED", "Invalid credentials entered")
            conn.commit()
            conn.close()
            return render_template(
                "admin_login.html",
                next_url=next_url,
                error="ACCESS DENIED: Invalid administrative credentials.",
                default_identifier=identifier,
                site_settings=get_settings_dict()
            ), 401

        if not row["is_active"]:
            log_audit_event(conn, row["id"], row["username"], "ADMIN_LOGIN_BLOCKED", "Account suspended")
            conn.commit()
            conn.close()
            return render_template(
                "admin_login.html",
                next_url=next_url,
                error="ACCOUNT SUSPENDED: Administrative clearance revoked.",
                default_identifier=identifier
            ), 403

        # Permit Master Admin (ID=1, role=ADMIN) OR Staff Moderator (role=MODERATOR, is_active=1)
        if row["role"] not in ("ADMIN", "MODERATOR"):
            log_audit_event(conn, row["id"], row["username"], "STAFF_LOGIN_FORBIDDEN", "Unauthorized customer attempted staff login")
            conn.commit()
            conn.close()
            return render_template(
                "admin_login.html",
                next_url=next_url,
                error="ACCESS DENIED: Insufficient operator clearance. Only Master Admin and Staff Moderators may access the Command Matrix.",
                default_identifier=identifier
            ), 403

        if row["role"] == "ADMIN" and (row["id"] != 1 or row["username"].lower() != "admin"):
            log_audit_event(conn, row["id"], row["username"], "ADMIN_LOGIN_FORBIDDEN", "Unauthorized admin identity attempted login")
            conn.commit()
            conn.close()
            return render_template(
                "admin_login.html",
                next_url=next_url,
                error="ACCESS DENIED: Master Administrator clearance restricted to the in-built master account.",
                default_identifier=identifier
            ), 403

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        client_ip = get_client_ip(request)
        client_hwid = (request.cookies.get("zd_hwid") or "").strip()
        if client_hwid:
            conn.execute("UPDATE users SET last_login_at = ?, last_ip = ?, device_hwid = ? WHERE id = ?", (now_str, client_ip, client_hwid, row["id"]))
        else:
            conn.execute("UPDATE users SET last_login_at = ?, last_ip = ? WHERE id = ?", (now_str, client_ip, row["id"]))
        log_audit_event(conn, row["id"], row["username"], "STAFF_LOGIN_SUCCESS", f"Role={row['role']}, IP={client_ip}")
        conn.commit()
        conn.close()

        # STRICT ISOLATION: Destroy any customer session keys completely
        session.pop("user_id", None)
        session.pop("user_role", None)

        # ISOLATED STAFF SESSION
        session["admin_id"] = row["id"]
        session["admin_username"] = row["username"]
        session["admin_role"] = row["role"]
        session["csrf_token"] = secrets.token_hex(24)

        # DIRECT OPEN ADMIN DASHBOARD!
        return redirect(get_admin_panel_url())


    @app.route("/admin/logout", defaults={"admin_slug": "admin"})
    @app.route("/<string:admin_slug>/logout")
    def admin_logout(admin_slug="admin"):
        active_slug = get_admin_custom_path()
        admin = get_current_admin()
        if not admin and (admin_slug or "").strip().lower() != active_slug.lower():
            abort(404)
        if admin:
            conn = get_db()
            log_audit_event(conn, admin["id"], admin["username"], "ADMIN_LOGOUT", "Admin session terminated")
            conn.commit()
            conn.close()
        session.pop("admin_id", None)
        session.pop("admin_username", None)
        session.pop("admin_role", None)
        session.pop("csrf_token", None)
        return redirect(get_admin_login_url())
    
    
    
    
    @app.route("/api/security/device-verify", methods=["POST"])
    def api_device_verify():
        data = request.get_json(force=True, silent=True) or {}
        hwid = (data.get("hwid") or request.cookies.get("zd_hwid") or "").strip()
        client_ip = get_client_ip(request)
        user_id = session.get("user_id")
    
        conn = get_db()
        is_banned, _ = check_is_banned_db(conn, client_ip, hwid, user_id)
        conn.close()
    
        if is_banned:
            resp = jsonify({"banned": True, "error": "Access terminated by administrator."})
            ban_crypto_token = generate_ban_crypto_token(hwid, client_ip)
            resp.set_cookie(BAN_COOKIE_NAME, ban_crypto_token, max_age=315360000, path="/", httponly=True, samesite="Lax")
            resp.delete_cookie("zd_allow_token", path="/")
            resp.delete_cookie("zd_banned", path="/")
            return resp, 403
    
        resp = jsonify({"banned": False, "ok": True})
        resp.delete_cookie(BAN_COOKIE_NAME, path="/")
        resp.delete_cookie("zd_banned", path="/")
        resp.set_cookie("zd_allow_token", secrets.token_hex(24), max_age=31536000, path="/", samesite="Lax")
        if hwid:
            resp.set_cookie("zd_hwid", hwid, max_age=31536000, path="/", samesite="Lax")
        return resp
    
    
