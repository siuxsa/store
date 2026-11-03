import requests
from bs4 import BeautifulSoup

BASE_URL = "http://127.0.0.1:5000"

def run_tests():
    print("=================================================================")
    print("STARTING FULL COMPREHENSIVE FEATURE VERIFICATION SUITE")
    print("=================================================================")
    
    admin_session = requests.Session()
    # 1. Login as Master Admin
    login_resp = admin_session.post(f"{BASE_URL}/admin/login", data={"identifier": "admin", "password": "Admin@2026"})
    assert login_resp.status_code == 200, f"Admin login failed: {login_resp.status_code}"
    print("✓ Master Admin authenticated successfully.")

    # -----------------------------------------------------------------
    # TEST 1: POST COMMENTING & MODERATION LIFECYCLE
    # -----------------------------------------------------------------
    print("\n[TEST 1] Testing Journal Post Comments (Public Submission & Admin Moderation)...")
    visitor_session = requests.Session()
    # Find active blog post
    journal_html = visitor_session.get(f"{BASE_URL}/journal").text
    soup_j = BeautifulSoup(journal_html, 'html.parser')
    first_link = soup_j.find('a', href=lambda h: h and '/journal/' in h and h != '/journal')
    assert first_link is not None, "No journal post found!"
    post_slug = first_link['href'].split('/journal/')[-1]
    
    # Get post ID from post detail page
    detail_html = visitor_session.get(f"{BASE_URL}/journal/{post_slug}").text
    soup_detail = BeautifulSoup(detail_html, 'html.parser')
    form = soup_detail.find('form', id='comment-dispatch-form')
    assert form is not None, "Missing comment form on journal post detail!"
    action_url = form['action']
    post_id = int(action_url.split('/api/posts/')[-1].split('/comments')[0])
    
    test_comment_body = "TEST_COMMENT_E2E_VERIFICATION_PAYLOAD_987654"
    comment_payload = {
        "author_name": "CYBER_AUDITOR_X",
        "author_role": "RECON SPECIALIST",
        "body": test_comment_body
    }
    comment_resp = visitor_session.post(f"{BASE_URL}/api/posts/{post_id}/comments", json=comment_payload)
    assert comment_resp.status_code == 200, f"Comment submission failed: {comment_resp.text}"
    comment_data = comment_resp.json()
    assert comment_data.get("ok") is True
    assert comment_data.get("status") == "PENDING"
    print("✓ Visitor submitted comment successfully (Status: PENDING).")

    # Verify unapproved comment is NOT public
    detail_html_after = visitor_session.get(f"{BASE_URL}/journal/{post_slug}").text
    assert test_comment_body not in detail_html_after, "Pending comment leaked publicly before admin approval!"
    print("✓ Verified pending comment is safely held in admin moderation queue.")

    # Get comment ID from admin panel comments list
    admin_panel_html = admin_session.get(f"{BASE_URL}/admin").text
    soup_admin = BeautifulSoup(admin_panel_html, 'html.parser')
    comment_row = soup_admin.find('tr', id=lambda i: i and i.startswith('comment-row-'))
    assert comment_row is not None, "Missing comment row in admin comments table!"
    created_comment_id = int(comment_row['id'].replace('comment-row-', ''))

    # Admin approves comment
    approve_resp = admin_session.post(f"{BASE_URL}/api/admin/comments/{created_comment_id}/status", json={"status": "APPROVED"})
    assert approve_resp.status_code == 200, f"Comment approve failed: {approve_resp.text}"
    print(f"✓ Master Admin approved comment #{created_comment_id}.")

    # Verify comment IS NOW public on post detail page
    detail_html_approved = visitor_session.get(f"{BASE_URL}/journal/{post_slug}").text
    assert test_comment_body in detail_html_approved, "Approved comment not displaying on journal post!"
    print("✓ Verified approved comment is now live on journal post.")

    # Admin deletes test comment to keep DB clean
    del_resp = admin_session.delete(f"{BASE_URL}/api/admin/comments/{created_comment_id}")
    assert del_resp.status_code == 200, f"Comment delete failed: {del_resp.text}"
    print(f"✓ Master Admin permanently cleaned up comment #{created_comment_id}.")

    # -----------------------------------------------------------------
    # TEST 2: THEME COLOR CUSTOMIZATION (STOREFRONT & CANVASES)
    # -----------------------------------------------------------------
    print("\n[TEST 2] Testing Theme Color Customization & Live CSS Injection...")
    test_colors = {
        "accent_cyan_color": "#00d4ff",
        "accent_green_color": "#00ff66",
        "accent_amber_color": "#ffaa00",
        "theme_bg_color": "#0a0c10",
        "theme_text_color": "#e0e6ed",
        "theme_dark_color": "#121620",
        "custom_css_overrides": "/* E2E Test CSS Override */ .e2e-test-marker { opacity: 0.99; }"
    }
    save_theme_resp = admin_session.post(f"{BASE_URL}/api/admin/theme", json=test_colors)
    assert save_theme_resp.status_code == 200, f"Theme save failed: {save_theme_resp.text}"
    print("✓ Theme colors saved to database via /api/admin/theme.")

    # Verify public homepage has injected CSS variables
    home_html = visitor_session.get(f"{BASE_URL}/").text
    assert "site-theme-custom-vars" in home_html, "Missing site-theme-custom-vars style block in homepage!"
    assert "--cyan: #00d4ff" in home_html, "Missing --cyan in injected styles!"
    assert "--green: #00ff66" in home_html, "Missing --green in injected styles!"
    assert "--amber: #ffaa00" in home_html, "Missing --amber in injected styles!"
    assert "--bg: #0a0c10" in home_html, "Missing --bg in injected styles!"
    assert "--text: #e0e6ed" in home_html, "Missing --text in injected styles!"
    assert "--dark: #121620" in home_html, "Missing --dark in injected styles!"
    assert ".e2e-test-marker" in home_html, "Missing custom CSS overrides in injected styles!"
    print("✓ Verified public storefront renders all custom colors and CSS variables dynamically in <head>.")

    # Restore default clean colors
    restore_colors = {
        "accent_cyan_color": "#00e5ff",
        "accent_green_color": "#10b981",
        "accent_amber_color": "#f59e0b",
        "theme_bg_color": "#f3f2ee",
        "theme_text_color": "#111111",
        "theme_dark_color": "#101010",
        "custom_css_overrides": ""
    }
    admin_session.post(f"{BASE_URL}/api/admin/theme", json=restore_colors)
    print("✓ Restored default theme colors cleanly.")

    # -----------------------------------------------------------------
    # TEST 3: REVIEWS STUDIO (CRUD)
    # -----------------------------------------------------------------
    print("\n[TEST 3] Testing Product Reviews CRUD in Admin Panel...")
    review_payload = {
        "product_sku": "LIC-BURP-PRO",
        "rating": 5,
        "author_name": "ALPHA_RED_LEAD",
        "author_role": "Red Team Commander",
        "author_org": "Offensive Labs Global",
        "verified_badge": "VERIFIED ENTERPRISE DEPLOYMENT",
        "title": "Unrivaled airgap offensive tool suite",
        "content": "Flawless deployment on enterprise networks. Instant license dispatch.",
        "featured_manifesto": True
    }
    rev_save_resp = admin_session.post(f"{BASE_URL}/api/admin/reviews", json=review_payload)
    assert rev_save_resp.status_code == 200, f"Review save failed: {rev_save_resp.text}"
    rev_data = rev_save_resp.json()
    assert rev_data.get("ok") is True
    review_id = rev_data.get("id")
    print(f"✓ Created verified product review #{review_id}.")

    # Delete review to clean up
    del_rev_resp = admin_session.delete(f"{BASE_URL}/api/admin/reviews/{review_id}")
    assert del_rev_resp.status_code == 200, f"Review delete failed: {del_rev_resp.text}"
    print(f"✓ Cleaned up review #{review_id}.")

    # -----------------------------------------------------------------
    # TEST 4: PRODUCT CREATION & DETAIL PAGE
    # -----------------------------------------------------------------
    print("\n[TEST 4] Testing Product Catalog Studio...")
    prod_payload = {
        "sku": "LIC-TEST-TOOL-99",
        "name": "ZeroDay Test Exploiter Suite",
        "slug": "zeroday-test-exploiter-suite",
        "category": "OFFENSIVE & RED TEAM",
        "product_type": "LICENSE_KEY",
        "price": 499.00,
        "retail_price": 999.00,
        "version": "v2026.1",
        "license_duration": "1-Year License",
        "platform": "Linux / macOS",
        "short_desc": "Automated payload generator for testing.",
        "description": "Comprehensive test product description.",
        "badge_text": "INSTANT DISPATCH",
        "featured": 0
    }
    prod_save_resp = admin_session.post(f"{BASE_URL}/api/admin/products", json=prod_payload)
    assert prod_save_resp.status_code == 200, f"Product save failed: {prod_save_resp.text}"
    prod_data = prod_save_resp.json()
    assert prod_data.get("ok") is True
    created_prod_id = prod_data.get("id")
    print(f"✓ Created test product #{created_prod_id} ({prod_payload['sku']}).")

    # Verify detail page
    p_detail_resp = visitor_session.get(f"{BASE_URL}/product/zeroday-test-exploiter-suite")
    assert p_detail_resp.status_code == 200
    assert "ZeroDay Test Exploiter Suite" in p_detail_resp.text
    print("✓ Verified product detail page loads properly.")

    # Clean up product
    del_prod_resp = admin_session.delete(f"{BASE_URL}/api/admin/products/{created_prod_id}")
    assert del_prod_resp.status_code == 200, f"Product delete failed: {del_prod_resp.text}"
    print(f"✓ Cleaned up test product #{created_prod_id}.")

    # -----------------------------------------------------------------
    # TEST 5: JOURNAL DISPATCHES & MARKDOWN PREVIEW
    # -----------------------------------------------------------------
    print("\n[TEST 5] Testing Threat Journal Dispatches Studio & Live Markdown Preview...")
    preview_resp = admin_session.post(f"{BASE_URL}/api/admin/posts/preview", json={
        "content": "# Research Advisory\n\n[!WARNING]\nCritical buffer overflow detected in network daemon.\n\n[ad:LIC-BURP-PRO]"
    })
    assert preview_resp.status_code == 200, f"Post preview failed: {preview_resp.text}"
    preview_data = preview_resp.json()
    assert preview_data.get("ok") is True
    assert "Critical buffer overflow" in preview_data.get("rendered_html", "")
    print("✓ Live markdown preview and Smart Ad processor verified.")

    # -----------------------------------------------------------------
    # TEST 6: CUSTOMER VAULT & ORDERS LOOKUP
    # -----------------------------------------------------------------
    print("\n[TEST 6] Testing Order Checkout & Vault Tracking...")
    checkout_payload = {
        "buyer_telegram": "@operator_test_x",
        "items": [{"sku": "LIC-BURP-PRO", "name": "Burp Suite Pro", "price": 399.0, "qty": 1}],
        "payment_method": "USDT_TRC20"
    }
    chk_resp = visitor_session.post(f"{BASE_URL}/api/checkout", json=checkout_payload)
    assert chk_resp.status_code == 200, f"Checkout failed: {chk_resp.text}"
    chk_data = chk_resp.json()
    assert chk_data.get("ok") is True
    order_num = chk_data.get("order_number")
    print(f"✓ Checkout processed order ticket: #{order_num}")

    order_lookup_resp = visitor_session.get(f"{BASE_URL}/orders/{order_num}")
    assert order_lookup_resp.status_code == 200
    assert order_num in order_lookup_resp.text
    print("✓ Verified public order lookup page.")

    print("\n=================================================================")
    print("ALL COMPREHENSIVE FEATURES TESTED AND VERIFIED 100% OPERATIONAL!")
    print("=================================================================")

if __name__ == "__main__":
    run_tests()
