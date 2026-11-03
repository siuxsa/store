import json
from flask import render_template
from database import get_db
from core.helpers import get_settings_dict, row_to_product, row_to_post, compute_analytics_summary
from core.security import get_current_admin, admin_required

def register_admin_panel_routes(app):
    @app.route("/admin")
    @admin_required
    def admin_panel():
        admin = get_current_admin()
        conn = get_db()
        settings = get_settings_dict(conn)
        products = [row_to_product(r) for r in conn.execute("SELECT * FROM products ORDER BY id DESC").fetchall()]
        posts = [row_to_post(r) for r in conn.execute("SELECT * FROM posts ORDER BY id DESC").fetchall()]
        orders = []
        for r in conn.execute("SELECT * FROM orders ORDER BY id DESC").fetchall():
            od = dict(r)
            try:
                od["items"] = json.loads(od.get("items_json") or "[]")
            except Exception:
                od["items"] = []
            orders.append(od)
    
        if admin["role"] == "ADMIN":
            users_list = [
                dict(u)
                for u in conn.execute("SELECT id, username, email, role, telegram_handle, is_active, last_login_at, created_at, device_hwid, last_ip FROM users ORDER BY id ASC").fetchall()
            ]
            audit_logs = [
                dict(a)
                for a in conn.execute("SELECT * FROM auth_audit_logs ORDER BY id DESC LIMIT 50").fetchall()
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
        conn.close()
    
        return render_template(
            "admin.html",
            admin=admin,
            current_admin=admin,
            settings=settings,
            settings_json=json.dumps(settings),
            products=products,
            posts=posts,
            orders=orders,
            users_list=users_list,
            audit_logs=audit_logs,
            banned_clients_list=banned_clients_list,
            reviews=reviews,
            comments_list=comments_list,
            pending_comments_count=pending_comments_count,
            tool_requests=tool_requests,
            pending_tool_requests_count=pending_tool_requests_count,
            stats=stats,
            analytics_summary=analytics_data.get("kpis", {}),
            analytics_data=analytics_data,
            analytics_data_json=json.dumps(analytics_data),
            page_type="ADMIN",
            target_slug="admin",
            target_title="Command Center // Admin"
        )
    
    
    # ==========================================
    # CHECKOUT & ORDER TICKET API
    # ==========================================
    
