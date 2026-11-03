import json
from datetime import datetime
from flask import request, jsonify

from database import get_db
from core.helpers import compute_analytics_summary
from core.security import admin_required

def register_telemetry_routes(app):
    @app.route("/api/telemetry/pageview", methods=["POST"])
    @app.route("/api/v1/sync/state", methods=["POST"])
    def api_telemetry_pageview():
        data = request.get_json(force=True, silent=True) or {}
        visit_token = (data.get("visit_token") or "").strip()
        if not visit_token:
            return jsonify({"ok": False}), 400
    
        visitor_id = (data.get("visitor_id") or "anon").strip()
        session_id = (data.get("session_id") or "sess").strip()
        page_type = (data.get("page_type") or "HOME").strip().upper()
        target_slug = (data.get("target_slug") or "").strip()
        target_title = (data.get("target_title") or page_type).strip()
        duration = max(0, min(7200, int(data.get("duration_seconds") or 0)))
        scroll_pct = max(0, min(100, int(data.get("max_scroll_pct") or 0)))
        referrer = (data.get("referrer") or "Direct").strip()[:120]
        device_type = (data.get("device_type") or "Desktop").strip()
        os_name = (data.get("os_name") or "Linux").strip()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
        conn = get_db()
        try:
            existing = conn.execute(
                "SELECT id, duration_seconds, max_scroll_pct FROM analytics_pageviews WHERE visit_token = ?",
                (visit_token,)
            ).fetchone()
    
            if existing:
                new_dur = max(existing["duration_seconds"], duration)
                new_scroll = max(existing["max_scroll_pct"], scroll_pct)
                conn.execute("""
                UPDATE analytics_pageviews
                SET duration_seconds = ?, max_scroll_pct = ?, last_ping_at = ?
                WHERE visit_token = ?
                """, (new_dur, new_scroll, now_str, visit_token))
            else:
                conn.execute("""
                INSERT INTO analytics_pageviews (
                    visit_token, visitor_id, session_id, page_type, target_slug, target_title,
                    duration_seconds, max_scroll_pct, referrer, device_type, os_name, created_at, last_ping_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    visit_token, visitor_id, session_id, page_type, target_slug, target_title,
                    duration, scroll_pct, referrer, device_type, os_name, now_str, now_str
                ))
            conn.commit()
        except Exception:
            pass
        finally:
            conn.close()
        return jsonify({"ok": True})
    
    
    @app.route("/api/telemetry/event", methods=["POST"])
    @app.route("/api/v1/sync/action", methods=["POST"])
    def api_telemetry_event():
        data = request.get_json(force=True, silent=True) or {}
        visitor_id = (data.get("visitor_id") or "anon").strip()
        session_id = (data.get("session_id") or "sess").strip()
        event_type = (data.get("event_type") or "CLICK").strip().upper()
        source_page = (data.get("source_page") or "").strip()
        target_sku = (data.get("target_sku") or "").strip().upper()
        meta_info = (data.get("meta_info") or "").strip()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
        conn = get_db()
        try:
            conn.execute("""
            INSERT INTO analytics_events (
                visitor_id, session_id, event_type, source_page, target_sku, meta_info, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (visitor_id, session_id, event_type, source_page, target_sku, meta_info, now_str))
            conn.commit()
        except Exception:
            pass
        finally:
            conn.close()
        return jsonify({"ok": True})
    
    
    
    
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
    
