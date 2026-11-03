import requests
import json
import secrets

BASE_URL = "http://127.0.0.1:5000"

def test_modular_app():
    print("=== TESTING COMPLETE MODULAR APP WORKFLOW ===")
    session = requests.Session()

    # 1. Homepage & Shop
    r = session.get(f"{BASE_URL}/")
    assert r.status_code == 200, f"Homepage failed: {r.status_code}"
    assert "ZERO//FORM" in r.text or "ZERODAY" in r.text
    print("✓ Public Homepage loaded successfully.")

    r_shop = session.get(f"{BASE_URL}/shop")
    assert r_shop.status_code == 200, f"Shop failed: {r_shop.status_code}"
    print("✓ Arsenal / Shop page loaded successfully.")

    # 2. Product Detail
    r_prod = session.get(f"{BASE_URL}/product/burp-suite-professional-license")
    assert r_prod.status_code == 200, f"Product detail failed: {r_prod.status_code}"
    assert "Burp Suite Professional" in r_prod.text
    print("✓ Product Detail page loaded successfully.")

    # 3. Threat Journal Index & Post Detail
    r_journal = session.get(f"{BASE_URL}/journal")
    assert r_journal.status_code == 200, f"Journal failed: {r_journal.status_code}"
    print("✓ Threat Journal index loaded successfully.")

    r_post = session.get(f"{BASE_URL}/journal/cve-2026-8841-oauth2-token-smuggling-cloud-gateways")
    assert r_post.status_code == 200, f"Post detail failed: {r_post.status_code}"
    assert "CVE-2026-8841" in r_post.text
    print("✓ Journal Advisory Detail page loaded successfully.")

    # 4. Customer Registration & Vault
    uname = f"operator_{secrets.token_hex(4)}"
    email = f"{uname}@testsec.io"
    pwd = "User@2026!Strong"
    r_reg = session.post(f"{BASE_URL}/register", data={
        "username": uname,
        "email": email,
        "password": pwd,
        "confirm_password": pwd,
        "telegram_handle": f"@{uname}"
    })
    assert r_reg.status_code in (200, 302), f"Registration failed: {r_reg.status_code}"
    print(f"✓ Customer registered: {uname}")

    r_vault = session.get(f"{BASE_URL}/vault")
    assert r_vault.status_code == 200, f"Vault failed: {r_vault.status_code}"
    assert uname in r_vault.text
    print("✓ Customer Vault accessed successfully.")

    # 5. Order Checkout via API
    checkout_payload = {
        "items": [
            {"sku": "LIC-BURP-PRO", "name": "Burp Suite Professional (v2026.10)", "price": 149.0, "qty": 1}
        ],
        "buyer_telegram": f"@{uname}",
        "buyer_note": "Modular architecture test checkout"
    }
    r_checkout = session.post(f"{BASE_URL}/api/checkout", json=checkout_payload)
    assert r_checkout.status_code == 200, f"Checkout failed: {r_checkout.status_code}"
    order_data = r_checkout.json()
    order_number = order_data.get("order_number")
    assert order_number, "Order number missing in checkout response"
    print(f"✓ Checkout processed: {order_number}")

    # 6. Admin Panel & Order Fulfillment
    admin_sess = requests.Session()
    r_admin_login = admin_sess.post(f"{BASE_URL}/admin/login", data={"identifier": "admin", "password": "Admin@2026"})
    assert r_admin_login.status_code == 200

    r_admin = admin_sess.get(f"{BASE_URL}/admin")
    assert r_admin.status_code == 200
    assert order_number in r_admin.text
    print("✓ Admin panel verified new order.")

    # Fulfill order via admin API
    conn = requests.get(f"{BASE_URL}/orders/{order_number}")
    assert conn.status_code == 200
    print("✓ Public order status lookup verified.")

    print("\n=== ALL MODULAR ARCHITECTURE WORKFLOW TESTS PASSED! ===")

if __name__ == "__main__":
    test_modular_app()
