from flask import request, jsonify
from database import get_db
from core.helpers import log_audit_event
from core.security import get_current_admin, admin_required

def register_admin_orders_routes(app):
    @app.route("/api/admin/orders/<int:order_id>", methods=["POST"])
    @admin_required
    def api_admin_update_order(order_id):
        admin = get_current_admin()
        data = request.get_json(force=True, silent=True) or {}
        status = (data.get("status") or "PENDING_TELEGRAM").strip().upper()
        license_info = (data.get("fulfilled_license_info") or "").strip()
    
        conn = get_db()
        conn.execute("""
        UPDATE orders SET status = ?, fulfilled_license_info = ? WHERE id = ?
        """, (status, license_info, order_id))
        log_audit_event(conn, admin["id"], admin["username"], "ORDER_UPDATED", f"Order ID={order_id}, Status={status}")
        conn.commit()
        conn.close()
        return jsonify({"ok": True})
    
    
    @app.route("/api/admin/orders/<int:order_id>", methods=["DELETE"])
    @admin_required
    def api_admin_delete_order(order_id):
        admin = get_current_admin()
        conn = get_db()
        conn.execute("DELETE FROM orders WHERE id = ?", (order_id,))
        log_audit_event(conn, admin["id"], admin["username"], "ORDER_DELETED", f"Order ID={order_id}")
        conn.commit()
        conn.close()
        return jsonify({"ok": True})
    
    
