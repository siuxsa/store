import re
import json
from datetime import datetime
from flask import request, jsonify
from database import get_db
from core.helpers import log_audit_event
from core.security import get_current_admin, admin_required

def register_admin_products_routes(app):
    @app.route("/api/admin/products", methods=["POST"])
    @admin_required
    def api_admin_save_product():
        admin = get_current_admin()
        data = request.get_json(force=True, silent=True) or {}
        prod_id = data.get("id")
        sku = (data.get("sku") or "").strip().upper()
        name = (data.get("name") or "").strip()
        slug = (data.get("slug") or "").strip().lower()
        if not slug and name:
            slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    
        if not sku or not name:
            return jsonify({"error": "SKU and Product Name are required."}), 400
    
        category = (data.get("category") or "Web & AppSec Licenses").strip()
        product_type = (data.get("product_type") or "LICENSE_KEY").strip().upper()
        price = float(data.get("price") or 0.0)
        retail_price = float(data.get("retail_price") or 0.0)
        version = (data.get("version") or "v2026.1").strip()
        license_duration = (data.get("license_duration") or "1-Year Pro License").strip()
        platform = (data.get("platform") or "Windows / Linux / macOS").strip()
        short_desc = (data.get("short_desc") or "").strip()
        description = (data.get("description") or "").strip()
        specs_raw = data.get("specs") or []
        if isinstance(specs_raw, str):
            specs_list = [line.strip() for line in specs_raw.split("\n") if line.strip()]
        else:
            specs_list = specs_raw
        specs_json = json.dumps(specs_list)
    
        faq_raw = data.get("faq")
        if faq_raw is None:
            faq_raw = data.get("faq_json")
        if isinstance(faq_raw, str):
            try:
                faq_list = json.loads(faq_raw)
            except Exception:
                faq_list = []
        elif isinstance(faq_raw, list):
            faq_list = faq_raw
        else:
            faq_list = []
        cleaned_faq = []
        for item in faq_list:
            if isinstance(item, dict):
                q = str(item.get("q") or "").strip()
                a = str(item.get("a") or "").strip()
                if q or a:
                    cleaned_faq.append({"q": q, "a": a})
        faq_json = json.dumps(cleaned_faq)
    
        sha256_hash = (data.get("sha256_hash") or "").strip()
        download_url = (data.get("download_url") or "").strip()

        raw_delivery_links = data.get("delivery_links")
        if raw_delivery_links is None:
            raw_delivery_links = data.get("delivery_links_json")
        if isinstance(raw_delivery_links, str):
            try:
                links_list = json.loads(raw_delivery_links)
            except Exception:
                links_list = []
        elif isinstance(raw_delivery_links, list):
            links_list = raw_delivery_links
        else:
            links_list = []
        cleaned_delivery_links = []
        for lk in links_list:
            if isinstance(lk, dict):
                l_url = str(lk.get("url") or "").strip()
                l_label = str(lk.get("label") or "").strip() or "Download Package"
                if l_url:
                    cleaned_delivery_links.append({"label": l_label, "url": l_url})
            elif isinstance(lk, str) and lk.strip():
                cleaned_delivery_links.append({"label": "Download Package", "url": lk.strip()})
        if not cleaned_delivery_links and download_url:
            cleaned_delivery_links.append({"label": f"{name} ({version})", "url": download_url})
        if cleaned_delivery_links and not download_url:
            download_url = cleaned_delivery_links[0]["url"]
        delivery_links_json = json.dumps(cleaned_delivery_links)
        delivery_message = (data.get("delivery_message") or "").strip()

        badge_text = (data.get("badge_text") or "INSTANT DELIVERY").strip()
        featured = 1 if data.get("featured") else 0
        status = (data.get("status") or "PUBLISHED").strip().upper()
        if status not in ("PUBLISHED", "DRAFT"):
            status = "PUBLISHED"
        image_url = (data.get("image_url") or "").strip()
        meta_title = (data.get("meta_title") or "").strip()
        meta_desc = (data.get("meta_desc") or "").strip()
        meta_keywords = (data.get("meta_keywords") or "").strip()
        og_image = (data.get("og_image") or "").strip()
        ad_headline = (data.get("ad_headline") or "").strip()
        ad_description = (data.get("ad_description") or "").strip()
        ad_badge = (data.get("ad_badge") or "").strip()
        ad_cta_text = (data.get("ad_cta_text") or "").strip()
        ad_image_url = (data.get("ad_image_url") or "").strip()
        custom_js = (data.get("custom_js") or "").strip()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = get_db()
        # RBAC: Only Master Administrator (role=ADMIN) can supply or alter executable custom_js
        if admin.get("role") != "ADMIN":
            if prod_id:
                existing_p = conn.execute("SELECT custom_js FROM products WHERE id=?", (int(prod_id),)).fetchone()
                custom_js = existing_p["custom_js"] if existing_p else ""
            else:
                custom_js = ""
        try:
            if prod_id:
                conn.execute("""
                UPDATE products SET
                    sku=?, name=?, slug=?, category=?, product_type=?, price=?, retail_price=?,
                    version=?, license_duration=?, platform=?, short_desc=?, description=?, specs_json=?, faq_json=?,
                    sha256_hash=?, download_url=?, delivery_links_json=?, delivery_message=?, badge_text=?, featured=?, status=?,
                    image_url=?, meta_title=?, meta_desc=?, meta_keywords=?, og_image=?,
                    ad_headline=?, ad_description=?, ad_badge=?, ad_cta_text=?, ad_image_url=?, custom_js=?
                WHERE id=?
                """, (
                    sku, name, slug, category, product_type, price, retail_price,
                    version, license_duration, platform, short_desc, description, specs_json, faq_json,
                    sha256_hash, download_url, delivery_links_json, delivery_message, badge_text, featured, status,
                    image_url, meta_title, meta_desc, meta_keywords, og_image,
                    ad_headline, ad_description, ad_badge, ad_cta_text, ad_image_url, custom_js, int(prod_id)
                ))
                log_audit_event(conn, admin["id"], admin["username"], "PRODUCT_UPDATED", f"SKU={sku} STATUS={status}")
            else:
                cur = conn.execute("""
                INSERT INTO products (
                    sku, name, slug, category, product_type, price, retail_price,
                    version, license_duration, platform, short_desc, description, specs_json, faq_json,
                    sha256_hash, download_url, delivery_links_json, delivery_message, badge_text, featured, status, views_count, created_at,
                    image_url, meta_title, meta_desc, meta_keywords, og_image,
                    ad_headline, ad_description, ad_badge, ad_cta_text, ad_image_url, custom_js
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    sku, name, slug, category, product_type, price, retail_price,
                    version, license_duration, platform, short_desc, description, specs_json, faq_json,
                    sha256_hash, download_url, delivery_links_json, delivery_message, badge_text, featured, status, now_str,
                    image_url, meta_title, meta_desc, meta_keywords, og_image,
                    ad_headline, ad_description, ad_badge, ad_cta_text, ad_image_url, custom_js
                ))
                saved_id = cur.lastrowid
                log_audit_event(conn, admin["id"], admin["username"], "PRODUCT_CREATED", f"SKU={sku} STATUS={status}")
            conn.commit()
        except Exception as exc:
            conn.close()
            return jsonify({"error": str(exc)}), 400

        conn.close()
        return jsonify({"ok": True, "id": int(prod_id) if prod_id else saved_id, "sku": sku, "status": status})


    @app.route("/api/admin/products/<int:prod_id>/toggle-status", methods=["POST"])
    @admin_required
    def api_admin_toggle_product_status(prod_id):
        admin = get_current_admin()
        conn = get_db()
        row = conn.execute("SELECT status, sku, name FROM products WHERE id = ?", (prod_id,)).fetchone()
        if not row:
             conn.close()
             return jsonify({"error": "Product not found"}), 404
        current_status = (row["status"] or "PUBLISHED").strip().upper()
        new_status = "DRAFT" if current_status == "PUBLISHED" else "PUBLISHED"
        conn.execute("UPDATE products SET status = ? WHERE id = ?", (new_status, prod_id))
        log_audit_event(conn, admin["id"], admin["username"], "PRODUCT_STATUS_TOGGLED", f"SKU={row['sku']} {current_status}->{new_status}")
        conn.commit()
        conn.close()
        return jsonify({"ok": True, "new_status": new_status, "id": prod_id})


    @app.route("/api/admin/products/<int:prod_id>", methods=["DELETE"])
    @admin_required
    def api_admin_delete_product(prod_id):
        admin = get_current_admin()
        conn = get_db()
        conn.execute("DELETE FROM products WHERE id = ?", (prod_id,))
        log_audit_event(conn, admin["id"], admin["username"], "PRODUCT_DELETED", f"ID={prod_id}")
        conn.commit()
        conn.close()
        return jsonify({"ok": True})
    
    
