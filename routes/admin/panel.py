import os
import json
from flask import render_template, abort, redirect, request
from database import get_db, DB_PATH
from core.helpers import get_settings_dict, row_to_product, row_to_post, compute_analytics_summary, generate_sitemap_xml
from core.security import (
    get_current_admin, get_admin_custom_path_from_settings,
    get_admin_login_url, get_rate_limit_telemetry
)

def register_admin_panel_routes(app):
    @app.route("/admin", defaults={"admin_slug": "admin"})
    @app.route("/<string:admin_slug>")
    def admin_panel(admin_slug="admin"):
        conn = get_db()
        settings = get_settings_dict(conn)
        active_slug = get_admin_custom_path_from_settings(settings)

        # Stealth defense: if requested slug does not match active admin path, return 404
        if (admin_slug or "").strip().lower() != active_slug.lower():
            conn.close()
            abort(404)

        admin = get_current_admin(conn)
        if not admin or admin["role"] not in ("ADMIN", "MODERATOR"):
            conn.close()
            return redirect(get_admin_login_url(next_url=request.path))
        products = [row_to_product(r, include_private=True) for r in conn.execute("SELECT * FROM products ORDER BY id DESC").fetchall()]
        products_by_sku = {p["sku"].upper(): p for p in products if p.get("sku")}
        posts = [row_to_post(r) for r in conn.execute("SELECT * FROM posts ORDER BY id DESC").fetchall()]

        all_customers = [
            dict(u)
            for u in conn.execute("SELECT id, username, email, role, telegram_handle FROM users WHERE role = 'CUSTOMER' ORDER BY username ASC").fetchall()
        ]
        customers_by_id = {u["id"]: u for u in all_customers}
        customers_by_tg = {
            u["telegram_handle"].strip().lower(): u
            for u in all_customers
            if (u.get("telegram_handle") or "").strip() and u["telegram_handle"].strip().lower() != "@anonymous_operator"
        }

        orders = []
        for r in conn.execute("SELECT * FROM orders ORDER BY id DESC").fetchall():
            od = dict(r)
            try:
                od["items"] = json.loads(od.get("items_json") or "[]")
            except Exception:
                od["items"] = []

            try:
                raw_links = json.loads(od.get("delivery_links_json") or "[]")
                if not isinstance(raw_links, list):
                    raw_links = []
            except Exception:
                raw_links = []
            cleaned_links = []
            for lk in raw_links:
                if isinstance(lk, dict) and (lk.get("url") or "").strip():
                    cleaned_links.append({
                        "label": (lk.get("label") or "").strip() or "Download Link",
                        "url": lk["url"].strip()
                    })
                elif isinstance(lk, str) and lk.strip():
                    cleaned_links.append({"label": "Download Link", "url": lk.strip()})
            od["delivery_links"] = cleaned_links
            od["delivery_message"] = (od.get("delivery_message") or "").strip()

            # Compute default delivery links & message from the ordered product(s)
            default_links = []
            default_msgs = []
            seen_urls = set()
            for it in od["items"]:
                it_sku = (it.get("sku") or "").strip().upper()
                p_match = products_by_sku.get(it_sku)
                if p_match:
                    for plk in (p_match.get("delivery_links") or []):
                        u_str = (plk.get("url") or "").strip()
                        if u_str and u_str not in seen_urls:
                            seen_urls.add(u_str)
                            default_links.append({
                                "label": plk.get("label") or f"{p_match['name']} Download",
                                "url": u_str
                            })
                    p_msg = (p_match.get("delivery_message") or "").strip()
                    if p_msg and p_msg not in default_msgs:
                        default_msgs.append(p_msg)
            od["default_delivery_links"] = default_links
            od["default_delivery_message"] = "\n\n".join(default_msgs)

            # Resolve customer account ownership
            matched_user = None
            if od.get("user_id") and od["user_id"] in customers_by_id:
                matched_user = customers_by_id[od["user_id"]]
            else:
                tg_key = (od.get("buyer_telegram") or "").strip().lower()
                if tg_key and tg_key != "@anonymous_operator" and tg_key in customers_by_tg:
                    matched_user = customers_by_tg[tg_key]
            od["owner_user_id"] = matched_user["id"] if matched_user else (od.get("user_id") or None)
            od["owner_username"] = matched_user["username"] if matched_user else ""
            orders.append(od)
    
        if admin["role"] == "ADMIN":
            users_list = [
                dict(u)
                for u in conn.execute("SELECT id, username, email, role, telegram_handle, is_active, last_login_at, created_at, device_hwid, last_ip FROM users ORDER BY id ASC").fetchall()
            ]
            audit_logs = [
                dict(a)
                for a in conn.execute("SELECT * FROM auth_audit_logs ORDER BY id DESC").fetchall()
            ]
            banned_clients_list = [
                dict(b)
                for b in conn.execute("SELECT * FROM banned_clients ORDER BY id DESC").fetchall()
            ]
        else:
            users_list = []
            audit_logs = []
            banned_clients_list = []
    
        reviews = [
            dict(r)
            for r in conn.execute("SELECT * FROM product_reviews ORDER BY id DESC").fetchall()
        ]
        comments_list = [
            dict(c)
            for c in conn.execute("""
                SELECT c.*, p.title as post_title, p.slug as post_slug
                FROM post_comments c
                LEFT JOIN posts p ON c.post_id = p.id
                ORDER BY c.id DESC
            """).fetchall()
        ]
        pending_comments_count = sum(1 for c in comments_list if c.get("status") == "PENDING")

        tool_requests = [
            dict(r)
            for r in conn.execute("SELECT * FROM tool_requests ORDER BY id DESC").fetchall()
        ]
        pending_tool_requests_count = sum(1 for tr in tool_requests if tr.get("status") in ("PENDING", "NEW"))
    
        total_revenue = sum(float(o["total_amount"]) for o in orders if o.get("status") == "COMPLETED")
        pending_count = sum(1 for o in orders if o.get("status") == "PENDING_TELEGRAM")
        completed_count = sum(1 for o in orders if o.get("status") == "COMPLETED")
    
        stats = {
            "total_revenue": total_revenue,
            "completed_orders_count": completed_count,
            "pending_orders_count": pending_count,
            "products_count": len(products),
            "posts_count": len(posts),
            "users_count": len(users_list)
        }
    
        analytics_data = compute_analytics_summary(conn, days=14)
        sitemap_data = generate_sitemap_xml(conn)
        conn.close()

        db_size_kb = round(os.path.getsize(DB_PATH) / 1024, 1) if os.path.exists(DB_PATH) else 0

        return render_template(
            "admin.html",
            admin=admin,
            current_admin=admin,
            settings=settings,
            settings_json=json.dumps(settings).replace('</', '<\\/'),
            sitemap_data=sitemap_data,
            products=products,
            posts=posts,
            orders=orders,
            customers_list=all_customers,
            users_list=users_list,
            audit_logs=audit_logs,
            banned_clients_list=banned_clients_list,
            reviews=reviews,
            comments_list=comments_list,
            pending_comments_count=pending_comments_count,
            tool_requests=tool_requests,
            pending_tool_requests_count=pending_tool_requests_count,
            stats=stats,
            rate_limit_telemetry=get_rate_limit_telemetry(),
            analytics_summary=analytics_data.get("kpis", {}),
            analytics_data=analytics_data,
            analytics_data_json=json.dumps(analytics_data).replace("</", "<\\/"),
            db_size_kb=db_size_kb,
            page_type="ADMIN",
            target_slug="admin",
            target_title="Command Center // Admin"
        )
    
    
    # ==========================================
    # CHECKOUT & ORDER TICKET API
    # ==========================================
    
