from datetime import datetime
from flask import request, jsonify
from database import get_db
from core.helpers import log_audit_event
from core.security import get_current_admin, admin_required

def register_admin_tool_request_routes(app):
    @app.route("/api/admin/tool-requests", methods=["GET"])
    @admin_required
    def api_admin_get_tool_requests():
        conn = get_db()
        rows = conn.execute("SELECT * FROM tool_requests ORDER BY id DESC").fetchall()
        conn.close()
        return jsonify({
            "ok": True,
            "requests": [dict(r) for r in rows]
        })

    @app.route("/api/admin/tool-requests/<int:req_id>/status", methods=["POST"])
    @admin_required
    def api_admin_update_tool_request_status(req_id):
        admin = get_current_admin()
        data = request.get_json(force=True, silent=True) or {}
        new_status = (data.get("status") or "").strip().upper()
        admin_notes = data.get("admin_notes")

        allowed_statuses = ("PENDING", "IN_REVIEW", "SOURCING", "FULFILLED", "REJECTED")
        if new_status not in allowed_statuses:
            return jsonify({"error": f"Invalid status '{new_status}'. Allowed: {', '.join(allowed_statuses)}"}), 400

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = get_db()
        existing = conn.execute("SELECT * FROM tool_requests WHERE id = ?", (req_id,)).fetchone()
        if not existing:
            conn.close()
            return jsonify({"error": "Tool request not found."}), 404

        if admin_notes is not None:
            conn.execute(
                "UPDATE tool_requests SET status = ?, admin_notes = ?, updated_at = ? WHERE id = ?",
                (new_status, str(admin_notes).strip(), now_str, req_id)
            )
        else:
            conn.execute(
                "UPDATE tool_requests SET status = ?, updated_at = ? WHERE id = ?",
                (new_status, now_str, req_id)
            )

        log_audit_event(
            conn, admin["id"], admin["username"], "TOOL_REQUEST_UPDATED",
            f"Updated request #{existing['request_id']} ({existing['tool_name']}) status to {new_status}"
        )
        conn.commit()
        conn.close()

        return jsonify({
            "ok": True,
            "id": req_id,
            "request_id": existing["request_id"],
            "status": new_status,
            "message": f"Request #{existing['request_id']} updated to {new_status}."
        })

    @app.route("/api/admin/tool-requests/<int:req_id>", methods=["DELETE"])
    @admin_required
    def api_admin_delete_tool_request(req_id):
        admin = get_current_admin()
        conn = get_db()
        existing = conn.execute("SELECT * FROM tool_requests WHERE id = ?", (req_id,)).fetchone()
        if not existing:
            conn.close()
            return jsonify({"error": "Tool request not found."}), 404

        conn.execute("DELETE FROM tool_requests WHERE id = ?", (req_id,))
        log_audit_event(
            conn, admin["id"], admin["username"], "TOOL_REQUEST_DELETED",
            f"Deleted request #{existing['request_id']} ({existing['tool_name']})"
        )
        conn.commit()
        conn.close()

        return jsonify({
            "ok": True,
            "id": req_id,
            "message": f"Tool request #{existing['request_id']} deleted permanently."
        })
