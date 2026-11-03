import io
import requests
from bs4 import BeautifulSoup

BASE_URL = "http://127.0.0.1:5000"

def test_favicon_and_logo():
    print("=== TESTING FAVICON & LOGO MANAGEMENT SYSTEM ===")

    session = requests.Session()
    # 1. Admin Login
    login_resp = session.post(f"{BASE_URL}/admin/login", data={"identifier": "admin", "password": "Admin@2026"})
    assert login_resp.status_code == 200, "Admin login failed"
    print("✓ Master Admin authenticated successfully.")

    # 2. Test initial /favicon.ico route
    r_fav = requests.get(f"{BASE_URL}/favicon.ico")
    assert r_fav.status_code in [200, 302], f"Favicon route failed: {r_fav.status_code}"
    print(f"✓ Initial /favicon.ico route verified (Status: {r_fav.status_code}, Content-Type: {r_fav.headers.get('Content-Type')}).")

    # 3. Check Settings module in Admin panel renders Logo & Favicon controls
    r_admin = session.get(f"{BASE_URL}/admin")
    assert r_admin.status_code == 200
    admin_html = r_admin.text
    assert "SITE BRAND LOGO" in admin_html, "Missing 'SITE BRAND LOGO' in admin settings"
    assert "settings-site_logo" in admin_html
    assert "settings-logo-preview" in admin_html
    assert "BROWSER TAB FAVICON" in admin_html, "Missing 'BROWSER TAB FAVICON' in admin settings"
    assert "settings-site_favicon" in admin_html
    assert "settings-fav-preview" in admin_html
    print("✓ Admin panel Settings module correctly renders interactive Logo & Favicon upload controls with live previews.")

    # 4. Check Themes Text Studio also has Logo & Favicon inputs
    assert "input-site_logo" in admin_html
    assert "input-site_favicon" in admin_html
    print("✓ Themes Text Studio also renders Logo & Favicon inputs under Global Shell & Branding.")

    # 5. Test uploading a custom image asset via /api/admin/upload-image
    dummy_svg = b'<svg xmlns="http://www.w3.org/2000/svg" width="120" height="30"><rect width="120" height="30" fill="#00e5ff"/><text x="10" y="20" fill="#000" font-family="monospace">MATRIX LOGO</text></svg>'
    files = {"file": ("test_logo.svg", io.BytesIO(dummy_svg), "image/svg+xml")}
    r_upload = session.post(f"{BASE_URL}/api/admin/upload-image", files=files)
    assert r_upload.status_code == 200, f"Upload failed: {r_upload.text}"
    uploaded_logo_url = r_upload.json().get("url")
    assert uploaded_logo_url, "No URL returned from upload"
    print(f"✓ Uploaded brand logo asset: {uploaded_logo_url}")

    # Upload dummy favicon
    dummy_fav = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><circle cx="16" cy="16" r="14" fill="#10b981"/></svg>'
    files_fav = {"file": ("custom_favicon.svg", io.BytesIO(dummy_fav), "image/svg+xml")}
    r_upload_fav = session.post(f"{BASE_URL}/api/admin/upload-image", files=files_fav)
    assert r_upload_fav.status_code == 200
    uploaded_fav_url = r_upload_fav.json().get("url")
    assert uploaded_fav_url, "No URL returned from favicon upload"
    print(f"✓ Uploaded favicon asset: {uploaded_fav_url}")

    # 6. Save custom logo and favicon via /api/admin/settings
    update_payload = {
        "site_name": "ZERO//FORM",
        "site_tagline": "ARCHITECTURAL SECURITY SYSTEMS",
        "site_logo": uploaded_logo_url,
        "site_favicon": uploaded_fav_url,
        "ticker_text": "SS26 TICKER // ACTIVE",
        "telegram_user": "ZeroFormConcierge"
    }
    r_save = session.post(f"{BASE_URL}/api/admin/settings", json=update_payload)
    assert r_save.status_code == 200
    assert r_save.json().get("ok") is True
    print("✓ Successfully saved custom logo and favicon settings in database.")

    # 7. Verify public storefront displays the custom logo in header & footer
    r_home = requests.get(f"{BASE_URL}/")
    assert r_home.status_code == 200
    soup = BeautifulSoup(r_home.text, "html.parser")

    # Header brand logo image
    brand_imgs = soup.find_all("img", attrs={"class": "brand-logo-img"})
    assert len(brand_imgs) > 0, "Expected brand logo img in header"
    assert brand_imgs[0]["src"] == uploaded_logo_url
    print(f"✓ Verified public header renders custom logo: {brand_imgs[0]['src']}")

    # Favicon in head
    fav_link = soup.find("link", attrs={"rel": lambda r: r and "icon" in r.lower()})
    assert fav_link and fav_link.get("href") == uploaded_fav_url, f"Expected favicon link to be {uploaded_fav_url}, found {fav_link}"
    print(f"✓ Verified public <head> renders custom favicon link: {fav_link.get('href')}")

    # /favicon.ico route redirects to updated favicon
    r_fav_redirect = requests.get(f"{BASE_URL}/favicon.ico", allow_redirects=False)
    assert r_fav_redirect.status_code in [302, 301]
    assert uploaded_fav_url in r_fav_redirect.headers.get("Location", "")
    print(f"✓ Verified /favicon.ico redirects to active custom favicon: {r_fav_redirect.headers.get('Location')}")

    # 8. Reset Logo and Favicon back to clean default (empty)
    reset_payload = {
        "site_name": "ZERO//FORM",
        "site_tagline": "ARCHITECTURAL SECURITY SYSTEMS & VERIFIED ENTERPRISE LICENSES",
        "site_logo": "",
        "site_favicon": "",
        "ticker_text": "SS26 SECURITY ARCHITECTURE // SYSTEMS FOR THE UNPREDICTABLE — INSTANT DISPATCH VIA TELEGRAM CONCIERGE",
        "telegram_user": "ZeroFormConcierge"
    }
    r_reset = session.post(f"{BASE_URL}/api/admin/settings", json=reset_payload)
    assert r_reset.status_code == 200
    print("✓ Successfully reset logo and favicon back to default state.")

    # 9. Verify homepage falls back to clean text logo and default favicon
    r_home_after = requests.get(f"{BASE_URL}/")
    soup_after = BeautifulSoup(r_home_after.text, "html.parser")
    assert len(soup_after.find_all("img", attrs={"class": "brand-logo-img"})) == 0, "No logo img should be rendered after reset"
    assert "ZERO//FORM" in soup_after.find(attrs={"class": "brand-logo"}).text
    print("✓ Verified homepage cleanly falls back to text brand logo.")

    print("\n=== ALL FAVICON & LOGO MANAGEMENT TESTS PASSED 100%! ===")

if __name__ == "__main__":
    test_favicon_and_logo()
