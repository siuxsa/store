import requests
from bs4 import BeautifulSoup

BASE_URL = "http://127.0.0.1:5000"

def test_tool_requests_pipeline():
    print("=== TESTING TOOL REQUESTS PIPELINE & ORDER LOOKUP TRANSITION ===")
    session = requests.Session()

    # 1. Public Storefront Navigation Check
    r_home = requests.get(f"{BASE_URL}/")
    assert r_home.status_code == 200
    soup_home = BeautifulSoup(r_home.text, "html.parser")
    nav_links = [a.text.strip() for a in soup_home.select(".nav-center a")]
    print(f"✓ Found header nav links: {nav_links}")
    assert any("REQUEST TOOL" in l for l in nav_links), "Expected 'REQUEST TOOL' in header nav!"
    assert not any("ORDER LOOKUP" in l for l in nav_links), "'ORDER LOOKUP' should no longer be in main nav"
    print("✓ Main header navigation successfully updated: 'ORDER LOOKUP' transformed to 'REQUEST TOOL'.")

    # 2. Public Tool Request Page GET
    r_req_page = requests.get(f"{BASE_URL}/request")
    assert r_req_page.status_code == 200
    assert "REQUEST UNLISTED TOOLS" in r_req_page.text
    assert "CUSTOM SOURCING" in r_req_page.text
    assert "ALREADY PURCHASED AN ARSENAL SYSTEM" not in r_req_page.text, "Dashed 'Already purchased' box must be removed"
    assert "TRACK EXISTING ORDER TICKET" not in r_req_page.text, "Order ticket tracking box must be removed"
    soup_req = BeautifulSoup(r_req_page.text, "html.parser")
    assert soup_req.find(id="req-tool-name") is not None
    assert soup_req.find(id="req-category") is not None
    assert soup_req.find(id="req-urgency") is not None
    assert soup_req.find(id="req-telegram") is not None
    assert soup_req.find(id="req-specs") is not None
    print("✓ Public /request page renders all intake fields and operational briefing specs without order lookup callout.")

    # 3. Validation on POST /api/request-tool
    r_empty = requests.post(f"{BASE_URL}/api/request-tool", json={})
    assert r_empty.status_code == 400
    assert "tool" in r_empty.json().get("error", "").lower()

    r_no_contact = requests.post(f"{BASE_URL}/api/request-tool", json={"tool_name": "Test Tool 01"})
    assert r_no_contact.status_code == 400
    assert "telegram" in r_no_contact.json().get("error", "").lower()
    print("✓ Client submission validation properly blocks missing tool names and empty contact channels.")

    # 4. Successful Submission of Custom Tool Sourcing Brief
    req_payload = {
        "tool_name": "SpectreStrike Hardware RF C2 Transceiver",
        "category": "HARDWARE_C2",
        "urgency": "IMMEDIATE",
        "contact_telegram": "@operator_spectre_99",
        "contact_email": "spectre@cyber-sec.org",
        "budget_range": "5K_TO_20K",
        "technical_specs": "Sub-1GHz ISM band transceiver with encrypted spread-spectrum frequency hopping firmware and USB-C hardware casing.",
        "preferred_contact": "TELEGRAM"
    }
    r_sub = requests.post(f"{BASE_URL}/api/request-tool", json=req_payload)
    assert r_sub.status_code == 200, f"Submission failed: {r_sub.text}"
    sub_data = r_sub.json()
    assert sub_data.get("ok") is True
    test_req_id = sub_data.get("request_id")
    assert test_req_id and test_req_id.startswith("REQ-"), f"Unexpected request_id: {test_req_id}"
    print(f"✓ Successfully submitted custom tool procurement brief: Generated Ticket #{test_req_id}.")

    # 5. Order Lookup total removal & redirect to /request
    r_orders_bare = requests.get(f"{BASE_URL}/orders", allow_redirects=False)
    assert r_orders_bare.status_code in [302, 301]
    assert "/request" in r_orders_bare.headers.get("Location", "")
    print("✓ Bare /orders properly redirects away to /request.")

    r_orders_direct = requests.get(f"{BASE_URL}/orders/ORD-84920", allow_redirects=False)
    assert r_orders_direct.status_code in [302, 301]
    assert "/request" in r_orders_direct.headers.get("Location", "")
    print("✓ Direct ticket URL /orders/ORD-84920 redirects to /request.")

    # 6. Admin Panel: Tool Requests Intake Queue & Management
    # 6a. Block unauthenticated access
    r_admin_unauth = requests.get(f"{BASE_URL}/api/admin/tool-requests")
    assert r_admin_unauth.status_code in [302, 401, 403]

    # 6b. Login Master Admin
    r_login = session.post(f"{BASE_URL}/admin/login", data={"identifier": "admin", "password": "Admin@2026"})
    assert r_login.status_code == 200

    # 6c. Verify admin UI has subtab and module
    r_admin = session.get(f"{BASE_URL}/admin")
    assert r_admin.status_code == 200
    soup_admin = BeautifulSoup(r_admin.text, "html.parser")
    subtab_req = soup_admin.find("button", attrs={"data-subtab": "requests"})
    assert subtab_req is not None, "Missing [03] CUSTOM TOOL REQUESTS subtab button!"
    assert "CUSTOM TOOL REQUESTS" in subtab_req.text

    mod_req = soup_admin.find(id="mod-tool-requests")
    assert mod_req is not None, "Missing #mod-tool-requests module section in admin panel!"
    assert test_req_id in r_admin.text, f"Newly submitted ticket #{test_req_id} not found in admin table HTML!"
    print("✓ Admin panel renders [03] CUSTOM TOOL REQUESTS subtab and live queue with newly submitted request.")

    # 6d. Test Admin Status Update API
    r_list = session.get(f"{BASE_URL}/api/admin/tool-requests")
    assert r_list.status_code == 200
    all_reqs = r_list.json().get("requests", [])
    matching = [r for r in all_reqs if r["request_id"] == test_req_id]
    assert len(matching) == 1, f"Could not find matching request #{test_req_id}"
    db_id = matching[0]["id"]

    r_update = session.post(f"{BASE_URL}/api/admin/tool-requests/{db_id}/status", json={
        "status": "SOURCING",
        "admin_notes": "Sourced unit from lab in Germany. Arranging private Telegram escrow."
    })
    assert r_update.status_code == 200
    assert r_update.json().get("ok") is True
    print(f"✓ Master Admin updated request #{test_req_id} status to 'SOURCING' with internal notes.")

    # 6e. Clean up test request via DELETE API
    r_del = session.delete(f"{BASE_URL}/api/admin/tool-requests/{db_id}")
    assert r_del.status_code == 200
    assert r_del.json().get("ok") is True
    print(f"✓ Master Admin cleanly purged test request #{test_req_id}.")

    print("\n=== ALL TOOL REQUESTS & NAVIGATION TESTS PASSED 100%! ===")

if __name__ == "__main__":
    test_tool_requests_pipeline()
