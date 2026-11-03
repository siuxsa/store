import os
import re
import math
import json
import secrets
from datetime import datetime
from urllib.parse import quote
from flask import request, session, render_template, redirect, url_for, jsonify, Response

from database import get_db
from core.helpers import (
    get_settings_dict, row_to_product, row_to_post, render_markdown_prose,
    process_post_smart_ads, log_audit_event, build_telegram_product_url,
    compute_pagination_pages
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
            for r in conn.execute("SELECT * FROM products WHERE status = 'PUBLISHED' ORDER BY id DESC").fetchall()
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
            for r in conn.execute("SELECT * FROM posts WHERE status = 'PUBLISHED' ORDER BY id DESC").fetchall()
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
    
        curated_review_ids = []
        rev_json_str = settings.get("home_featured_reviews_json")
        if rev_json_str:
            try:
                parsed = json.loads(rev_json_str)
                if isinstance(parsed, list):
                    curated_review_ids = [int(x) for x in parsed if str(x).isdigit() and int(x) > 0]
            except Exception:
                pass

        if not curated_review_ids:
            for i in range(1, 13):
                v = settings.get(f"home_featured_review_{i}")
                if v and str(v).isdigit() and int(v) > 0:
                    curated_review_ids.append(int(v))

        manifesto_reviews = []
        if curated_review_ids:
            all_revs_map = {r["id"]: dict(r) for r in conn.execute("SELECT * FROM product_reviews").fetchall()}
            for rid in curated_review_ids:
                if rid in all_revs_map:
                    manifesto_reviews.append(all_revs_map[rid])

        if not manifesto_reviews:
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
        page_str = request.args.get("page", "1").strip()

        conn = get_db()
        settings = get_settings_dict(conn)
        rows = conn.execute("SELECT * FROM products WHERE status = 'PUBLISHED' ORDER BY featured DESC, id ASC").fetchall()
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

        try:
            per_page = int(settings.get("products_per_page", 8))
            if per_page < 1:
                per_page = 8
        except (ValueError, TypeError):
            per_page = 8

        try:
            current_page = int(page_str)
            if current_page < 1:
                current_page = 1
        except (ValueError, TypeError):
            current_page = 1

        total_items = len(filtered)
        total_pages = max(1, math.ceil(total_items / per_page))
        if current_page > total_pages:
            current_page = total_pages

        start_idx = (current_page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_products = filtered[start_idx:end_idx]

        start_item = (start_idx + 1) if total_items > 0 else 0
        end_item = min(end_idx, total_items)
        page_numbers = compute_pagination_pages(current_page, total_pages)

        def make_page_url(page_num):
            args = {}
            if category_filter:
                args["category"] = category_filter
            if type_filter:
                args["type"] = type_filter
            if q:
                args["q"] = q
            if page_num > 1:
                args["page"] = page_num
            return url_for("shop", **args)

        return render_template(
            "shop.html",
            products=paginated_products,
            all_count=len(all_products),
            total_items=total_items,
            start_item=start_item,
            end_item=end_item,
            categories=categories,
            current_category=category_filter,
            current_type=type_filter,
            search_query=q,
            current_page=current_page,
            total_pages=total_pages,
            per_page=per_page,
            has_prev=(current_page > 1),
            has_next=(current_page < total_pages),
            prev_page=(current_page - 1),
            next_page=(current_page + 1),
            page_numbers=page_numbers,
            make_page_url=make_page_url,
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

        product = row_to_product(row)
        is_draft = (product.get("status") or "PUBLISHED").upper() == "DRAFT"
        admin = get_current_admin(conn)
        if is_draft and not admin:
            conn.close()
            return redirect(url_for("shop"))

        if not is_draft:
            try:
                conn.execute("UPDATE products SET views_count = views_count + 1 WHERE id = ?", (row["id"],))
                conn.commit()
            except Exception:
                pass

        settings = get_settings_dict(conn)
        product["telegram_buy_url"] = build_telegram_product_url(product, settings)

        all_posts = [row_to_post(r) for r in conn.execute("SELECT * FROM posts WHERE status = 'PUBLISHED' ORDER BY id DESC").fetchall()]
        related_posts = [p for p in all_posts if product["sku"] in p["related_sku_list"] or product["sku"] in p["content"]]
        if not related_posts:
            related_posts = all_posts[:2]

        other_products = [
            row_to_product(r)
            for r in conn.execute("SELECT * FROM products WHERE id != ? AND status = 'PUBLISHED' ORDER BY featured DESC LIMIT 3", (product["id"],)).fetchall()
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
            is_draft_preview=is_draft,
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
        page_str = request.args.get("page", "1").strip()

        conn = get_db()
        settings = get_settings_dict(conn)
        all_posts = [row_to_post(r) for r in conn.execute("SELECT * FROM posts WHERE status = 'PUBLISHED' ORDER BY featured DESC, id DESC").fetchall()]
        products_by_sku = {
            r["sku"]: row_to_product(r)
            for r in conn.execute("SELECT * FROM products WHERE status = 'PUBLISHED'").fetchall()
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

        try:
            per_page = int(settings.get("journal_per_page", 4))
            if per_page < 1:
                per_page = 4
        except (ValueError, TypeError):
            per_page = 4

        try:
            current_page = int(page_str)
            if current_page < 1:
                current_page = 1
        except (ValueError, TypeError):
            current_page = 1

        total_items = len(filtered)
        total_pages = max(1, math.ceil(total_items / per_page))
        if current_page > total_pages:
            current_page = total_pages

        start_idx = (current_page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_posts = filtered[start_idx:end_idx]

        for p in paginated_posts:
            p["linked_products"] = [products_by_sku[s] for s in p["related_sku_list"] if s in products_by_sku]

        start_item = (start_idx + 1) if total_items > 0 else 0
        end_item = min(end_idx, total_items)
        page_numbers = compute_pagination_pages(current_page, total_pages)

        def make_page_url(page_num):
            args = {}
            if severity_filter:
                args["severity"] = severity_filter
            if category_filter:
                args["category"] = category_filter
            if q:
                args["q"] = q
            if page_num > 1:
                args["page"] = page_num
            return url_for("blog", **args)

        return render_template(
            "blog.html",
            posts=paginated_posts,
            all_count=len(all_posts),
            total_items=total_items,
            start_item=start_item,
            end_item=end_item,
            categories=categories,
            current_severity=severity_filter,
            current_category=category_filter,
            search_query=q,
            current_page=current_page,
            total_pages=total_pages,
            per_page=per_page,
            has_prev=(current_page > 1),
            has_next=(current_page < total_pages),
            prev_page=(current_page - 1),
            next_page=(current_page + 1),
            page_numbers=page_numbers,
            make_page_url=make_page_url,
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

        post = row_to_post(row)
        is_draft = (post.get("status") or "PUBLISHED").upper() == "DRAFT"
        admin = get_current_admin(conn)
        if is_draft and not admin:
            conn.close()
            return redirect(url_for("blog"))

        if not is_draft:
            try:
                conn.execute("UPDATE posts SET views = views + 1 WHERE id = ?", (row["id"],))
                conn.commit()
            except Exception:
                pass

        settings = get_settings_dict(conn)
        all_prods = [row_to_product(r) for r in conn.execute("SELECT * FROM products WHERE status = 'PUBLISHED'").fetchall()]
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
            for r in conn.execute("SELECT * FROM posts WHERE id != ? AND status = 'PUBLISHED' ORDER BY id DESC LIMIT 3", (post["id"],)).fetchall()
        ]
        conn.close()

        return render_template(
            "post_detail.html",
            post=post,
            comments=comments,
            linked_products=linked_products,
            more_posts=more_posts,
            is_draft_preview=is_draft,
            page_type="BLOG_POST",
            target_slug=post["slug"],
            target_title=post["title"]
        )
    
    
    
    
    @app.route("/api/posts/<int:post_id>/comments", methods=["POST"])
    def api_add_post_comment(post_id):
        admin = get_current_admin()
        user = get_current_user()

        # Enforce authentication: only logged-in operators or admins can submit verification notes
        if not user and not admin:
            if request.is_json:
                return jsonify({
                    "ok": False,
                    "error": "AUTH_REQUIRED",
                    "message": "Authentication required. Please log in as an operator to submit technical verification notes."
                }), 401
            return redirect(url_for("login_page", next=request.referrer or url_for("blog")))

        data = request.get_json(force=True, silent=True) or {}
        if not data and request.form:
            data = request.form

        body = (data.get("comment_body") or data.get("body") or "").strip()
        if not body or len(body) < 3:
            if request.is_json:
                return jsonify({"error": "Comment cannot be empty."}), 400
            return redirect(request.referrer or url_for("blog"))

        if admin:
            author_name = (data.get("author_name") or admin["username"]).strip()
            author_role = "ZERO-DAY RESEARCH UNIT"
            user_id = admin["id"]
        else:
            author_name = user["username"]
            author_role = user.get("role") or "VERIFIED OPERATOR"
            user_id = user["id"]

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = get_db()
        saved_comment_id = None
        # All operator comments are PENDING until an admin approves them in the Admin Dashboard
        comment_status = "PENDING"
        try:
            cur = conn.execute("""
            INSERT INTO post_comments (post_id, user_id, author_name, author_role, body, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (post_id, user_id, author_name, author_role, body, comment_status, now_str))
            saved_comment_id = cur.lastrowid
            log_audit_event(conn, user_id, author_name, "COMMENT_SUBMITTED", f"Post ID={post_id} Comment ID={saved_comment_id} Status={comment_status}")
            conn.commit()
        except Exception as exc:
            pass
        finally:
            conn.close()

        if request.is_json:
            return jsonify({
                "ok": True,
                "status": comment_status,
                "message": "Verification report submitted to operational control. Awaiting administrator approval before publication."
            })
        return redirect((request.referrer or url_for("blog")) + "?comment_status=pending#verification-log")
    
    
    
    
    @app.route("/request", methods=["GET"])
    @app.route("/request-tool", methods=["GET"])
    def request_tool_page():
        settings = get_settings_dict()
        user = get_current_user()
        return render_template(
            "request_tool.html",
            site_settings=settings,
            current_user=user,
            page_type="REQUEST",
            target_slug="request-tool",
            target_title="Custom Tool & Exploit Sourcing Desk"
        )

    @app.route("/api/request-tool", methods=["POST"])
    def api_submit_tool_request():
        data = request.get_json(force=True, silent=True) or {}
        tool_name = (data.get("tool_name") or "").strip()
        contact_telegram = (data.get("contact_telegram") or "").strip()
        contact_email = (data.get("contact_email") or "").strip()
        category = (data.get("category") or "EXPLOIT_TOOLKIT").strip()
        urgency = (data.get("urgency") or "STANDARD").strip()
        budget_range = (data.get("budget_range") or "FLEXIBLE").strip()
        technical_specs = (data.get("technical_specs") or "").strip()
        preferred_contact = (data.get("preferred_contact") or "TELEGRAM").strip()

        if not tool_name:
            return jsonify({"error": "Please enter the tool, license, or exploit name you are requesting."}), 400
        if len(tool_name) > 200:
            return jsonify({"error": "Tool name exceeds maximum length (200 characters)."}), 400
        if not contact_telegram and not contact_email:
            return jsonify({"error": "Please provide your Telegram handle or Email so our concierge desk can reach you."}), 400

        user = get_current_user()
        user_id = user["id"] if user else None
        
        request_id = f"REQ-{secrets.randbelow(90000) + 10000}"
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ip_addr = request.headers.get("X-Forwarded-For", request.remote_addr or "127.0.0.1").split(",")[0].strip()

        conn = get_db()
        conn.execute("""
            INSERT INTO tool_requests (
                request_id, user_id, tool_name, category, contact_telegram, contact_email,
                preferred_contact, urgency, budget_range, technical_specs, status, admin_notes,
                ip_address, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDING', '', ?, ?, ?)
        """, (
            request_id, user_id, tool_name, category, contact_telegram, contact_email,
            preferred_contact, urgency, budget_range, technical_specs, ip_addr, now_str, now_str
        ))
        conn.commit()
        conn.close()

        return jsonify({
            "ok": True,
            "request_id": request_id,
            "message": "Custom tool sourcing request submitted successfully."
        })

    @app.route("/orders", methods=["GET"])
    @app.route("/orders/<path:order_number>", methods=["GET"])
    def order_lookup(order_number=None):
        if session.get("user_id"):
            return redirect(url_for("user_vault"))
        return redirect(url_for("request_tool_page"))

    @app.route("/favicon.ico", methods=["GET"])
    def site_favicon():
        settings = get_settings_dict()
        fav = settings.get("site_favicon")
        if fav:
            return redirect(fav)
        static_fav = os.path.join(app.root_path, "static", "favicon.ico")
        if os.path.exists(static_fav):
            return app.send_static_file("favicon.ico")
        svg_icon = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect width="100" height="100" fill="#050505"/><polygon points="50,15 85,85 15,85" fill="#00e5ff"/></svg>"""
        return Response(svg_icon, mimetype="image/svg+xml")
    
    
    
