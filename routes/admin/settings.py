import os
import io
import csv
import json
from datetime import datetime, timedelta
from flask import request, jsonify, make_response
from database import get_db, DB_PATH
from core.helpers import log_audit_event
from core.security import get_current_admin, master_admin_required

def register_admin_settings_routes(app):
    @app.route("/api/admin/settings", methods=["POST"])
    @master_admin_required
    def api_admin_save_settings():
        admin = get_current_admin()
        data = request.get_json(force=True, silent=True) or {}
        conn = get_db()
        for key, val in data.items():
            conn.execute(
                "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (str(key).strip(), str(val).strip())
            )
        log_audit_event(conn, admin["id"], admin["username"], "SETTINGS_UPDATED", "Updated global platform settings")
        conn.commit()
        conn.close()
        return jsonify({"ok": True, "message": "Global site & Telegram settings updated."})

    @app.route("/api/admin/data/stats", methods=["GET"])
    @master_admin_required
    def api_admin_data_stats():
        conn = get_db()
        cur = conn.cursor()
        counts = {
            "pageviews": cur.execute("SELECT COUNT(*) FROM analytics_pageviews").fetchone()[0],
            "events": cur.execute("SELECT COUNT(*) FROM analytics_events").fetchone()[0],
            "unique_visitors": cur.execute("SELECT COUNT(DISTINCT visitor_id) FROM analytics_pageviews").fetchone()[0],
            "unique_sessions": cur.execute("SELECT COUNT(DISTINCT session_id) FROM analytics_pageviews").fetchone()[0],
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
                rows = conn.execute("SELECT id, visitor_id, session_id, event_type, source_page, target_sku, meta_info, created_at FROM analytics_events ORDER BY id ASC").fetchall()
                cw.writerow(["ID", "Visitor ID", "Session ID", "Event Type", "Source Page", "Target SKU", "Metadata", "Timestamp"])
                for r in rows:
                    cw.writerow([r["id"], r["visitor_id"], r["session_id"], r["event_type"], r["source_page"], r["target_sku"], r["meta_info"], r["created_at"]])
                filename = f"zeroday_tracking_events_{timestamp}.csv"
            else:
                rows = conn.execute("SELECT id, visit_token, visitor_id, session_id, page_type, target_slug, target_title, duration_seconds, max_scroll_pct, referrer, device_type, os_name, created_at, last_ping_at FROM analytics_pageviews ORDER BY id ASC").fetchall()
                cw.writerow(["ID", "Visit Token", "Visitor ID", "Session ID", "Page Type", "Target Slug", "Target Title", "Duration (Seconds)", "Max Scroll %", "Referrer", "Device Type", "OS", "Created At", "Last Ping At"])
                for r in rows:
                    cw.writerow([r["id"], r["visit_token"], r["visitor_id"], r["session_id"], r["page_type"], r["target_slug"], r["target_title"], r["duration_seconds"], r["max_scroll_pct"], r["referrer"], r["device_type"], r["os_name"], r["created_at"], r["last_ping_at"]])
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
        data = request.get_json(force=True, silent=True) or {}
        action = (data.get("action") or data.get("target") or "").strip()
        older_than_days = data.get("older_than_days")

        # Telemetry-only safeguard: NEVER allow deletion of core website data (products, orders, reviews, comments, users)
        allowed_actions = ("analytics_all", "analytics_pageviews", "analytics_events", "vacuum")
        if action not in allowed_actions:
            return jsonify({"error": f"Invalid action '{action}'. Strict Data Isolation: Only visitor telemetry data can be purged through this system. Core website content (reviews, comments, products, orders) is strictly decoupled and protected."}), 400

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
                deleted_count = (c1 if c1 > 0 else 0) + (c2 if c2 > 0 else 0)
                details = f"Purged {deleted_count} total telemetry records ({c1} pageviews, {c2} events)" + (f" older than {older_than_days} days" if older_than_days else "")

            elif action == "analytics_pageviews":
                c = conn.execute(f"DELETE FROM analytics_pageviews{time_clause}", params).rowcount
                deleted_count = c if c > 0 else 0
                details = f"Purged {deleted_count} visitor pageview records" + (f" older than {older_than_days} days" if older_than_days else "")

            elif action == "analytics_events":
                c = conn.execute(f"DELETE FROM analytics_events{time_clause}", params).rowcount
                deleted_count = c if c > 0 else 0
                details = f"Purged {deleted_count} ad and tracking event records" + (f" older than {older_than_days} days" if older_than_days else "")

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
    
    
