import re
import json
from datetime import datetime
from urllib.parse import quote
from flask import request, session, render_template, redirect, url_for, jsonify

from database import get_db
from core.helpers import (
    get_settings_dict, row_to_product, row_to_post, render_markdown_prose,
    process_post_smart_ads, log_audit_event, build_telegram_product_url
)
from core.security import get_current_user, get_current_admin

def register_frontend_routes(app):
    
    @app.route("/about")
    def about_page():
        return render_template(
            "about.html",
            page_type="ABOUT",
            target_slug="about",
            target_title="About // Architecture & Systems"
        )
    
    
    
    
    @app.route("/")
    def index():
        conn = get_db()
        settings = get_settings_dict(conn)
        all_products_raw = [
            row_to_product(r)
            for r in conn.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
        ]
        prod_by_id = {str(p["id"]): p for p in all_products_raw}
        prod_by_sku = {p["sku"]: p for p in all_products_raw}
    
        # Curate exactly 4 products by Serial (1 -> 4)
        curated_products = []
        seen_prod_ids = set()
        for i in range(1, 5):
            val = str(settings.get(f"home_featured_product_{i}", "")).strip()
            matched = prod_by_id.get(val) or prod_by_sku.get(val)
            if matched and matched["id"] not in seen_prod_ids:
                curated_products.append(matched)
                seen_prod_ids.add(matched["id"])
    
        # Fallback to catalog products if fewer than 4 were configured
        if len(curated_products) < 4:
            for p in all_products_raw:
                if p["id"] not in seen_prod_ids:
                    curated_products.append(p)
                    seen_prod_ids.add(p["id"])
                    if len(curated_products) == 4:
                        break
    
        all_posts_raw = [
            row_to_post(r)
            for r in conn.execute("SELECT * FROM posts ORDER BY id DESC").fetchall()
        ]
        post_by_id = {str(p["id"]): p for p in all_posts_raw}
        post_by_slug = {p["slug"]: p for p in all_posts_raw}
    
        # Curate exactly 4 journal posts by Serial (1 -> 4)
        curated_posts = []
        seen_post_ids = set()
        for i in range(1, 5):
            val = str(settings.get(f"home_featured_post_{i}", "")).strip()
            matched = post_by_id.get(val) or post_by_slug.get(val)
            if matched and matched["id"] not in seen_post_ids:
                curated_posts.append(matched)
                seen_post_ids.add(matched["id"])
    
        # Fallback to latest posts if fewer than 4 were configured
        if len(curated_posts) < 4:
            for p in all_posts_raw:
                if p["id"] not in seen_post_ids:
                    curated_posts.append(p)
                    seen_post_ids.add(p["id"])
                    if len(curated_posts) == 4:
                        break
    
        manifesto_reviews = [
            dict(r)
            for r in conn.execute(
                "SELECT * FROM product_reviews WHERE featured_manifesto = 1 OR product_sku = '' ORDER BY id DESC LIMIT 6"
            ).fetchall()
        ]
        if not manifesto_reviews:
            manifesto_reviews = [
                dict(r)
                for r in conn.execute("SELECT * FROM product_reviews ORDER BY id DESC LIMIT 4").fetchall()
            ]
        conn.close()
        return render_template(
            "index.html",
            products=all_products_raw,
            featured_products=curated_products[:4],
            posts=curated_posts[:4],
            manifesto_reviews=manifesto_reviews,
            page_type="HOME",
            target_slug="home",
            target_title="Home // Threat Matrix"
        )
    
    
    
    
    @app.route("/arsenal")
    @app.route("/shop")
    def shop():
        category_filter = request.args.get("category", "").strip()
        type_filter = request.args.get("type", "").strip()
        q = request.args.get("q", "").strip()
    
        conn = get_db()
        rows = conn.execute("SELECT * FROM products ORDER BY featured DESC, id ASC").fetchall()
        all_products = [row_to_product(r) for r in rows]
        categories = sorted(list({p["category"] for p in all_products}))
        conn.close()
    
        filtered = all_products
        if category_filter:
            filtered = [p for p in filtered if p["category"].lower() == category_filter.lower()]
        if type_filter:
            filtered = [p for p in filtered if p["product_type"].lower() == type_filter.lower()]
        if q:
            ql = q.lower()
            filtered = [
                p for p in filtered
                if ql in p["name"].lower() or ql in p["sku"].lower() or ql in p["short_desc"].lower() or ql in p["category"].lower()
            ]
    
        return render_template(
            "shop.html",
            products=filtered,
            all_count=len(all_products),
            categories=categories,
            current_category=category_filter,
            current_type=type_filter,
            search_query=q,
            page_type="SHOP",
            target_slug="arsenal",
            target_title="Digital Arsenal Catalog"
        )
    
    
    
    
    @app.route("/arsenal/<slug>")
    @app.route("/product/<slug>")
    @app.route("/shop/<slug>")
    def product_detail(slug):
        conn = get_db()
        row = conn.execute("SELECT * FROM products WHERE slug = ? OR sku = ?", (slug, slug.upper())).fetchone()
        if not row:
            conn.close()
            return redirect(url_for("shop"))
    
        try:
            conn.execute("UPDATE products SET views_count = views_count + 1 WHERE id = ?", (row["id"],))
            conn.commit()
        except Exception:
            pass
    
        product = row_to_product(row)
        settings = get_settings_dict(conn)
        product["telegram_buy_url"] = build_telegram_product_url(product, settings)
    
        all_posts = [row_to_post(r) for r in conn.execute("SELECT * FROM posts ORDER BY id DESC").fetchall()]
        related_posts = [p for p in all_posts if product["sku"] in p["related_sku_list"] or product["sku"] in p["content"]]
        if not related_posts:
            related_posts = all_posts[:2]
    
        other_products = [
            row_to_product(r)
            for r in conn.execute("SELECT * FROM products WHERE id != ? ORDER BY featured DESC LIMIT 3", (product["id"],)).fetchall()
        ]
    
        product_reviews = [
            dict(r)
            for r in conn.execute(
                "SELECT * FROM product_reviews WHERE product_sku = ? OR product_id = ? OR product_sku = '' ORDER BY id DESC",
                (product["sku"], product["id"])
            ).fetchall()
        ]
        if not product_reviews:
            product_reviews = [
                dict(r)
                for r in conn.execute("SELECT * FROM product_reviews ORDER BY id DESC LIMIT 3").fetchall()
            ]
        avg_rating = round(sum(r["rating"] for r in product_reviews) / len(product_reviews), 1) if product_reviews else 5.0
    
        conn.close()
    
        return render_template(
            "product_detail.html",
            product=product,
            related_posts=related_posts,
            other_products=other_products,
            reviews=product_reviews,
            avg_rating=avg_rating,
            review_count=len(product_reviews),
            page_type="PRODUCT",
            target_slug=product["slug"],
            target_title=product["name"]
        )
    
    
    
    
    @app.route("/intel")
    @app.route("/journal")
    def blog():
        severity_filter = request.args.get("severity", "").strip().upper()
        category_filter = request.args.get("category", "").strip()
        q = request.args.get("q", "").strip()
    
        conn = get_db()
        all_posts = [row_to_post(r) for r in conn.execute("SELECT * FROM posts ORDER BY featured DESC, id DESC").fetchall()]
        products_by_sku = {
            r["sku"]: row_to_product(r)
            for r in conn.execute("SELECT * FROM products").fetchall()
        }
        categories = sorted(list({p["category"] for p in all_posts}))
        conn.close()
    
        filtered = all_posts
        if severity_filter:
            filtered = [p for p in filtered if p["severity"].upper() == severity_filter]
        if category_filter:
            filtered = [p for p in filtered if p["category"].lower() == category_filter.lower()]
        if q:
            ql = q.lower()
            filtered = [
                p for p in filtered
                if ql in p["title"].lower() or ql in p["summary"].lower() or ql in p["cve_id"].lower() or ql in p["content"].lower()
            ]
    
        for p in filtered:
            p["linked_products"] = [products_by_sku[s] for s in p["related_sku_list"] if s in products_by_sku]
    
        return render_template(
            "blog.html",
            posts=filtered,
            categories=categories,
            current_severity=severity_filter,
            current_category=category_filter,
            search_query=q,
            page_type="BLOG_INDEX",
            target_slug="intel",
            target_title="Threat Intelligence Wire"
        )
    
    
    
    
    @app.route("/intel/<slug>")
    @app.route("/journal/<slug>")
    def post_detail(slug):
        conn = get_db()
        row = conn.execute("SELECT * FROM posts WHERE slug = ?", (slug,)).fetchone()
        if not row:
            conn.close()
            return redirect(url_for("blog"))
    
        try:
            conn.execute("UPDATE posts SET views = views + 1 WHERE id = ?", (row["id"],))
            conn.commit()
        except Exception:
            pass
    
        post = row_to_post(row)
        settings = get_settings_dict(conn)
        all_prods = [row_to_product(r) for r in conn.execute("SELECT * FROM products").fetchall()]
        products_by_sku = {p["sku"].upper(): p for p in all_prods}
    
        for p in all_prods:
            p["telegram_buy_url"] = build_telegram_product_url(p, settings)
    
        post["rendered_content"] = process_post_smart_ads(post, products_by_sku, settings, all_prods=all_prods)
        linked_products = [products_by_sku[s.upper()] for s in post["related_sku_list"] if s.upper() in products_by_sku]
        if not linked_products and all_prods:
            linked_products = all_prods[:2]
    
        comments = [
            dict(c)
            for c in conn.execute("SELECT * FROM post_comments WHERE post_id = ? AND status = 'APPROVED' ORDER BY id DESC", (post["id"],)).fetchall()
        ]
    
        more_posts = [
            row_to_post(r)
            for r in conn.execute("SELECT * FROM posts WHERE id != ? ORDER BY id DESC LIMIT 3", (post["id"],)).fetchall()
        ]
        conn.close()
    
        return render_template(
            "post_detail.html",
            post=post,
            comments=comments,
            linked_products=linked_products,
            more_posts=more_posts,
            page_type="BLOG_POST",
            target_slug=post["slug"],
            target_title=post["title"]
        )
    
    
    
    
    @app.route("/api/posts/<int:post_id>/comments", methods=["POST"])
    def api_add_post_comment(post_id):
        data = request.get_json(force=True, silent=True) or {}
        if not data and request.form:
            data = request.form
    
        body = (data.get("comment_body") or data.get("body") or "").strip()
        if not body or len(body) < 3:
            if request.is_json:
                return jsonify({"error": "Comment cannot be empty."}), 400
            return redirect(request.referrer or url_for("blog"))
    
        author_name = (data.get("author_name") or "").strip()
        author_role = (data.get("author_role") or "SECURITY AUDITOR").strip()
    
        admin = get_current_admin()
        user = get_current_user()
        if admin:
            author_name = author_name or admin["username"]
            author_role = "ZERO-DAY RESEARCH UNIT"
            user_id = admin["id"]
        elif user:
            author_name = author_name or user["username"]
            author_role = "VERIFIED OPERATOR"
            user_id = user["id"]
        else:
            author_name = author_name or "ANON_OPERATOR"
            user_id = None
    
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = get_db()
        saved_comment_id = None
        # User comments are PENDING until an admin approves them in the Admin Dashboard
        comment_status = "APPROVED" if admin else "PENDING"
        try:
            cur = conn.execute("""
            INSERT INTO post_comments (post_id, user_id, author_name, author_role, body, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (post_id, user_id, author_name, author_role, body, comment_status, now_str))
            saved_comment_id = cur.lastrowid
            log_audit_event(conn, user_id or (admin["id"] if admin else None), author_name, "COMMENT_SUBMITTED", f"Post ID={post_id} Comment ID={saved_comment_id} Status={comment_status}")
            conn.commit()
        except Exception as exc:
            pass
        finally:
            conn.close()
    
        if request.is_json:
            return jsonify({
                "ok": True,
                "status": comment_status,
                "message": "Verification note logged to operational control. Awaiting administrator approval before publication." if comment_status == "PENDING" else "Verification note published."
            })
        return redirect((request.referrer or url_for("blog")) + ("?comment_status=pending#verification-log" if comment_status == "PENDING" else "#verification-log"))
    
    
    
    
    @app.route("/orders")
    @app.route("/orders/<order_number>")
    def order_lookup(order_number=None):
        q_order = (order_number or request.args.get("order_number", "") or request.args.get("order_id", "")).strip().upper()
        order_data = None
        settings = get_settings_dict()
    
        if q_order:
            conn = get_db()
            row = conn.execute("SELECT * FROM orders WHERE UPPER(order_number) = ?", (q_order,)).fetchone()
            conn.close()
            if row:
                order_data = dict(row)
                try:
                    order_data["items"] = json.loads(order_data.get("items_json") or "[]")
                except Exception:
                    order_data["items"] = []
    
                tg_user = settings.get("telegram_user", "ZeroDayMatrixSupport").lstrip("@")
                prefix = settings.get("telegram_msg_prefix", "Hello! I want to purchase:")
                lines = [f"{i.get('qty', 1)}x {i.get('name')} (${float(i.get('price', 0)):.2f})" for i in order_data["items"]]
                msg = (
                    f"{prefix}\n"
                    f"Order Ticket: #{order_data['order_number']}\n"
                    f"Buyer Handle: {order_data['buyer_telegram']}\n"
                    f"Items: {', '.join(lines)}\n"
                    f"Total: ${float(order_data['total_amount']):.2f}\n"
                    f"Please send payment details to unlock my license/download."
                )
                order_data["telegram_url"] = f"https://t.me/{tg_user}?text={quote(msg)}"
                order_data["raw_message"] = msg
    
        return render_template(
            "order_lookup.html",
            order=order_data,
            searched_id=q_order,
            page_type="ORDERS",
            target_slug=q_order or "orders",
            target_title=f"Order Vault {q_order}" if q_order else "Order & License Vault"
        )
    
    
