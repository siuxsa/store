from datetime import datetime
from flask import request, jsonify
from werkzeug.security import generate_password_hash
from database import get_db
from core.helpers import log_audit_event
from core.security import get_current_admin, master_admin_required

def register_admin_users_routes(app):
    @app.route("/api/admin/users/<int:target_user_id>/password", methods=["POST"])
    @master_admin_required
    def api_admin_change_user_password(target_user_id):
        admin = get_current_admin()
        data = request.get_json(force=True, silent=True) or {}
        new_pass = (data.get("password") or "").strip()
        if not new_pass or len(new_pass) < 6:
            return jsonify({"error": "Password must be at least 6 characters."}), 400
        conn = get_db()
        conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (generate_password_hash(new_pass), target_user_id))
        log_audit_event(conn, admin["id"], admin["username"], "USER_PASSWORD_RESET", f"TargetUserID={target_user_id}")
        conn.commit()
        conn.close()
        return jsonify({"ok": True, "message": "Password updated successfully."})
    
    
    @app.route("/api/admin/users/<int:target_user_id>/ban", methods=["POST"])
    @master_admin_required
    def api_admin_ban_user(target_user_id):
        if target_user_id == 1:
            return jsonify({"error": "Cannot ban the in-built Master Administrator."}), 400
        admin = get_current_admin()
        data = request.get_json(force=True, silent=True) or {}
        should_ban = bool(data.get("ban", True))
        reason = (data.get("reason") or "Administrative device blacklist").strip()
    
        conn = get_db()
        target_user = conn.execute("SELECT id, username, last_ip, device_hwid FROM users WHERE id = ?", (target_user_id,)).fetchone()
        if not target_user:
            conn.close()
            return jsonify({"error": "Target user not found."}), 404
    
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if should_ban:
            conn.execute("UPDATE users SET is_active = 0 WHERE id = ?", (target_user_id,))
            conn.execute("""
            INSERT INTO banned_clients (user_id, username, ip_address, device_hwid, reason, banned_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (target_user_id, target_user["username"], target_user["last_ip"] or "", target_user["device_hwid"] or "", reason, now_str))
            log_audit_event(conn, admin["id"], admin["username"], "USER_BANNED", f"TargetUser={target_user['username']}, HWID={target_user['device_hwid']}")
        else:
            conn.execute("UPDATE users SET is_active = 1 WHERE id = ?", (target_user_id,))
            conn.execute("DELETE FROM banned_clients WHERE user_id = ?", (target_user_id,))
            log_audit_event(conn, admin["id"], admin["username"], "USER_UNBANNED", f"TargetUser={target_user['username']}")
    
        conn.commit()
        conn.close()
        return jsonify({"ok": True, "is_active": 0 if should_ban else 1})
    
    
    @app.route("/api/admin/users/<int:target_user_id>/role", methods=["POST"])
    @master_admin_required
    def api_admin_change_user_role(target_user_id):
        if target_user_id == 1:
            return jsonify({"error": "Cannot alter the in-built Master Administrator role."}), 400
        admin = get_current_admin()
        data = request.get_json(force=True, silent=True) or {}
        new_role = (data.get("role") or "").strip().upper()
        if new_role not in ("MODERATOR", "CUSTOMER"):
            return jsonify({"error": "Invalid role. Only MODERATOR or CUSTOMER can be assigned."}), 400
    
        conn = get_db()
        conn.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, target_user_id))
        log_audit_event(conn, admin["id"], admin["username"], "USER_ROLE_CHANGED", f"TargetUserID={target_user_id}, NewRole={new_role}")
        conn.commit()
        conn.close()
        return jsonify({"ok": True, "role": new_role})
    
    
    @app.route("/api/admin/unban-identifier", methods=["POST"])
    @master_admin_required
    def api_admin_unban_identifier():
        admin = get_current_admin()
        data = request.get_json(force=True, silent=True) or {}
        ban_id = data.get("id")
        conn = get_db()
        b_row = conn.execute("SELECT * FROM banned_clients WHERE id = ?", (ban_id,)).fetchone()
        if b_row:
            if b_row["user_id"]:
                conn.execute("UPDATE users SET is_active = 1 WHERE id = ?", (b_row["user_id"],))
            conn.execute("DELETE FROM banned_clients WHERE id = ?", (ban_id,))
            log_audit_event(conn, admin["id"], admin["username"], "IDENTIFIER_UNBANNED", f"BanID={ban_id}")
            conn.commit()
        conn.close()
        return jsonify({"ok": True})
    
    
    @app.route("/api/admin/users/<int:target_user_id>", methods=["POST"])
    @master_admin_required
    def api_admin_update_user(target_user_id):
        admin_user = get_current_admin()
        data = request.get_json(force=True, silent=True) or {}
        is_active = 1 if data.get("is_active", True) else 0
        new_password = (data.get("new_password") or "").strip()
    
        # The in-built master admin account (ID 1) cannot be deactivated or converted
        if target_user_id == 1:
            if not is_active:
                return jsonify({"error": "The in-built master admin account cannot be deactivated."}), 400
            conn = get_db()
            if new_password:
                conn.execute(
                    "UPDATE users SET password_hash = ? WHERE id = 1",
                    (generate_password_hash(new_password),)
                )
                log_audit_event(conn, admin_user["id"], admin_user["username"], "ADMIN_PASSWORD_UPDATED", "Master admin password changed")
                conn.commit()
            conn.close()
            return jsonify({"ok": True})
    
        conn = get_db()
        target_user = conn.execute("SELECT * FROM users WHERE id = ?", (target_user_id,)).fetchone()
        if not target_user:
            conn.close()
            return jsonify({"error": "User not found."}), 404
    
        if new_password:
            conn.execute(
                "UPDATE users SET is_active = ?, password_hash = ? WHERE id = ?",
                (is_active, generate_password_hash(new_password), target_user_id)
            )
        else:
            conn.execute(
                "UPDATE users SET is_active = ? WHERE id = ?",
                (is_active, target_user_id)
            )
    
        if is_active == 0:
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn.execute("""
            INSERT INTO banned_clients (user_id, username, ip_address, device_hwid, reason, banned_at)
            VALUES (?, ?, ?, ?, 'Administrative status deactivation', ?)
            """, (target_user_id, target_user["username"], target_user["last_ip"] or "", target_user["device_hwid"] or "", now_str))
        else:
            conn.execute("DELETE FROM banned_clients WHERE user_id = ?", (target_user_id,))
    
        log_audit_event(conn, admin_user["id"], admin_user["username"], "USER_UPDATED", f"TargetUserID={target_user_id}, Active={is_active}")
        conn.commit()
        conn.close()
        return jsonify({"ok": True})
    
    
    @app.route("/api/admin/users/<int:target_user_id>", methods=["DELETE"])
    @master_admin_required
    def api_admin_delete_user(target_user_id):
        admin_user = get_current_admin()
        if target_user_id == 1:
            return jsonify({"error": "Cannot delete the in-built master admin account."}), 400
        conn = get_db()
        conn.execute("DELETE FROM users WHERE id = ?", (target_user_id,))
        conn.execute("DELETE FROM banned_clients WHERE user_id = ?", (target_user_id,))
        log_audit_event(conn, admin_user["id"], admin_user["username"], "USER_DELETED", f"TargetUserID={target_user_id}")
        conn.commit()
        conn.close()
        return jsonify({"ok": True})
