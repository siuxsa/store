import requests
from bs4 import BeautifulSoup

BASE_URL = "http://127.0.0.1:5000"

def test_custom_js_tracking():
    print("=== TESTING CUSTOM JAVASCRIPT & ANALYTICS TRACKING MATRIX ===")
    s = requests.Session()

    # 1. Admin login
    res_login = s.post(f"{BASE_URL}/admin/login", data={"identifier": "admin", "password": "Admin@2026"})
    assert res_login.status_code == 200 or res_login.history, "Admin login failed"
    print("✓ Master Admin authenticated successfully.")

    # 2. Check Admin Panel Form Fields
    res_admin = s.get(f"{BASE_URL}/admin")
    assert res_admin.status_code == 200
    soup_admin = BeautifulSoup(res_admin.text, "html.parser")

    # Global and Per-page settings inputs in Settings module
    for field_name in ["custom_head_js", "custom_footer_js", "custom_js_home", "custom_js_shop", "custom_js_journal", "custom_js_request", "custom_js_vault"]:
        inp = soup_admin.find("textarea", {"name": field_name})
        assert inp is not None, f"Missing {field_name} in settings form"
    print("✓ Verified all 7 Global & Per-Page tracking textareas present in Admin Settings form.")

    # Product editor field
    pse_js = soup_admin.find(id="pse-custom-js")
    assert pse_js is not None, "Missing #pse-custom-js in product editor"
    print("✓ Verified #pse-custom-js present in Product Editor.")

    # Post editor field
    jse_js = soup_admin.find(id="jse-custom-js")
    assert jse_js is not None, "Missing #jse-custom-js in post editor"
    print("✓ Verified #jse-custom-js present in Post Editor.")

    # 3. Configure Global & Per-Page Scripts
    test_settings = {
        "custom_head_js": "<script>/* GTM/GA4 */ window.__GLOBAL_HEAD_TRACKER = true;</script>",
        "custom_footer_js": "<script>/* TELEMETRY */ window.__GLOBAL_FOOTER_TRACKER = true;</script>",
        "custom_js_home": "<script>window.__PAGE_HOME_TRACKER = true;</script>",
        "custom_js_shop": "<script>window.__PAGE_SHOP_TRACKER = true;</script>",
        "custom_js_journal": "<script>window.__PAGE_JOURNAL_TRACKER = true;</script>",
        "custom_js_request": "<script>window.__PAGE_REQUEST_TRACKER = true;</script>",
        "custom_js_vault": "<script>window.__PAGE_VAULT_TRACKER = true;</script>"
    }
    res_set = s.post(f"{BASE_URL}/api/admin/settings", json=test_settings)
    assert res_set.status_code == 200 and res_set.json().get("ok"), "Failed to save settings"
    print("✓ Successfully persisted Global and Per-Page tracking snippets.")

    # 4. Verify Global Head & Footer Scripts on All Pages
    routes = ["/", "/shop", "/journal", "/request"]
    for path in routes:
        res = requests.get(f"{BASE_URL}{path}")
        assert res.status_code == 200, f"Failed loading {path}"
        assert "window.__GLOBAL_HEAD_TRACKER = true;" in res.text, f"Global <head> script missing on {path}"
        assert "window.__GLOBAL_FOOTER_TRACKER = true;" in res.text, f"Global footer script missing on {path}"
        print(f"✓ Global <head> & footer scripts rendered on {path}")

    # 5. Verify Route-Specific Isolation
    res_h = requests.get(f"{BASE_URL}/")
    assert "window.__PAGE_HOME_TRACKER = true;" in res_h.text
    assert "window.__PAGE_SHOP_TRACKER = true;" not in res_h.text

    res_s = requests.get(f"{BASE_URL}/shop")
    assert "window.__PAGE_SHOP_TRACKER = true;" in res_s.text
    assert "window.__PAGE_HOME_TRACKER = true;" not in res_s.text

    res_j = requests.get(f"{BASE_URL}/journal")
    assert "window.__PAGE_JOURNAL_TRACKER = true;" in res_j.text

    res_r = requests.get(f"{BASE_URL}/request")
    assert "window.__PAGE_REQUEST_TRACKER = true;" in res_r.text
    print("✓ Verified route-specific isolation across all storefront endpoints.")

    # 6. Verify Product-Specific Tracking Snippet
    res_prod = s.post(f"{BASE_URL}/api/admin/products", json={
        "id": 22,
        "sku": "LIC-BURP-PRO",
        "name": "Burp Suite Professional v2026.10",
        "slug": "burp-suite-professional-v2026-10",
        "category": "Web & AppSec Licenses",
        "price": 499.0,
        "retail_price": 899.0,
        "status": "PUBLISHED",
        "custom_js": "<script>window.__PRODUCT_CONVERSION_PIXEL = true;</script>"
    })
    assert res_prod.status_code == 200 and res_prod.json().get("ok")
    res_pdp = requests.get(f"{BASE_URL}/product/burp-suite-professional-v2026-10")
    assert "window.__PRODUCT_CONVERSION_PIXEL = true;" in res_pdp.text
    print("✓ Verified product-specific custom tracking snippet executed on product detail page.")

    # 7. Verify Post-Specific Tracking Snippet
    res_post = s.post(f"{BASE_URL}/api/admin/posts", json={
        "id": 11,
        "title": "Breaking Azure AD Hybrid Kerberos PKINIT Silver Tickets",
        "slug": "breaking-azure-ad-hybrid-kerberos-pkinit-silver-tickets",
        "category": "ACTIVE DIRECTORY & CLOUD",
        "severity": "HIGH",
        "cve_id": "CVE-2026-1944",
        "cvss_score": "8.8",
        "summary": "Deep technical breakdown.",
        "content": "Exploit writeup.",
        "status": "PUBLISHED",
        "custom_js": "<script>window.__ADVISORY_ANALYTICS_EVENT = true;</script>"
    })
    assert res_post.status_code == 200 and res_post.json().get("ok")
    res_art = requests.get(f"{BASE_URL}/journal/breaking-azure-ad-hybrid-kerberos-pkinit-silver-tickets")
    assert "window.__ADVISORY_ANALYTICS_EVENT = true;" in res_art.text
    print("✓ Verified advisory-specific custom tracking snippet executed on journal post page.")

    # 8. Reset Settings and Clean Up
    s.post(f"{BASE_URL}/api/admin/settings", json={
        "custom_head_js": "",
        "custom_footer_js": "",
        "custom_js_home": "",
        "custom_js_shop": "",
        "custom_js_journal": "",
        "custom_js_request": "",
        "custom_js_vault": ""
    })
    s.post(f"{BASE_URL}/api/admin/products", json={
        "id": 22,
        "sku": "LIC-BURP-PRO",
        "name": "Burp Suite Professional v2026.10",
        "slug": "burp-suite-professional-v2026-10",
        "category": "Web & AppSec Licenses",
        "price": 499.0,
        "retail_price": 899.0,
        "status": "PUBLISHED",
        "custom_js": ""
    })
    s.post(f"{BASE_URL}/api/admin/posts", json={
        "id": 11,
        "title": "Breaking Azure AD Hybrid Kerberos PKINIT Silver Tickets",
        "slug": "breaking-azure-ad-hybrid-kerberos-pkinit-silver-tickets",
        "category": "ACTIVE DIRECTORY & CLOUD",
        "severity": "HIGH",
        "cve_id": "CVE-2026-1944",
        "cvss_score": "8.8",
        "summary": "Deep technical breakdown.",
        "content": "Exploit writeup.",
        "status": "PUBLISHED",
        "custom_js": ""
    })
    print("✓ Cleaned up test configurations successfully.")
    print("\n=== ALL CUSTOM JAVASCRIPT & ANALYTICS TESTS PASSED 100%! ===")

if __name__ == "__main__":
    test_custom_js_tracking()
