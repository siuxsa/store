import re
import json
from datetime import datetime
from flask import request, jsonify
from database import get_db
from core.helpers import log_audit_event, render_markdown_prose, process_post_smart_ads, row_to_product, get_settings_dict
from core.security import get_current_admin, admin_required

def register_admin_posts_routes(app):
    @app.route("/api/admin/posts", methods=["POST"])
    @admin_required
    def api_admin_save_post():
        admin = get_current_admin()
        data = request.get_json(force=True, silent=True) or {}
        post_id = data.get("id")
        title = (data.get("title") or "").strip()
        slug = (data.get("slug") or "").strip().lower()
    
        if not title:
            return jsonify({"error": "Article Title is required."}), 400
    
        conn = get_db()
        if post_id and not slug:
            existing = conn.execute("SELECT slug FROM posts WHERE id = ?", (int(post_id),)).fetchone()
            if existing and existing["slug"]:
                slug = existing["slug"]
    
        if not slug and title:
            slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    
        category = (data.get("category") or "Zero-Day Advisories").strip()
        severity = (data.get("severity") or "CRITICAL").strip().upper()
        cve_id = (data.get("cve_id") or "").strip().upper()
        cvss_score = (data.get("cvss_score") or "").strip()
        author = (data.get("author") or "ZERO-DAY UNIT").strip()
        read_time = (data.get("read_time") or "6 MIN READ").strip()
        summary = (data.get("summary") or "").strip()
        content = data.get("content") or ""
        related_skus = (data.get("related_skus") or "").strip().upper()
        ad_mode = (data.get("ad_mode") or "ALL").strip().upper()
        try:
            ad_count = int(data.get("ad_count") if data.get("ad_count") is not None else 1)
        except Exception:
            ad_count = 1
        ad_placement = (data.get("ad_placement") or "MIDDLE").strip().upper()
        try:
            ad_paragraph_interval = int(data.get("ad_paragraph_interval") if data.get("ad_paragraph_interval") is not None else 4)
        except Exception:
            ad_paragraph_interval = 4
        ad_custom_pitch = (data.get("ad_custom_pitch") or "").strip()
        featured = 1 if data.get("featured") else 0
        if post_id and "featured" not in data:
            curr = conn.execute("SELECT featured FROM posts WHERE id=?", (int(post_id),)).fetchone()
            if curr:
                featured = curr["featured"]
        status = (data.get("status") or "PUBLISHED").strip().upper()
        if status not in ("PUBLISHED", "DRAFT"):
            status = "PUBLISHED"
        image_url = (data.get("image_url") or "").strip()
        meta_title = (data.get("meta_title") or "").strip()
        meta_desc = (data.get("meta_desc") or "").strip()
        meta_keywords = (data.get("meta_keywords") or "").strip()
        og_image = (data.get("og_image") or "").strip()
        custom_js = (data.get("custom_js") or "").strip()
        # RBAC: Only Master Administrator (role=ADMIN) can supply or alter executable custom_js
        if admin.get("role") != "ADMIN":
            if post_id:
                existing_post = conn.execute("SELECT custom_js FROM posts WHERE id=?", (int(post_id),)).fetchone()
                custom_js = existing_post["custom_js"] if existing_post else ""
            else:
                custom_js = ""
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            saved_id = None
            if post_id:
                conn.execute("""
                UPDATE posts SET
                    title=?, slug=?, category=?, severity=?, cve_id=?, cvss_score=?,
                    author=?, read_time=?, summary=?, content=?, related_skus=?,
                    ad_mode=?, ad_count=?, ad_placement=?, ad_paragraph_interval=?,
                    ad_custom_pitch=?, featured=?, status=?, image_url=?,
                    meta_title=?, meta_desc=?, meta_keywords=?, og_image=?, custom_js=?
                WHERE id=?
                """, (
                    title, slug, category, severity, cve_id, cvss_score,
                    author, read_time, summary, content, related_skus,
                    ad_mode, ad_count, ad_placement, ad_paragraph_interval,
                    ad_custom_pitch, featured, status, image_url,
                    meta_title, meta_desc, meta_keywords, og_image, custom_js, int(post_id)
                ))
                saved_id = int(post_id)
                log_audit_event(conn, admin["id"], admin["username"], "POST_UPDATED", f"Slug={slug} STATUS={status}")
            else:
                cur = conn.execute("""
                INSERT INTO posts (
                    title, slug, category, severity, cve_id, cvss_score,
                    author, read_time, summary, content, related_skus,
                    ad_mode, ad_count, ad_placement, ad_paragraph_interval,
                    ad_custom_pitch, featured, status, views, published_at, image_url,
                    meta_title, meta_desc, meta_keywords, og_image, custom_js
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    title, slug, category, severity, cve_id, cvss_score,
                    author, read_time, summary, content, related_skus,
                    ad_mode, ad_count, ad_placement, ad_paragraph_interval,
                    ad_custom_pitch, featured, status, now_str, image_url,
                    meta_title, meta_desc, meta_keywords, og_image, custom_js
                ))
                saved_id = cur.lastrowid
                action_tag = "POST_PUBLISHED" if status == "PUBLISHED" else "POST_DRAFTED"
                log_audit_event(conn, admin["id"], admin["username"], action_tag, f"Slug={slug} STATUS={status}")
            conn.commit()
        except Exception as exc:
            conn.close()
            return jsonify({"error": str(exc)}), 400

        conn.close()
        return jsonify({"ok": True, "slug": slug, "id": saved_id, "status": status})


    @app.route("/api/admin/posts/<int:post_id>/toggle-status", methods=["POST"])
    @admin_required
    def api_admin_toggle_post_status(post_id):
        admin = get_current_admin()
        conn = get_db()
        row = conn.execute("SELECT status, slug, title FROM posts WHERE id = ?", (post_id,)).fetchone()
        if not row:
             conn.close()
             return jsonify({"error": "Post not found"}), 404
        current_status = (row["status"] or "PUBLISHED").strip().upper()
        new_status = "DRAFT" if current_status == "PUBLISHED" else "PUBLISHED"
        conn.execute("UPDATE posts SET status = ? WHERE id = ?", (new_status, post_id))
        log_audit_event(conn, admin["id"], admin["username"], "POST_STATUS_TOGGLED", f"Slug={row['slug']} {current_status}->{new_status}")
        conn.commit()
        conn.close()
        return jsonify({"ok": True, "new_status": new_status, "id": post_id})


    @app.route("/api/admin/posts/<int:post_id>", methods=["DELETE"])
    @admin_required
    def api_admin_delete_post(post_id):
        admin = get_current_admin()
        conn = get_db()
        conn.execute("DELETE FROM posts WHERE id = ?", (post_id,))
        log_audit_event(conn, admin["id"], admin["username"], "POST_DELETED", f"ID={post_id}")
        conn.commit()
        conn.close()
        return jsonify({"ok": True})
    
    
    
    
    @app.route("/api/admin/posts/preview", methods=["POST"])
    @admin_required
    def api_admin_preview_post():
        data = request.get_json(force=True, silent=True) or {}
        conn = get_db()
        settings = get_settings_dict(conn)
        all_prods = [row_to_product(r) for r in conn.execute("SELECT * FROM products").fetchall()]
        products_by_sku = {p["sku"].upper(): p for p in all_prods}
        conn.close()
    
        skus = [s.strip().upper() for s in (data.get("related_skus") or "").split(",") if s.strip()]
        try:
            ad_count = int(data.get("ad_count") if data.get("ad_count") is not None else 1)
        except Exception:
            ad_count = 1
        ad_placement = (data.get("ad_placement") or "MIDDLE").strip().upper()
        try:
            ad_paragraph_interval = int(data.get("ad_paragraph_interval") if data.get("ad_paragraph_interval") is not None else 4)
        except Exception:
            ad_paragraph_interval = 4
    
        mock_post = {
            "slug": data.get("slug") or "preview-post",
            "content": data.get("content") or "",
            "ad_mode": data.get("ad_mode") or "ALL",
            "ad_count": ad_count,
            "ad_placement": ad_placement,
            "ad_paragraph_interval": ad_paragraph_interval,
            "related_sku_list": skus
        }
        rendered_html = process_post_smart_ads(mock_post, products_by_sku, settings, all_prods=all_prods)
        return jsonify({"ok": True, "rendered_html": rendered_html})
    
    
