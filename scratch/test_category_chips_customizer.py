import requests
import sqlite3
import os

BASE_URL = "http://127.0.0.1:5000"

def test_category_chips():
    print("=== TESTING EDITABLE CATEGORY NAVIGATION STRIP CHIPS ===")
    session = requests.Session()

    # 1. Login as Master Admin
    login_resp = session.post(f"{BASE_URL}/admin/login", data={"identifier": "admin", "password": "Admin@2026"})
    assert login_resp.status_code == 200, f"Admin login failed: {login_resp.status_code}"
    print("✓ Master Admin authenticated successfully.")

    # 2. Update category chips via theme API
    custom_chips = {
        "cat_chip_all": "CORE SYSTEMS (ALL)",
        "cat_chip_web": "WEB APPLICATION DEFENSE",
        "cat_chip_offensive": "RED TEAM ARSENAL",
        "cat_chip_siem": "BLUE TEAM & SIEM OPS",
        "cat_chip_re": "BINARY DECOMPILATION",
        "cat_chip_osint": "RECONNAISSANCE & INTEL"
    }
    update_resp = session.post(f"{BASE_URL}/api/admin/theme", json=custom_chips)
    assert update_resp.status_code == 200, f"Theme update failed: {update_resp.status_code}, {update_resp.text}"
    print("✓ Category chips updated via /api/admin/theme API.")

    # 3. Verify on public homepage
    home_resp = requests.get(f"{BASE_URL}/")
    assert home_resp.status_code == 200
    for key, text in custom_chips.items():
        assert text in home_resp.text or text.replace("&", "&amp;") in home_resp.text, f"Expected '{text}' on homepage, but not found!"
        print(f"✓ Verified custom chip text: '{text}'")

    # 4. Restore original standard values
    default_chips = {
        "cat_chip_all": "ALL SYSTEMS",
        "cat_chip_web": "WEB & APPSEC",
        "cat_chip_offensive": "OFFENSIVE & RED TEAM",
        "cat_chip_siem": "SIEM & BLUE TEAM",
        "cat_chip_re": "REVERSE ENGINEERING",
        "cat_chip_osint": "OSINT & RECON"
    }
    session.post(f"{BASE_URL}/api/admin/theme", json=default_chips)
    home_resp_restored = requests.get(f"{BASE_URL}/")
    assert "ALL SYSTEMS" in home_resp_restored.text
    assert "WEB &amp; APPSEC" in home_resp_restored.text or "WEB & APPSEC" in home_resp_restored.text
    print("✓ Restored default category chip labels successfully.")

    print("\n=== ALL CATEGORY CHIPS CUSTOMIZATION TESTS PASSED! ===")

if __name__ == "__main__":
    test_category_chips()
