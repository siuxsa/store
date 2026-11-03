import os
import time
import uuid
import secrets
from flask import request, jsonify
from werkzeug.utils import secure_filename
from database import get_db
from core.config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS
from core.helpers import log_audit_event
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
        allowed_exts = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}
        if ext not in allowed_exts:
            return jsonify({"error": f"Unsupported format '{ext}'. Allowed: {', '.join(allowed_exts)}"}), 400
    
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
    
    
