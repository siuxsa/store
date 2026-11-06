import os
import io
import csv
import json
from datetime import datetime, timedelta
from flask import request, jsonify, make_response
from database import get_db, DB_PATH
from core.helpers import log_audit_event, get_settings_dict
from core.security import (
    get_current_admin, master_admin_required,
    validate_admin_custom_path, get_admin_custom_path_from_settings,
    get_rate_limit_telemetry, reset_rate_limits
)

def register_admin_settings_routes(app):
    @app.route("/api/admin/settings", methods=["POST"])
    @master_admin_required
    def api_admin_save_settings():
        admin = get_current_admin()
        data = request.get_json(force=True, silent=True) or (request.form.to_dict() if request.form else {}) or {}

        # Validate custom admin path if included in payload
        if "admin_custom_path" in data:
            ok, cleaned_slug, err_msg = validate_admin_custom_path(data.get("admin_custom_path"))
            if not ok:
                return jsonify({"ok": False, "error": err_msg}), 400
            data["admin_custom_path"] = cleaned_slug

        # Normalize numeric rate-limit settings if provided
        int_bounds = {
            "rate_limit_login_max": (1, 10000, 8),
            "rate_limit_page_max": (1, 100000, 120),
            "rate_limit_api_max": (1, 100000, 60),
            "rate_limit_block_seconds": (1, 86400, 60),
        }
        for k, (lo, hi, default_v) in int_bounds.items():
            if k in data:
                try:
                    v = int(str(data[k]).strip())
                    data[k] = str(max(lo, min(hi, v)))
                except Exception:
                    data[k] = str(default_v)

        if "rate_limit_enabled" in data:
            val_s = str(data["rate_limit_enabled"]).strip().lower()
            data["rate_limit_enabled"] = "0" if val_s in ("0", "false", "off", "no") else "1"

        conn = get_db()
        for key, val in data.items():
            conn.execute(
                "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (str(key).strip(), str(val).strip())
            )
        updated_settings = get_settings_dict(conn)
        active_slug = get_admin_custom_path_from_settings(updated_settings)
        log_audit_event(
            conn,
            admin["id"],
            admin["username"],
            "SETTINGS_UPDATED",
            f"AdminPath=/{active_slug}, RateLimit={updated_settings.get('rate_limit_enabled')}, LoginMax={updated_settings.get('rate_limit_login_max')}/min, PageMax={updated_settings.get('rate_limit_page_max')}/min"
        )
        conn.commit()
        conn.close()
        return jsonify({
            "ok": True,
            "message": "System & security configuration updated.",
            "admin_custom_path": active_slug,
            "admin_panel_url": f"/{active_slug}",
            "admin_login_url": f"/{active_slug}/login"
        })

    @app.route("/api/admin/security/telemetry", methods=["GET"])
    @master_admin_required
    def api_admin_security_telemetry():
        conn = get_db()
        settings = get_settings_dict(conn)
        conn.close()
        active_slug = get_admin_custom_path_from_settings(settings)
        return jsonify({
            "ok": True,
            "telemetry": get_rate_limit_telemetry(),
            "admin_custom_path": active_slug,
            "admin_panel_url": f"/{active_slug}",
            "admin_login_url": f"/{active_slug}/login",
            "rate_limit_enabled": settings.get("rate_limit_enabled", "1"),
            "rate_limit_login_max": settings.get("rate_limit_login_max", "8"),
            "rate_limit_page_max": settings.get("rate_limit_page_max", "120"),
            "rate_limit_api_max": settings.get("rate_limit_api_max", "60"),
            "rate_limit_block_seconds": settings.get("rate_limit_block_seconds", "60")
        })

    @app.route("/api/admin/security/rate-limit-reset", methods=["POST"])
    @master_admin_required
    def api_admin_reset_rate_limits():
        admin = get_current_admin()
        data = request.get_json(force=True, silent=True) or {}
        target_ip = (data.get("ip") or "").strip() or None
        cleared = reset_rate_limits(target_ip=target_ip)
        conn = get_db()
        log_audit_event(
            conn,
            admin["id"],
            admin["username"],
            "RATE_LIMIT_RESET",
            f"Cleared rate limit buckets (TargetIP={target_ip or 'ALL'}, Count={cleared})"
        )
        conn.commit()
        conn.close()
        return jsonify({
            "ok": True,
            "cleared_count": cleared,
            "message": f"Cleared active rate limit counters and unblocked {target_ip or 'all IP addresses'}.",
            "telemetry": get_rate_limit_telemetry()
        })

    @app.route("/api/admin/data/stats", methods=["GET"])
    @master_admin_required
    def api_admin_data_stats():
        conn = get_db()
        cur = conn.cursor()
        counts = {
            "pageviews": cur.execute("SELECT COUNT(*) FROM analytics_pageviews WHERE page_type NOT IN ('ADMIN', 'AUTH')").fetchone()[0],
            "events": cur.execute("SELECT COUNT(*) FROM analytics_events").fetchone()[0],
            "unique_visitors": cur.execute("SELECT COUNT(DISTINCT visitor_id) FROM analytics_pageviews WHERE page_type NOT IN ('ADMIN', 'AUTH')").fetchone()[0],
            "unique_sessions": cur.execute("SELECT COUNT(DISTINCT session_id) FROM analytics_pageviews WHERE page_type NOT IN ('ADMIN', 'AUTH')").fetchone()[0],
            "orders": cur.execute("SELECT COUNT(*) FROM orders").fetchone()[0],
            "pipeline_revenue": cur.execute("SELECT COALESCE(SUM(total_amount), 0.0) FROM orders").fetchone()[0],
        }
        conn.close()
        size_bytes = os.path.getsize(DB_PATH) if os.path.exists(DB_PATH) else 0
        counts["db_size_kb"] = round(size_bytes / 1024, 1)
        return jsonify({"ok": True, "stats": counts})

    @app.route("/api/admin/analytics/export", methods=["GET"])
    @master_admin_required
    def api_admin_export_analytics():
        admin = get_current_admin()
        export_format = (request.args.get("format") or "json").lower().strip()
        export_type = (request.args.get("type") or "all").lower().strip()

        conn = get_db()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if export_format == "csv":
            si = io.StringIO()
            cw = csv.writer(si)

            if export_type == "events":
                rows = conn.execute("SELECT id, visitor_id, session_id, event_type, source_page, target_sku, meta_info, user_agent, ip_address, created_at FROM analytics_events ORDER BY id ASC").fetchall()
                cw.writerow(["ID", "Visitor ID", "Session ID", "Event Type", "Source Page", "Target SKU", "Metadata", "User Agent", "IP Address", "Timestamp"])
                for r in rows:
                    cw.writerow([r["id"], r["visitor_id"], r["session_id"], r["event_type"], r["source_page"], r["target_sku"], r["meta_info"], r["user_agent"], r["ip_address"], r["created_at"]])
                filename = f"zeroday_tracking_events_{timestamp}.csv"
            else:
                rows = conn.execute("SELECT id, visit_token, visitor_id, session_id, page_type, target_slug, target_title, duration_seconds, max_scroll_pct, referrer, device_type, os_name, user_agent, ip_address, created_at, last_ping_at FROM analytics_pageviews ORDER BY id ASC").fetchall()
                cw.writerow(["ID", "Visit Token", "Visitor ID", "Session ID", "Page Type", "Target Slug", "Target Title", "Duration (Seconds)", "Max Scroll %", "Referrer", "Device Type", "OS", "User Agent", "IP Address", "Created At", "Last Ping At"])
                for r in rows:
                    cw.writerow([r["id"], r["visit_token"], r["visitor_id"], r["session_id"], r["page_type"], r["target_slug"], r["target_title"], r["duration_seconds"], r["max_scroll_pct"], r["referrer"], r["device_type"], r["os_name"], r["user_agent"], r["ip_address"], r["created_at"], r["last_ping_at"]])
                filename = f"zeroday_pageviews_{timestamp}.csv"

            conn.close()
            output = make_response(si.getvalue())
            output.headers["Content-Disposition"] = f"attachment; filename={filename}"
            output.headers["Content-Type"] = "text/csv; charset=utf-8"
            return output

        else:
            pageviews = [dict(r) for r in conn.execute("SELECT * FROM analytics_pageviews ORDER BY id ASC").fetchall()]
            events = [dict(r) for r in conn.execute("SELECT * FROM analytics_events ORDER BY id ASC").fetchall()]
            conn.close()
            export_payload = {
                "system": "ZERODAY // ARSENAL & INTEL TELEMETRY EXPORT",
                "export_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "operator": admin["username"],
                "total_pageviews": len(pageviews),
                "total_events": len(events),
                "analytics_pageviews": pageviews,
                "analytics_events": events
            }
            output = make_response(json.dumps(export_payload, indent=2))
            output.headers["Content-Disposition"] = f"attachment; filename=zeroday_telemetry_export_{timestamp}.json"
            output.headers["Content-Type"] = "application/json; charset=utf-8"
            return output

    @app.route("/api/admin/data/purge", methods=["POST"])
    @master_admin_required
    def api_admin_purge_data():
        admin = get_current_admin()
        data = request.get_json(force=True, silent=True) or (request.form.to_dict() if request.form else {}) or {}
        action = (data.get("action") or data.get("target") or "").strip()
        older_than_days = data.get("older_than_days")

        # Telemetry & pipeline analytics safeguard: allow purging visitor telemetry, events, and test orders
        # Core site catalog (products, reviews, comments, operator accounts) remains strictly decoupled and protected
        allowed_actions = ("analytics_all", "analytics_pageviews", "analytics_events", "analytics_orders", "analytics_revenue", "vacuum")
        if action not in allowed_actions:
            return jsonify({"error": f"Invalid action '{action}'. Valid actions: {', '.join(allowed_actions)}"}), 400

        conn = get_db()
        deleted_count = 0
        details = ""

        time_clause = ""
        params = []
        if older_than_days is not None and str(older_than_days).isdigit() and int(older_than_days) > 0:
            cutoff = (datetime.now() - timedelta(days=int(older_than_days))).strftime("%Y-%m-%d %H:%M:%S")
            time_clause = " WHERE created_at < ?"
            params = [cutoff]

        try:
            if action == "analytics_all":
                c1 = conn.execute(f"DELETE FROM analytics_pageviews{time_clause}", params).rowcount
                c2 = conn.execute(f"DELETE FROM analytics_events{time_clause}", params).rowcount
                c3 = conn.execute(f"DELETE FROM orders{time_clause}", params).rowcount
                c1 = c1 if c1 > 0 else 0
                c2 = c2 if c2 > 0 else 0
                c3 = c3 if c3 > 0 else 0
                deleted_count = c1 + c2 + c3
                details = f"Purged {deleted_count} total records ({c1} pageviews, {c2} events, {c3} orders/pipeline earnings reset to $0.00)" + (f" older than {older_than_days} days" if older_than_days else "")

            elif action == "analytics_pageviews":
                c = conn.execute(f"DELETE FROM analytics_pageviews{time_clause}", params).rowcount
                deleted_count = c if c > 0 else 0
                details = f"Purged {deleted_count} visitor pageview records" + (f" older than {older_than_days} days" if older_than_days else "")

            elif action == "analytics_events":
                c = conn.execute(f"DELETE FROM analytics_events{time_clause}", params).rowcount
                deleted_count = c if c > 0 else 0
                details = f"Purged {deleted_count} ad and tracking event records" + (f" older than {older_than_days} days" if older_than_days else "")

            elif action in ("analytics_orders", "analytics_revenue"):
                c = conn.execute(f"DELETE FROM orders{time_clause}", params).rowcount
                deleted_count = c if c > 0 else 0
                details = f"Purged {deleted_count} orders (Pipeline earnings reset to $0.00)" + (f" older than {older_than_days} days" if older_than_days else "")

            elif action == "vacuum":
                conn.commit()
                conn.execute("VACUUM")
                conn.execute("REINDEX")
                details = "Database defragmented and free storage reclaimed (VACUUM & REINDEX complete)."
                log_audit_event(conn, admin["id"], admin["username"], "DATABASE_OPTIMIZED", details)
                conn.commit()
                conn.close()
                new_size = round((os.path.getsize(DB_PATH) if os.path.exists(DB_PATH) else 0) / 1024, 1)
                return jsonify({
                    "ok": True,
                    "action": action,
                    "deleted_count": 0,
                    "message": details,
                    "db_size_kb": new_size
                })

            conn.commit()
            if data.get("auto_vacuum", True):
                try:
                    conn.execute("VACUUM")
                except Exception:
                    pass

            log_audit_event(conn, admin["id"], admin["username"], "TELEMETRY_PURGED", f"{action}: {details}")
            conn.commit()
        except Exception as exc:
            conn.close()
            return jsonify({"error": str(exc)}), 500

        conn.close()
        new_size = round((os.path.getsize(DB_PATH) if os.path.exists(DB_PATH) else 0) / 1024, 1)
        return jsonify({
            "ok": True,
            "action": action,
            "deleted_count": deleted_count,
            "message": details,
            "db_size_kb": new_size
        })
    
    
