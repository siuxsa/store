from flask import request, jsonify
from database import get_db
from core.helpers import log_audit_event
from core.security import get_current_admin, admin_required

def register_admin_comments_routes(app):
    @app.route("/api/admin/comments/<int:comment_id>/status", methods=["POST"])
    @admin_required
    def api_admin_update_comment_status(comment_id):
        admin = get_current_admin()
        data = request.get_json(force=True, silent=True) or {}
        new_status = (data.get("status") or "APPROVED").strip().upper()
        if new_status not in ("APPROVED", "PENDING", "REJECTED"):
            return jsonify({"error": "Invalid status."}), 400
        conn = get_db()
        conn.execute("UPDATE post_comments SET status = ? WHERE id = ?", (new_status, comment_id))
        log_audit_event(conn, admin["id"], admin["username"], f"COMMENT_{new_status}", f"Comment ID={comment_id}")
        conn.commit()
        conn.close()
        return jsonify({"ok": True, "status": new_status})
    
    
    @app.route("/api/admin/comments/<int:comment_id>", methods=["DELETE"])
    @admin_required
    def api_admin_delete_comment(comment_id):
        admin = get_current_admin()
        conn = get_db()
        conn.execute("DELETE FROM post_comments WHERE id = ?", (comment_id,))
        log_audit_event(conn, admin["id"], admin["username"], "COMMENT_DELETED", f"Comment ID={comment_id}")
        conn.commit()
        conn.close()
        return jsonify({"ok": True})
    
    
