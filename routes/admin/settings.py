from flask import request, jsonify
from database import get_db
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
    
    
