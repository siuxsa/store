import requests
import sqlite3

BASE_URL = "http://127.0.0.1:5000"

def test_home_curation():
    print("=== TESTING HOMEPAGE 4 PRODUCTS & 4 JOURNALS CURATION WITH SERIALS ===")

    # 1. Test Admin Privilege Check: Unauthorized user / Non-admin should be rejected (403)
    anon_session = requests.Session()
    unauth_resp = anon_session.post(f"{BASE_URL}/api/admin/home-curation", json={})
    assert unauth_resp.status_code in (401, 403, 302), f"Expected 401/403/302 for unauth curation API, got {unauth_resp.status_code}"
    print("✓ Unauthenticated access to /api/admin/home-curation properly blocked.")

    # 2. Login as Master Admin
    admin_session = requests.Session()
    login_resp = admin_session.post(f"{BASE_URL}/admin/login", data={"identifier": "admin", "password": "Admin@2026"})
    assert login_resp.status_code == 200, f"Master Admin login failed: {login_resp.status_code}"
    print("✓ Master Admin authenticated successfully.")

    # 3. Verify Admin Panel HTML:
    # - old checkmark `id="pse-featured"` is REMOVED
    # - new curation slots exist
    admin_page = admin_session.get(f"{BASE_URL}/admin")
    assert admin_page.status_code == 200
    assert 'id="pse-featured"' not in admin_page.text, "Old feature checkmark 'pse-featured' must be removed from product editor!"
    print("✓ Verified old feature checkmark 'pse-featured' is successfully removed from product editor.")

    for s in range(1, 5):
        assert f'name="home_featured_product_{s}"' in admin_page.text, f"Slot product {s} missing from admin"
        assert f'name="home_featured_post_{s}"' in admin_page.text, f"Slot post {s} missing from admin"
    print("✓ Verified all 4 Product and 4 Journal serial dropdown slots exist in admin panel.")

    # 4. Fetch list of available products and posts from database
    conn = sqlite3.connect("cyber.db")
    prods = conn.execute("SELECT id, sku, name FROM products ORDER BY id DESC").fetchall()
    posts = conn.execute("SELECT id, slug, title FROM posts ORDER BY id DESC").fetchall()
    conn.close()

    assert len(prods) >= 4, f"Need at least 4 products, found {len(prods)}"
    assert len(posts) >= 4, f"Need at least 4 posts, found {len(posts)}"

    # Pick 4 specific products in a distinct serial order:
    p1, p2, p3, p4 = prods[0], prods[1], prods[2], prods[3]
    # Pick 4 specific posts in a distinct serial order:
    j1, j2, j3, j4 = posts[0], posts[1], posts[2], posts[3]

    curation_payload = {
        "home_featured_product_1": str(p1[0]),
        "home_featured_product_2": str(p2[0]),
        "home_featured_product_3": str(p3[0]),
        "home_featured_product_4": str(p4[0]),
        "home_featured_post_1": str(j1[0]),
        "home_featured_post_2": str(j2[0]),
        "home_featured_post_3": str(j3[0]),
        "home_featured_post_4": str(j4[0])
    }

    save_resp = admin_session.post(f"{BASE_URL}/api/admin/home-curation", json=curation_payload)
    assert save_resp.status_code == 200, f"Curation save failed: {save_resp.status_code}, {save_resp.text}"
    assert save_resp.json().get("ok") is True
    print("✓ Saved custom 4-Product and 4-Journal showcase serials via /api/admin/home-curation.")

    # 5. Verify Homepage displays these exact products & posts in exact serial order!
    home_resp = requests.get(f"{BASE_URL}/")
    assert home_resp.status_code == 200
    home_html = home_resp.text

    # Verify products exist on homepage and appear in exact serial sequence
    idx_p1 = home_html.find(p1[2]) # name
    idx_p2 = home_html.find(p2[2])
    idx_p3 = home_html.find(p3[2])
    idx_p4 = home_html.find(p4[2])

    assert idx_p1 != -1, f"Product 1 ({p1[2]}) not found on homepage"
    assert idx_p2 != -1, f"Product 2 ({p2[2]}) not found on homepage"
    assert idx_p3 != -1, f"Product 3 ({p3[2]}) not found on homepage"
    assert idx_p4 != -1, f"Product 4 ({p4[2]}) not found on homepage"
    assert idx_p1 < idx_p2 < idx_p3 < idx_p4, f"Products not in correct serial sequence! ({idx_p1}, {idx_p2}, {idx_p3}, {idx_p4})"
    print(f"✓ Verified 4 Products appear on homepage in exact serial order: [1: {p1[1]} -> 2: {p2[1]} -> 3: {p3[1]} -> 4: {p4[1]}]")

    # Verify posts exist on homepage and appear in exact serial sequence
    idx_j1 = home_html.find(j1[2]) # title
    idx_j2 = home_html.find(j2[2])
    idx_j3 = home_html.find(j3[2])
    idx_j4 = home_html.find(j4[2])

    assert idx_j1 != -1, f"Post 1 ({j1[2]}) not found on homepage"
    assert idx_j2 != -1, f"Post 2 ({j2[2]}) not found on homepage"
    assert idx_j3 != -1, f"Post 3 ({j3[2]}) not found on homepage"
    assert idx_j4 != -1, f"Post 4 ({j4[2]}) not found on homepage"
    assert idx_j1 < idx_j2 < idx_j3 < idx_j4, f"Posts not in correct serial sequence! ({idx_j1}, {idx_j2}, {idx_j3}, {idx_j4})"
    print(f"✓ Verified 4 Journal posts appear on homepage in exact serial order: [1: {j1[1][:20]} -> 2: {j2[1][:20]} -> 3: {j3[1][:20]} -> 4: {j4[1][:20]}]")

    # 6. Test Serial Order Swap (Swap Serial 1 and Serial 2)
    swap_payload = {
        "home_featured_product_1": str(p2[0]),
        "home_featured_product_2": str(p1[0]),
        "home_featured_product_3": str(p3[0]),
        "home_featured_product_4": str(p4[0]),
        "home_featured_post_1": str(j2[0]),
        "home_featured_post_2": str(j1[0]),
        "home_featured_post_3": str(j3[0]),
        "home_featured_post_4": str(j4[0])
    }
    swap_resp = admin_session.post(f"{BASE_URL}/api/admin/home-curation", json=swap_payload)
    assert swap_resp.status_code == 200

    home_resp2 = requests.get(f"{BASE_URL}/")
    html2 = home_resp2.text
    new_idx_p1 = html2.find(p1[2])
    new_idx_p2 = html2.find(p2[2])
    assert new_idx_p2 < new_idx_p1, "Swapped products did not swap positions on homepage!"

    new_idx_j1 = html2.find(j1[2])
    new_idx_j2 = html2.find(j2[2])
    assert new_idx_j2 < new_idx_j1, "Swapped journal posts did not swap positions on homepage!"
    print("✓ Successfully swapped Serial 1 and Serial 2: Homepage reflects swapped positions immediately!")

    print("\n=== ALL HOMEPAGE CURATION TESTS PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    test_home_curation()
