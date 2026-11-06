import os
import time
import uuid
import secrets
from datetime import datetime
from flask import request, jsonify
from werkzeug.utils import secure_filename
from database import get_db
from core.config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS, DEFAULT_ROBOTS_TXT
from core.helpers import log_audit_event, generate_sitemap_xml, render_robots_txt
from core.security import get_current_admin, master_admin_required, admin_required

def register_admin_theme_routes(app):
    @app.route("/api/admin/upload-image", methods=["POST"])
    @admin_required
    def api_admin_upload_image():
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded in request."}), 400
        file = request.files["file"]
        if not file or file.filename == "":
            return jsonify({"error": "No file selected."}), 400
    
        filename = secure_filename(file.filename)
        ext = os.path.splitext(filename)[1].lower()
        allowed_exts = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".ico"}
        if ext not in allowed_exts:
            return jsonify({"error": f"Unsupported format '{ext}'. Allowed: {', '.join(allowed_exts)}"}), 400

        # Disallow executable SVG vectors with embedded JavaScript or active event listeners
        if ext == ".svg":
            content = file.read()
            file.seek(0)
            lowered = content.lower()
            dangerous_patterns = [b"<script", b"javascript:", b"onload=", b"onerror=", b"onclick=", b"<iframe", b"<object", b"<embed", b"xlink:href"]
            if any(p in lowered for p in dangerous_patterns):
                return jsonify({"error": "Security alert: SVG file contains active scripts or disallowed embedded elements."}), 400
    
        upload_dir = os.path.join(app.root_path, "static", "uploads")
        os.makedirs(upload_dir, exist_ok=True)
    
        unique_name = f"asset_{int(time.time())}_{uuid.uuid4().hex[:8]}{ext}"
        dest_path = os.path.join(upload_dir, unique_name)
        file.save(dest_path)
    
        file_url = f"/static/uploads/{unique_name}"
        admin = get_current_admin()
        conn = get_db()
        log_audit_event(conn, admin["id"], admin["username"], "IMAGE_UPLOADED", f"Uploaded media asset: {unique_name}")
        conn.commit()
        conn.close()
    
        return jsonify({"ok": True, "url": file_url, "filename": unique_name})
    
    
    
    
    @app.route("/api/admin/theme", methods=["POST"])
    @master_admin_required
    def api_admin_save_theme():
        admin = get_current_admin()
        data = request.get_json(force=True, silent=True) or {}
        payload = data.get("settings") if isinstance(data.get("settings"), dict) else data
        conn = get_db()
        for key, val in payload.items():
            if key in ("csrf_token",):
                continue
            conn.execute(
                "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (str(key).strip(), str(val).strip() if val is not None else "")
            )
        log_audit_event(conn, admin["id"], admin["username"], "THEME_UPDATED", f"Updated visual theme & content ({len(payload)} fields)")
        conn.commit()
        conn.close()
        return jsonify({"ok": True, "message": "Visual theme and page content saved successfully."})
    
    
    
    
    @app.route("/api/admin/home-curation", methods=["POST"])
    @master_admin_required
    def api_admin_save_home_curation():
        admin = get_current_admin()
        data = request.get_json(force=True, silent=True) or {}
        conn = get_db()
    
        updates = {}
        # Accept either { "products": [id1, id2, id3, id4], "posts": [p1, p2, p3, p4] }
        # or direct keys { "home_featured_product_1": val, ... }
        if "products" in data and isinstance(data["products"], list):
            for idx, pid in enumerate(data["products"][:4], start=1):
                updates[f"home_featured_product_{idx}"] = str(pid or "").strip()
        if "posts" in data and isinstance(data["posts"], list):
            for idx, pid in enumerate(data["posts"][:4], start=1):
                updates[f"home_featured_post_{idx}"] = str(pid or "").strip()

        for k in (
            "home_featured_product_1", "home_featured_product_2", "home_featured_product_3", "home_featured_product_4",
            "home_featured_post_1", "home_featured_post_2", "home_featured_post_3", "home_featured_post_4"
        ):
            if k in data:
                updates[k] = str(data[k] or "").strip()

        if "reviews" in data and isinstance(data["reviews"], list):
            clean_rev_ids = []
            for r in data["reviews"]:
                s = str(r or "").strip()
                if s.isdigit() and int(s) > 0:
                    clean_rev_ids.append(int(s))
            updates["home_featured_reviews_json"] = json.dumps(clean_rev_ids)
            for idx in range(1, 13):
                val = str(clean_rev_ids[idx - 1]) if idx <= len(clean_rev_ids) else ""
                updates[f"home_featured_review_{idx}"] = val
            
            # Sync product_reviews table featured_manifesto column
            conn.execute("UPDATE product_reviews SET featured_manifesto = 0")
            if clean_rev_ids:
                placeholders = ",".join("?" for _ in clean_rev_ids)
                conn.execute(f"UPDATE product_reviews SET featured_manifesto = 1 WHERE id IN ({placeholders})", clean_rev_ids)
    
        for key, val in updates.items():
            conn.execute(
                "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (key, val)
            )
    
        log_audit_event(
            conn,
            admin["id"],
            admin["username"],
            "HOME_CURATION_UPDATED",
            f"Master admin updated 4 products & 4 journals showcase serials: {updates}"
        )
        conn.commit()
        conn.close()
        return jsonify({"ok": True, "message": "Homepage 4 Products & 4 Journals showcase updated successfully.", "curation": updates})

    @app.route("/api/admin/seo/robots", methods=["POST"])
    @master_admin_required
    def api_admin_save_robots_txt():
        admin = get_current_admin()
        data = request.get_json(force=True, silent=True) or {}
        reset_default = bool(data.get("reset_default", False))
        if reset_default:
            robots_content = DEFAULT_ROBOTS_TXT
        else:
            robots_content = data.get("robots_txt_content")
            if robots_content is None:
                robots_content = DEFAULT_ROBOTS_TXT
            else:
                robots_content = str(robots_content).strip()

        site_url = data.get("seo_site_url")
        conn = get_db()
        conn.execute(
            "INSERT INTO settings (key, value) VALUES ('robots_txt_content', ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (robots_content,)
        )
        if site_url is not None:
            conn.execute(
                "INSERT INTO settings (key, value) VALUES ('seo_site_url', ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (str(site_url).strip().rstrip("/"),)
            )
        conn.commit()
        rendered_robots = render_robots_txt(conn)
        try:
            static_robots_path = os.path.join(app.root_path, "static", "robots.txt")
            with open(static_robots_path, "w", encoding="utf-8") as f:
                f.write(rendered_robots)
        except Exception:
            pass
        log_audit_event(conn, admin["id"], admin["username"], "ROBOTS_TXT_UPDATED", f"Updated robots.txt ({len(robots_content)} bytes)")
        conn.commit()
        conn.close()
        return jsonify({
            "ok": True,
            "robots_txt_content": robots_content,
            "rendered_robots_txt": rendered_robots,
            "message": "robots.txt directives saved and deployed live at /robots.txt."
        })

    @app.route("/api/admin/seo/generate-sitemap", methods=["POST"])
    @master_admin_required
    def api_admin_generate_sitemap():
        admin = get_current_admin()
        data = request.get_json(force=True, silent=True) or {}
        base_url = (data.get("base_url") or data.get("seo_site_url") or "").strip().rstrip("/")
        include_aliases = bool(data.get("include_aliases", True))

        conn = get_db()
        if "seo_site_url" in data or "base_url" in data:
            conn.execute(
                "INSERT INTO settings (key, value) VALUES ('seo_site_url', ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (base_url,)
            )
            conn.commit()

        result = generate_sitemap_xml(conn, base_url=base_url or None, include_aliases=include_aliases)
        xml_content = result["xml"]
        stats = result["stats"]

        conn.execute(
            "INSERT INTO settings (key, value) VALUES ('sitemap_xml_content', ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (xml_content,)
        )
        conn.execute(
            "INSERT INTO settings (key, value) VALUES ('sitemap_last_generated', ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (stats["generated_at"],)
        )
        conn.execute(
            "INSERT INTO settings (key, value) VALUES ('sitemap_url_count', ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (str(stats["total_urls"]),)
        )
        try:
            static_sitemap_path = os.path.join(app.root_path, "static", "sitemap.xml")
            with open(static_sitemap_path, "w", encoding="utf-8") as f:
                f.write(xml_content)
        except Exception:
            pass

        log_audit_event(
            conn,
            admin["id"],
            admin["username"],
            "SITEMAP_GENERATED",
            f"Generated sitemap.xml with {stats['total_urls']} URLs ({stats['core_routes_count']} routes, {stats['products_count']} products, {stats['posts_count']} journal posts)"
        )
        conn.commit()
        conn.close()
        return jsonify({
            "ok": True,
            "sitemap_xml": xml_content,
            "urls": result["urls"],
            "stats": stats,
            "message": f"Generated sitemap.xml with {stats['total_urls']} public URLs ({stats['products_count']} products, {stats['posts_count']} journal dispatches)."
        })

    @app.route("/api/admin/seo/sitemap", methods=["POST"])
    @master_admin_required
    def api_admin_save_sitemap_xml():
        admin = get_current_admin()
        data = request.get_json(force=True, silent=True) or {}
        xml_content = (data.get("sitemap_xml_content") or "").strip()
        if not xml_content or "<urlset" not in xml_content:
            return jsonify({"error": "Invalid sitemap XML: must contain a <urlset> root element."}), 400

        url_count = xml_content.count("<url>")
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = get_db()
        conn.execute(
            "INSERT INTO settings (key, value) VALUES ('sitemap_xml_content', ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (xml_content,)
        )
        conn.execute(
            "INSERT INTO settings (key, value) VALUES ('sitemap_last_generated', ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (now_str,)
        )
        conn.execute(
            "INSERT INTO settings (key, value) VALUES ('sitemap_url_count', ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (str(url_count),)
        )
        try:
            static_sitemap_path = os.path.join(app.root_path, "static", "sitemap.xml")
            with open(static_sitemap_path, "w", encoding="utf-8") as f:
                f.write(xml_content)
        except Exception:
            pass
        log_audit_event(conn, admin["id"], admin["username"], "SITEMAP_UPDATED", f"Manually saved sitemap.xml ({url_count} URLs)")
        conn.commit()
        conn.close()
        return jsonify({
            "ok": True,
            "url_count": url_count,
            "last_generated": now_str,
            "message": f"Custom sitemap.xml saved and deployed live ({url_count} URLs)."
        })

    
    
