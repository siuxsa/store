import json
import secrets
from datetime import datetime, timedelta
from flask import request, jsonify, g

from database import get_db
from core.helpers import compute_analytics_summary
from core.security import (
    admin_required, get_client_ip, get_client_user_agent,
    VISITOR_COOKIE_NAME, SESSION_COOKIE_NAME, VISITOR_COOKIE_MAX_AGE,
    resolve_visitor_number, generate_cryptographic_token
)

def register_telemetry_routes(app):
    @app.route("/api/telemetry/pageview", methods=["POST"])
    @app.route("/api/v1/sync/state", methods=["POST"])
    def api_telemetry_pageview():
        data = request.get_json(force=True, silent=True) or {}

        # 1. Authoritative cryptographic cookie mapping:
        # Maps the 256-bit cryptographic cookie to the sequential visitor number.
        # Analytics tables store ONLY the visitor count number, NEVER the full cookie.
        conn = get_db()
        raw_cookie = request.cookies.get(VISITOR_COOKIE_NAME) or request.cookies.get("zf_visitor_token")
        vis_num, is_new, crypto_token = resolve_visitor_number(conn, raw_cookie)
        visitor_id = vis_num
        session_id = vis_num
        visit_token = vis_num

        # 2. Extract real original IP & Cloudflare CDN IP
        client_ip = get_client_ip(request)

        # 3. Extract actual client User-Agent (not hardcoded system linux/windows)
        user_agent = get_client_user_agent(request) or (data.get("user_agent") or "").strip() or "Mozilla/5.0 (Unknown Client)"

        page_type = (data.get("page_type") or "HOME").strip().upper()
        target_slug = (data.get("target_slug") or "").strip()
        target_title = (data.get("target_title") or page_type).strip()
        duration = max(0, min(7200, int(data.get("duration_seconds") or 0)))
        scroll_pct = max(0, min(100, int(data.get("max_scroll_pct") or 0)))
        referrer = (data.get("referrer") or request.referrer or "Direct").strip()[:120]
        device_type = (data.get("device_type") or "Desktop").strip()
        os_name = (data.get("os_name") or "Linux").strip()

        now_dt = datetime.now()
        now_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")
        window_cutoff = (now_dt - timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S")

        try:
            # Whole-website visitor session deduplication within the active 30-minute window:
            # While the 30-min cookie is active, the WHOLE WEBSITE counts ONE user, not per page.
            existing = conn.execute("""
                SELECT id, visit_token, duration_seconds, max_scroll_pct
                FROM analytics_pageviews
                WHERE visit_token = ?
                   OR (visitor_id = ? AND created_at >= ?)
                ORDER BY id DESC LIMIT 1
            """, (visit_token, visitor_id, window_cutoff)).fetchone()

            if existing:
                # Accumulate dwell time and update current location on the site
                new_dur = max(existing["duration_seconds"], existing["duration_seconds"] + (duration if duration > 0 else 1))
                new_scroll = max(existing["max_scroll_pct"], scroll_pct)
                conn.execute("""
                UPDATE analytics_pageviews
                SET page_type = ?, target_slug = ?, target_title = ?,
                    duration_seconds = ?, max_scroll_pct = ?, last_ping_at = ?,
                    user_agent = ?, ip_address = ?
                WHERE id = ?
                """, (page_type, target_slug, target_title, new_dur, new_scroll, now_str, user_agent, client_ip, existing["id"]))
            else:
                conn.execute("""
                INSERT INTO analytics_pageviews (
                    visit_token, visitor_id, session_id, page_type, target_slug, target_title,
                    duration_seconds, max_scroll_pct, referrer, device_type, os_name,
                    user_agent, ip_address, created_at, last_ping_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    visit_token, visitor_id, session_id, page_type, target_slug, target_title,
                    duration, scroll_pct, referrer, device_type, os_name,
                    user_agent, client_ip, now_str, now_str
                ))

            # Record product and threat intel reach events to keep catalog analytics accurate
            if page_type == "PRODUCT" and target_slug:
                conn.execute("""
                INSERT INTO analytics_events (
                    visitor_id, session_id, event_type, source_page, target_sku, meta_info,
                    user_agent, ip_address, created_at
                ) VALUES (?, ?, 'PRODUCT_VIEW', ?, ?, ?, ?, ?, ?)
                """, (visitor_id, session_id, f"/product/{target_slug}", target_slug, target_title, user_agent, client_ip, now_str))
            elif page_type == "BLOG_POST" and target_slug:
                conn.execute("""
                INSERT INTO analytics_events (
                    visitor_id, session_id, event_type, source_page, target_sku, meta_info,
                    user_agent, ip_address, created_at
                ) VALUES (?, ?, 'BLOG_VIEW', ?, '', ?, ?, ?, ?)
                """, (visitor_id, session_id, f"/intel/{target_slug}", target_title, user_agent, client_ip, now_str))

            # Clean storage: automatically clean up stale session logs older than 30 days
            try:
                clean_cutoff = (now_dt - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
                conn.execute("DELETE FROM analytics_pageviews WHERE created_at < ?", (clean_cutoff,))
                conn.execute("DELETE FROM analytics_events WHERE created_at < ?", (clean_cutoff,))
            except Exception:
                pass

            conn.commit()
        except Exception as e:
            pass
        finally:
            conn.close()

        resp = jsonify({"ok": True, "visitor_id": visitor_id, "session_id": session_id, "ip": client_ip})
        resp.set_cookie(VISITOR_COOKIE_NAME, crypto_token, max_age=VISITOR_COOKIE_MAX_AGE, path="/", httponly=True, samesite="Lax")
        resp.set_cookie(SESSION_COOKIE_NAME, crypto_token, max_age=VISITOR_COOKIE_MAX_AGE, path="/", httponly=True, samesite="Lax")
        return resp


    @app.route("/api/telemetry/event", methods=["POST"])
    @app.route("/api/v1/sync/action", methods=["POST"])
    def api_telemetry_event():
        data = request.get_json(force=True, silent=True) or {}

        # Resolve cryptographic cookie to visitor number
        conn = get_db()
        raw_cookie = request.cookies.get(VISITOR_COOKIE_NAME) or request.cookies.get("zf_visitor_token")
        vis_num, is_new, crypto_token = resolve_visitor_number(conn, raw_cookie)
        visitor_id = vis_num
        session_id = vis_num

        client_ip = get_client_ip(request)
        user_agent = get_client_user_agent(request) or (data.get("user_agent") or "").strip()

        event_type = (data.get("event_type") or "CLICK").strip().upper()
        source_page = (data.get("source_page") or "").strip()
        target_sku = (data.get("target_sku") or "").strip().upper()
        meta_info = (data.get("meta_info") or "").strip()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            conn.execute("""
            INSERT INTO analytics_events (
                visitor_id, session_id, event_type, source_page, target_sku, meta_info,
                user_agent, ip_address, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (visitor_id, session_id, event_type, source_page, target_sku, meta_info, user_agent, client_ip, now_str))
            conn.commit()
        except Exception:
            pass
        finally:
            conn.close()

        resp = jsonify({"ok": True, "visitor_id": visitor_id, "session_id": session_id})
        resp.set_cookie(VISITOR_COOKIE_NAME, crypto_token, max_age=VISITOR_COOKIE_MAX_AGE, path="/", httponly=True, samesite="Lax")
        resp.set_cookie(SESSION_COOKIE_NAME, crypto_token, max_age=VISITOR_COOKIE_MAX_AGE, path="/", httponly=True, samesite="Lax")
        return resp
    
    
    
    
    @app.route("/api/admin/analytics/summary")
    @app.route("/api/analytics/summary")
    @admin_required
    def api_analytics_summary():
        days = max(1, min(90, int(request.args.get("days", 14))))
        conn = get_db()
        data = compute_analytics_summary(conn, days)
        conn.close()
        return jsonify(data)
    
    
    # ==========================================
    # PROTECTED ADMIN CRUD & RBAC APIs
    # ==========================================
    
