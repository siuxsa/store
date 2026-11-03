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
    
    
