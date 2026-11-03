import requests
from bs4 import BeautifulSoup
import sqlite3

BASE_URL = "http://127.0.0.1:5000"

def test_visual_themes_studio():
    print("=== TESTING VISUAL THEMES STUDIO & LIVE INSPECT CANVAS ===")
    session = requests.Session()

    # 1. Login as Master Admin
    r_login = session.post(f"{BASE_URL}/admin/login", data={"identifier": "admin", "password": "Admin@2026"})
    assert r_login.status_code == 200, "Master Admin login failed"
    print("✓ Master Admin authenticated successfully.")

    # 2. Fetch admin panel and inspect visual themes DOM
    r_admin = session.get(f"{BASE_URL}/admin")
    assert r_admin.status_code == 200
    soup = BeautifulSoup(r_admin.text, "html.parser")

    mod_visual = soup.find(id="mod-themes-visual")
    assert mod_visual is not None, "Missing #mod-themes-visual section"
    print("✓ #mod-themes-visual exists in admin DOM.")

    # 3. Verify Canvas Stage and Iframe
    canvas = soup.find(id="theme-stage-canvas")
    scaler = soup.find(id="theme-frame-scaler")
    container = soup.find(id="theme-frame-container")
    iframe = soup.find(id="theme-preview-iframe")
    assert canvas is not None, "Missing #theme-stage-canvas"
    assert scaler is not None, "Missing #theme-frame-scaler"
    assert container is not None, "Missing #theme-frame-container"
    assert iframe is not None, "Missing #theme-preview-iframe"
    assert iframe.get("src") == "/", f"Expected iframe src='/' but got '{iframe.get('src')}'"
    print("✓ Visual Canvas Stage, Scaler, Container, and Live Store Iframe verified.")

    # 4. Verify Inspect Mode Toggle and Device Bar
    btn_inspect = soup.find(id="btn-inspect-mode")
    assert btn_inspect is not None, "Missing #btn-inspect-mode"
    assert "toggleInspectMode()" in btn_inspect.get("onclick", "")
    
    device_btns = mod_visual.find_all("button", class_="theme-device-btn")
    assert len(device_btns) == 3, f"Expected 3 device buttons (desktop, tablet, mobile), got {len(device_btns)}"
    print("✓ Point & Click Inspect Mode toggle and Responsive Device buttons (Desktop/Tablet/Mobile) present.")

    # 5. Verify Quick Color Palette Bar
    for color_key in ["theme_bg_color", "theme_text_color", "theme_dark_color", "accent_cyan_color", "accent_green_color", "accent_amber_color"]:
        picker = soup.find(id=f"quick-{color_key}")
        assert picker is not None, f"Missing quick color input #quick-{color_key}"
    save_colors_btn = soup.find(id="btn-save-colors-quick")
    assert save_colors_btn is not None, "Missing #btn-save-colors-quick"
    print("✓ Live Quick Color Palette inputs and SAVE COLORS button present.")

    # 6. Verify Quick Edit Element Modal
    modal = soup.find(id="modal-theme-element")
    assert modal is not None, "Missing #modal-theme-element"
    assert soup.find(id="quick-edit-field-key") is not None
    assert soup.find(id="quick-edit-input") is not None
    assert soup.find(id="quick-edit-textarea") is not None
    assert soup.find(id="quick-edit-image-url") is not None
    assert soup.find(id="btn-quick-edit-save") is not None
    print("✓ Point-and-Click Interactive Element Editor Modal (#modal-theme-element) fully wired up.")

    # 7. Test Theme Save API (Quick Color and Field update)
    test_palette = {
        "theme_bg_color": "#090a0c",
        "theme_text_color": "#e2e8f0",
        "theme_dark_color": "#111317",
        "accent_cyan_color": "#00f0ff",
        "accent_green_color": "#10b981",
        "accent_amber_color": "#f59e0b"
    }
    r_save = session.post(f"{BASE_URL}/api/admin/theme", json=test_palette)
    assert r_save.status_code == 200, f"Theme save failed: {r_save.text}"
    assert r_save.json().get("ok") is True
    print("✓ Successfully saved theme color palette via /api/admin/theme.")

    # 8. Verify public site reflects newly saved colors in CSS variables
    r_public = requests.get(f"{BASE_URL}/")
    assert r_public.status_code == 200
    assert "--bg: #090a0c" in r_public.text
    assert "--cyan: #00f0ff" in r_public.text
    print("✓ Live storefront dynamically renders updated CSS variables in <head>.")

    # 9. Clean up: Restore default color palette
    default_palette = {
        "theme_bg_color": "#f3f2ee",
        "theme_text_color": "#111111",
        "theme_dark_color": "#101010",
        "accent_cyan_color": "#00e5ff",
        "accent_green_color": "#10b981",
        "accent_amber_color": "#f59e0b"
    }
    r_restore = session.post(f"{BASE_URL}/api/admin/theme", json=default_palette)
    assert r_restore.status_code == 200
    print("✓ Default color palette cleanly restored.")

    print("\n=== ALL VISUAL THEMES STUDIO TESTS PASSED 100%! ===")

if __name__ == "__main__":
    test_visual_themes_studio()
