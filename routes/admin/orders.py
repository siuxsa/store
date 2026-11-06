import json
from datetime import datetime
from flask import request, jsonify
from database import get_db
from core.helpers import log_audit_event, row_to_product
from core.security import get_current_admin, admin_required

def register_admin_orders_routes(app):
    @app.route("/api/admin/orders/<int:order_id>", methods=["POST"])
    @admin_required
    def api_admin_update_order(order_id):
        admin = get_current_admin()
        data = request.get_json(force=True, silent=True) or {}
        status = (data.get("status") or "PENDING_TELEGRAM").strip().upper()
        license_info = (data.get("fulfilled_license_info") or "").strip()
        use_defaults = bool(data.get("use_product_defaults"))

        conn = get_db()
        existing = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
        if not existing:
            conn.close()
            return jsonify({"error": "Order not found."}), 404

        existing_dict = dict(existing)

        # Parse incoming delivery_links if provided
        raw_links = data.get("delivery_links")
        has_explicit_links = "delivery_links" in data
        has_explicit_msg = "delivery_message" in data

        cleaned_links = []
        if has_explicit_links:
            if isinstance(raw_links, str):
                try:
                    raw_links = json.loads(raw_links)
                except Exception:
                    raw_links = []
            if isinstance(raw_links, list):
                for lk in raw_links:
                    if isinstance(lk, dict):
                        u_str = str(lk.get("url") or "").strip()
                        l_str = str(lk.get("label") or "").strip() or "Download Package"
                        if u_str:
                            cleaned_links.append({"label": l_str, "url": u_str})
                    elif isinstance(lk, str) and lk.strip():
                        cleaned_links.append({"label": "Download Package", "url": lk.strip()})
        else:
            try:
                prev_links = json.loads(existing_dict.get("delivery_links_json") or "[]")
                if isinstance(prev_links, list):
                    cleaned_links = prev_links
            except Exception:
                cleaned_links = []

        if has_explicit_msg:
            delivery_message = (data.get("delivery_message") or "").strip()
        else:
            delivery_message = (existing_dict.get("delivery_message") or "").strip()

        if "fulfilled_license_info" not in data:
            license_info = (existing_dict.get("fulfilled_license_info") or "").strip()

        # Auto-populate from product defaults when completing order if requested or if empty
        if use_defaults or (status == "COMPLETED" and not cleaned_links and not delivery_message and not has_explicit_links and not has_explicit_msg):
            try:
                items = json.loads(existing_dict.get("items_json") or "[]")
            except Exception:
                items = []
            default_links = []
            default_msgs = []
            seen_urls = set()
            for it in items:
                sku = (it.get("sku") or "").strip().upper()
                if not sku:
                    continue
                prod_row = conn.execute("SELECT * FROM products WHERE UPPER(sku) = ?", (sku,)).fetchone()
                if prod_row:
                    p_obj = row_to_product(prod_row, include_private=True)
                    for plk in (p_obj.get("delivery_links") or []):
                        u_str = (plk.get("url") or "").strip()
                        if u_str and u_str not in seen_urls:
                            seen_urls.add(u_str)
                            default_links.append({
                                "label": plk.get("label") or f"{p_obj['name']} Download",
                                "url": u_str
                            })
                    p_msg = (p_obj.get("delivery_message") or "").strip()
                    if p_msg and p_msg not in default_msgs:
                        default_msgs.append(p_msg)
            if not cleaned_links and default_links:
                cleaned_links = default_links
            if not delivery_message and default_msgs:
                delivery_message = "\n\n".join(default_msgs)

        # Resolve user_id assignment for strict customer authentication
        target_user_id = existing_dict.get("user_id")
        if "user_id" in data:
            raw_uid = data.get("user_id")
            if raw_uid in (None, "", 0, "0"):
                target_user_id = None
            else:
                try:
                    target_user_id = int(raw_uid)
                except Exception:
                    pass
        elif not target_user_id:
            buyer_tg = (existing_dict.get("buyer_telegram") or "").strip()
            if buyer_tg and buyer_tg.lower() != "@anonymous_operator":
                matched_u = conn.execute(
                    "SELECT id FROM users WHERE role = 'CUSTOMER' AND LOWER(telegram_handle) = LOWER(?)",
                    (buyer_tg,)
                ).fetchone()
                if matched_u:
                    target_user_id = matched_u["id"]

        fulfilled_at = existing_dict.get("fulfilled_at") or ""
        if status == "COMPLETED" and not fulfilled_at:
            fulfilled_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elif status != "COMPLETED":
            fulfilled_at = ""

        delivery_links_json = json.dumps(cleaned_links)

        conn.execute("""
        UPDATE orders
        SET status = ?, fulfilled_license_info = ?, delivery_links_json = ?, delivery_message = ?, user_id = ?, fulfilled_at = ?
        WHERE id = ?
        """, (status, license_info, delivery_links_json, delivery_message, target_user_id, fulfilled_at, order_id))
        log_audit_event(
            conn,
            admin["id"],
            admin["username"],
            "ORDER_COMPLETED" if status == "COMPLETED" else "ORDER_UPDATED",
            f"Order ID={order_id}, Status={status}, Links={len(cleaned_links)}, UserID={target_user_id}"
        )
        conn.commit()
        conn.close()
        return jsonify({
            "ok": True,
            "status": status,
            "delivery_links": cleaned_links,
            "delivery_message": delivery_message,
            "fulfilled_license_info": license_info,
            "user_id": target_user_id
        })
    
    
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
    
    
