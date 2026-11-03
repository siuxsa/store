import requests
import sqlite3

BASE_URL = "http://127.0.0.1:5000"

def test_category_strip_single():
    print("=== TESTING EDITABLE ONE-LINE CATEGORY STRIP TEXT (LINKS TO SHOP) ===")
    session = requests.Session()

    # 1. Login as Master Admin
    login_resp = session.post(f"{BASE_URL}/admin/login", data={"identifier": "admin", "password": "Admin@2026"})
    assert login_resp.status_code == 200, f"Admin login failed: {login_resp.status_code}"
    print("✓ Master Admin authenticated successfully via /admin/login.")

    # 2. Update category_strip_text via theme API
    custom_text = "ZERO DAY ARSENAL // OFFENSIVE SUITES // SIEM EXPLOITS // REVERSE ENGINEERING // THREAT INTEL"
    update_resp = session.post(f"{BASE_URL}/api/admin/theme", json={"category_strip_text": custom_text})
    assert update_resp.status_code == 200, f"Theme update failed: {update_resp.status_code}, {update_resp.text}"
    print("✓ Category strip single text updated via /api/admin/theme API.")

    # 3. Verify on public homepage
    home_resp = requests.get(f"{BASE_URL}/")
    assert home_resp.status_code == 200
    assert custom_text in home_resp.text, f"Expected '{custom_text}' on homepage, but not found!"
    assert 'class="category-strip-single-link"' in home_resp.text, "Expected category-strip-single-link class"
    assert 'href="/shop"' in home_resp.text, "Expected category strip link to point to /shop"
    print(f"✓ Verified custom one-line category banner text on homepage: '{custom_text}'")

    # 4. Verify in Admin Theme Customizer panel HTML
    admin_resp = session.get(f"{BASE_URL}/admin")
    assert admin_resp.status_code == 200
    assert 'name="category_strip_text"' in admin_resp.text, "category_strip_text input field found in admin panel"
    print("✓ Verified category_strip_text input field in Admin panel theme editor.")

    # 5. Restore original standard value
    default_text = "ALL SYSTEMS // WEB & APPSEC // OFFENSIVE & RED TEAM // SIEM & BLUE TEAM // REVERSE ENGINEERING // OSINT & RECON"
    reset_resp = session.post(f"{BASE_URL}/api/admin/theme", json={"category_strip_text": default_text})
    assert reset_resp.status_code == 200
    home_resp_restored = requests.get(f"{BASE_URL}/")
    escaped_default = default_text.replace("&", "&amp;")
    assert default_text in home_resp_restored.text or escaped_default in home_resp_restored.text
    print("✓ Restored default category strip text successfully.")

    print("\n=== ALL CATEGORY STRIP TESTS PASSED! ===")

if __name__ == "__main__":
    test_category_strip_single()
