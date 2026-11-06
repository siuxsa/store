import json
import secrets
import random
from urllib.parse import quote
from datetime import datetime
from flask import request, jsonify

from database import get_db
from core.helpers import log_audit_event, get_settings_dict
from core.security import get_current_user

def register_orders_routes(app):
    @app.route("/api/checkout", methods=["POST"])
    def api_checkout():
        data = request.get_json(force=True, silent=True) or {}
        user = get_current_user()
        default_tg = user["telegram_handle"] if (user and user.get("telegram_handle")) else ""
    
        buyer_telegram = (data.get("buyer_telegram") or default_tg).strip()
        if not buyer_telegram or buyer_telegram == "@client_direct":
            return jsonify({"error": "Please enter your Telegram @username for order delivery."}), 400
        if not buyer_telegram.startswith("@") and "@" not in buyer_telegram:
            buyer_telegram = "@" + buyer_telegram
        buyer_note = (data.get("buyer_note") or "").strip()
        items = data.get("items") or []
    
        if not items:
            return jsonify({"error": "Your arsenal cart is empty."}), 400
    
        conn = get_db()
        settings = get_settings_dict(conn)
    
        total = 0.0
        normalized_items = []
        for item in items:
            if not isinstance(item, dict):
                conn.close()
                return jsonify({"error": "Invalid item payload in checkout."}), 400
            sku = (item.get("sku") or "").strip().upper()
            try:
                raw_qty = int(item.get("qty") or 1)
            except (ValueError, TypeError):
                raw_qty = 1
            qty = max(1, min(100, raw_qty))

            row = conn.execute("SELECT * FROM products WHERE UPPER(sku) = ? AND status = 'PUBLISHED'", (sku,)).fetchone()
            if not row:
                conn.close()
                return jsonify({"error": f"Product SKU '{sku}' is invalid or currently unavailable."}), 400

            price = float(row["price"] or 0.0)
            total += price * qty
            normalized_items.append({
                "sku": row["sku"],
                "name": row["name"],
                "version": row["version"] or "v2026.1",
                "price": price,
                "qty": qty
            })
    
        order_number = f"ORD-{random.randint(10000, 99999)}"
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
        conn.execute("""
        INSERT INTO orders (
            order_number, user_id, buyer_telegram, buyer_note, total_amount, status,
            items_json, fulfilled_license_info, created_at
        ) VALUES (?, ?, ?, ?, ?, 'PENDING_TELEGRAM', ?, '', ?)
        """, (
            order_number,
            user["id"] if user else None,
            buyer_telegram,
            buyer_note,
            total,
            json.dumps(normalized_items),
            now_str
        ))
        conn.commit()
        conn.close()
    
        tg_user = settings.get("telegram_user", "ZeroDayMatrixSupport").lstrip("@")
        prefix = settings.get("telegram_msg_prefix", "Hello ZeroDay Matrix! I want to purchase and activate the following order:")
        item_lines = "\n".join([f"• {i['qty']}x {i['name']} [{i['sku']}] — ${i['price']*i['qty']:.2f}" for i in normalized_items])
        msg = (
            f"{prefix}\n\n"
            f"[ORDER DISPATCH] #{order_number}\n"
            f"OPERATOR ID: {buyer_telegram}\n"
            f"{f'OPERATIONAL NOTE: {buyer_note}' + chr(10) if buyer_note else ''}"
            f"ARSENAL ASSETS:\n{item_lines}\n\n"
            f"TOTAL SETTLEMENT: ${total:.2f}\n"
            f"Please send payment details for instant license/download delivery."
        )
        tg_url = f"https://t.me/{tg_user}?text={quote(msg)}"
    
        return jsonify({
            "success": True,
            "ok": True,
            "order_number": order_number,
            "total_amount": total,
            "telegram_url": tg_url,
            "telegram_user": tg_user,
            "message_text": msg,
            "vault_url": "/vault"
        })
    
    
    # ==========================================
    # REAL-TIME TELEMETRY & ANALYTICS API
    # ==========================================
    
