import requests
from bs4 import BeautifulSoup

BASE_URL = "http://127.0.0.1:5000"

def test_admin_login_security():
    print("=== TESTING ADMIN LOGIN CREDENTIAL PRIVACY & SECURITY ===")

    session = requests.Session()
    r = session.get(f"{BASE_URL}/admin/login")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    html = r.text

    # 1. Assert no password or default credential text exists in the public page
    assert "Admin@2026" not in html, "LEAK DETECTED: 'Admin@2026' found in public HTML!"
    assert "quickfill" not in html.lower(), "LEAK DETECTED: 'quickfill' button or helper found!"
    assert "load default admin credentials" not in html.lower(), "LEAK DETECTED: Default credentials hint found!"

    soup = BeautifulSoup(html, "html.parser")
    user_input = soup.find("input", attrs={"name": "identifier"})
    pass_input = soup.find("input", attrs={"name": "password"})

    assert user_input is not None, "Missing identifier input"
    assert pass_input is not None, "Missing password input"

    # 2. Check input values are strictly blank (no prefilled values)
    assert user_input.get("value", "") == "", f"Username input pre-filled with '{user_input.get('value')}'"
    assert pass_input.get("value", "") == "", f"Password input pre-filled with '{pass_input.get('value')}'"

    # 3. Check placeholders do not leak sensitive handles or credentials
    assert "admin@zerodaymatrix.io" not in user_input.get("placeholder", "").lower()
    print("✓ Public /admin/login is completely clean: ZERO credentials, ZERO prefill, ZERO quickfill leaks.")

    # 4. Test actual authentication with valid credentials still works
    login_resp = session.post(f"{BASE_URL}/admin/login", data={"identifier": "admin", "password": "Admin@2026"}, allow_redirects=False)
    assert login_resp.status_code == 302, f"Login failed: {login_resp.status_code}"
    print("✓ Admin successfully authenticates with valid credentials.")

    # 5. Test failed login does not leak password in response
    bad_resp = requests.post(f"{BASE_URL}/admin/login", data={"identifier": "admin", "password": "wrong_pass_attempt"})
    assert bad_resp.status_code == 401
    assert "wrong_pass_attempt" not in bad_resp.text
    assert "Admin@2026" not in bad_resp.text
    print("✓ Failed login correctly rejects with 401 without leaking passwords.")

    print("\n=== ALL ADMIN LOGIN SECURITY TESTS PASSED 100%! ===")

if __name__ == "__main__":
    test_admin_login_security()
