from datetime import datetime
from flask import request, jsonify
from database import get_db
from core.helpers import log_audit_event
from core.security import get_current_admin, admin_required

def register_admin_reviews_routes(app):
    @app.route("/api/admin/reviews", methods=["POST"])
    @admin_required
    def api_admin_save_review():
        admin = get_current_admin()
        data = request.get_json(force=True, silent=True) or {}
        review_id = data.get("id")
        author_name = (data.get("author_name") or "").strip()
        content = (data.get("content") or "").strip()
        if not author_name or not content:
            return jsonify({"error": "Author Name and Review Assessment Content are required."}), 400
    
        author_role = (data.get("author_role") or "Enterprise Security Operator").strip()
        author_org = (data.get("author_org") or "Verified Entity").strip()
        product_sku = (data.get("product_sku") or "").strip().upper()
        try:
            rating = max(1, min(5, int(data.get("rating") or 5)))
        except Exception:
            rating = 5
        title = (data.get("title") or "").strip()
        verified_badge = (data.get("verified_badge") or "● VERIFIED LICENSE DEPLOYMENT").strip()
        featured_manifesto = 1 if data.get("featured_manifesto") else 0
        created_at = (data.get("created_at") or "").strip()
        if not created_at:
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
        conn = get_db()
        if review_id and "featured_manifesto" not in data:
            curr = conn.execute("SELECT featured_manifesto FROM product_reviews WHERE id=?", (int(review_id),)).fetchone()
            if curr:
                featured_manifesto = curr["featured_manifesto"]
        product_id = None
        if product_sku:
            prod_row = conn.execute("SELECT id FROM products WHERE sku = ?", (product_sku,)).fetchone()
            if prod_row:
                product_id = prod_row["id"]
    
        try:
            if review_id:
                conn.execute("""
                UPDATE product_reviews SET
                    product_id=?, product_sku=?, author_name=?, author_role=?,
                    author_org=?, rating=?, title=?, content=?, verified_badge=?,
                    featured_manifesto=?, created_at=?
                WHERE id=?
                """, (
                    product_id, product_sku, author_name, author_role,
                    author_org, rating, title, content, verified_badge,
                    featured_manifesto, created_at, int(review_id)
                ))
                saved_id = int(review_id)
                log_audit_event(conn, admin["id"], admin["username"], "REVIEW_UPDATED", f"ID={saved_id} Author={author_name}")
            else:
                cur = conn.execute("""
                INSERT INTO product_reviews (
                    product_id, product_sku, author_name, author_role, author_org,
                    rating, title, content, verified_badge, featured_manifesto, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    product_id, product_sku, author_name, author_role, author_org,
                    rating, title, content, verified_badge, featured_manifesto, created_at
                ))
                saved_id = cur.lastrowid
                log_audit_event(conn, admin["id"], admin["username"], "REVIEW_CREATED", f"ID={saved_id} Author={author_name}")
            conn.commit()
        except Exception as exc:
            conn.close()
            return jsonify({"error": str(exc)}), 400
    
        conn.close()
        return jsonify({"ok": True, "id": saved_id})
    
    
    @app.route("/api/admin/reviews/<int:review_id>", methods=["DELETE"])
    @admin_required
    def api_admin_delete_review(review_id):
        admin = get_current_admin()
        conn = get_db()
        conn.execute("DELETE FROM product_reviews WHERE id = ?", (review_id,))
        log_audit_event(conn, admin["id"], admin["username"], "REVIEW_DELETED", f"ID={review_id}")
        conn.commit()
        conn.close()
        return jsonify({"ok": True})

    @app.route("/api/admin/reviews/curation", methods=["POST"])
    @admin_required
    def api_admin_save_reviews_curation():
        import json
        admin = get_current_admin()
        data = request.get_json(force=True, silent=True) or {}
        raw_list = data.get("reviews") or data.get("review_ids") or []
        clean_rev_ids = []
        for r in raw_list:
            s = str(r or "").strip()
            if s.isdigit() and int(s) > 0:
                clean_rev_ids.append(int(s))

        conn = get_db()
        # Save JSON array
        conn.execute(
            "INSERT INTO settings (key, value) VALUES ('home_featured_reviews_json', ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (json.dumps(clean_rev_ids),)
        )
        # Save numbered keys
        for idx in range(1, 13):
            val = str(clean_rev_ids[idx - 1]) if idx <= len(clean_rev_ids) else ""
            conn.execute(
                f"INSERT INTO settings (key, value) VALUES ('home_featured_review_{idx}', ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (val,)
            )

        # Synchronize product_reviews table featured_manifesto flag
        conn.execute("UPDATE product_reviews SET featured_manifesto = 0")
        if clean_rev_ids:
            placeholders = ",".join("?" for _ in clean_rev_ids)
            conn.execute(f"UPDATE product_reviews SET featured_manifesto = 1 WHERE id IN ({placeholders})", clean_rev_ids)

        log_audit_event(
            conn,
            admin["id"],
            admin["username"],
            "HOME_REVIEWS_CURATION_UPDATED",
            f"Admin updated homepage client reviews showcase ({len(clean_rev_ids)} reviews): {clean_rev_ids}"
        )
        conn.commit()
        conn.close()
        return jsonify({
            "ok": True,
            "message": f"Homepage reviews showcase updated successfully with {len(clean_rev_ids)} reviews.",
            "reviews": clean_rev_ids
        })
    
    
