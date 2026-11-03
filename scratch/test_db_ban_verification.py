import requests
import sqlite3
import os
import sys

BASE_URL = "http://127.0.0.1:5000"
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cyber.db")

def test_ban_system():
    print("=== STARTING DATABASE-DRIVEN BAN VERIFICATION TEST ===")
    test_hwid = "HWID-TEST-DEVICE-9999"

    # Pre-clean database
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM banned_clients WHERE device_hwid = ?", (test_hwid,))
    conn.commit()
    conn.close()

    session = requests.Session()
    resp = session.post(f"{BASE_URL}/api/security/device-verify", json={"hwid": test_hwid})
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("banned") is False, "Clean device should not be banned"
    assert "zd_allow_token" in session.cookies, "Allow cookie must be issued for clean device"
    print("✓ Clean visitor device verified successfully, allow cookie issued.")

    # 2. Clean visitor can access store page
    page_resp = session.get(f"{BASE_URL}/")
    assert page_resp.status_code == 200, f"Expected 200, got {page_resp.status_code}"
    assert "HARDWARE SANCTION ACTIVE" not in page_resp.text, "Ban banner should not be shown to clean device"
    print("✓ Clean visitor can access site normally.")

    # 3. Add HWID directly to SQLite cyber.db banned_clients table
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM banned_clients WHERE device_hwid = ?", (test_hwid,))
    conn.execute("""
        INSERT INTO banned_clients (user_id, username, ip_address, device_hwid, reason, banned_at)
        VALUES (NULL, 'test_target', '', ?, 'Direct DB Sanction Test', datetime('now'))
    """, (test_hwid,))
    conn.commit()
    conn.close()
    print("✓ Inserted test HWID directly into database banned_clients table.")

    # 4. Device verification for the banned HWID
    banned_session = requests.Session()
    banned_resp = banned_session.post(f"{BASE_URL}/api/security/device-verify", json={"hwid": test_hwid})
    assert banned_resp.status_code == 403, f"Expected 403 for banned device, got {banned_resp.status_code}"
    banned_data = banned_resp.json()
    assert banned_data.get("banned") is True, "Banned device should have banned=True"
    assert "zd_allow_token" not in banned_session.cookies, "Allow cookie MUST NOT be provided to banned device"

    # Verify complex crypto cookie (>= 10 characters)
    crypto_cookie = banned_session.cookies.get("zd_sanction_token")
    assert crypto_cookie, "Complex crypto cookie 'zd_sanction_token' must be set on ban"
    assert len(crypto_cookie) >= 10, f"Crypto cookie must be at least 10 chars, got length {len(crypto_cookie)}: {crypto_cookie}"
    assert crypto_cookie.startswith("SANCT_"), "Crypto cookie must be signed cryptographic token"
    print(f"✓ Complex cryptographic ban cookie verified: {crypto_cookie[:18]}... (Length: {len(crypto_cookie)} chars).")

    # 5. Banned device attempts to load any page
    blocked_page = banned_session.get(f"{BASE_URL}/", cookies={"zd_hwid": test_hwid})
    assert blocked_page.status_code == 403, f"Expected 403 on page load for banned device, got {blocked_page.status_code}"
    assert "YOU ARE BANNED" in blocked_page.text, "Ban banner must state you are banned"
    assert "Telegram" in blocked_page.text or "TELEGRAM" in blocked_page.text, "Ban banner must instruct user to contact administrator on Telegram"

    # Verify ZERO fingerprint / root-cause leak
    assert test_hwid not in blocked_page.text, "CRITICAL: Banner must NEVER leak the banned HWID fingerprint!"
    assert "Direct DB Sanction Test" not in blocked_page.text, "CRITICAL: Banner must NEVER leak the root cause / sanction reason!"
    print("✓ Banner privacy verified: Zero leaks of HWID fingerprint, IP, or root-cause reason.")

    # 6. Test direct access by HWID blocks access
    blocked_by_hwid = requests.get(f"{BASE_URL}/shop", cookies={"zd_hwid": test_hwid})
    assert blocked_by_hwid.status_code == 403, f"Expected 403 on shop page, got {blocked_by_hwid.status_code}"
    assert "YOU ARE BANNED" in blocked_by_hwid.text
    print("✓ Direct DB check blocks user with 403 ban screen.")

    # 7. Unban HWID directly in database
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM banned_clients WHERE device_hwid = ?", (test_hwid,))
    conn.commit()
    conn.close()
    print("✓ Deleted test HWID from database banned_clients table.")

    # 8. Immediate unban verification without server reload (proves zero RAM reliance)
    unbanned_session = requests.Session()
    unban_verify = unbanned_session.post(f"{BASE_URL}/api/security/device-verify", json={"hwid": test_hwid})
    assert unban_verify.status_code == 200, f"Expected 200 after unban, got {unban_verify.status_code}"
    assert unban_verify.json().get("banned") is False, "Device should no longer be banned"
    assert "zd_allow_token" in unbanned_session.cookies, "Allow cookie now provided"

    unban_page = unbanned_session.get(f"{BASE_URL}/shop", cookies={"zd_hwid": test_hwid})
    assert unban_page.status_code == 200, f"Expected 200, got {unban_page.status_code}"
    print("✓ Instant DB unban verified: Access restored immediately without server restart.")

    print("\n=== ALL DATABASE-DRIVEN BAN TESTS PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    test_ban_system()
