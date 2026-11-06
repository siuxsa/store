import os
import sys
import json
import sqlite3

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from app import app
from database import get_db, init_db
from core.security import get_client_ip, get_client_user_agent, VISITOR_COOKIE_NAME, SESSION_COOKIE_NAME

def test_analytics_cookie_ua_and_cloudflare_ip():
    print("=== TESTING ANALYTICS COOKIE TRACKING, USER AGENT & CLOUDFLARE IP ===")
    init_db()

    client = app.test_client()

    # -------------------------------------------------------------------------
    # TEST 1: Cloudflare & Real IP Resolution
    # -------------------------------------------------------------------------
    print("\n[TEST 1] Testing Cloudflare & Real IP Extraction...")
    with app.test_request_context("/", headers={"CF-Connecting-IP": "104.28.19.45"}):
        ip = get_client_ip()
        assert ip == "104.28.19.45", f"Expected 104.28.19.45 from CF-Connecting-IP, got {ip}"
    print("✓ Successfully extracted client IP from Cloudflare CF-Connecting-IP header.")

    with app.test_request_context("/", headers={"True-Client-IP": "198.51.100.99", "X-Forwarded-For": "172.64.0.1"}):
        ip = get_client_ip()
        assert ip == "198.51.100.99", f"Expected 198.51.100.99 from True-Client-IP, got {ip}"
    print("✓ Successfully prioritized True-Client-IP over proxy chain.")

    with app.test_request_context("/", headers={"X-Forwarded-For": "203.0.113.88, 172.70.1.2"}):
        ip = get_client_ip()
        assert ip == "203.0.113.88", f"Expected first IP from X-Forwarded-For, got {ip}"
    print("✓ Successfully parsed leftmost client IP from X-Forwarded-For chain.")

    # -------------------------------------------------------------------------
    # TEST 2: Server Provisions Visitor Cookie
    # -------------------------------------------------------------------------
    print("\n[TEST 2] Testing Server Visitor Cookie Provisioning...")
    resp = client.get("/")
    assert resp.status_code == 200

    # Verify server provided cookies
    cookie_headers = resp.headers.getlist("Set-Cookie")
    set_cookie_str = "; ".join(cookie_headers)
    assert VISITOR_COOKIE_NAME in set_cookie_str, f"{VISITOR_COOKIE_NAME} not found in Set-Cookie headers: {set_cookie_str}"
    assert SESSION_COOKIE_NAME in set_cookie_str, f"{SESSION_COOKIE_NAME} not found in Set-Cookie headers: {set_cookie_str}"
    print(f"✓ Server automatically provisions '{VISITOR_COOKIE_NAME}' and '{SESSION_COOKIE_NAME}' cookies.")

    # Extract the visitor ID from cookie
    cookie = client.get_cookie(VISITOR_COOKIE_NAME)
    visitor_id = cookie.value if cookie else None
    assert visitor_id and visitor_id.startswith("VID-"), f"Invalid visitor ID format: {visitor_id}"
    print(f"✓ Visitor received persistent server ID: {visitor_id}")

    # -------------------------------------------------------------------------
    # TEST 3: User Visits Same Page Repeatedly -> Treated as ONE User
    # -------------------------------------------------------------------------
    print("\n[TEST 3] Testing Repeated Same-Page Visits by Same User...")
    test_ua = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    cf_client_ip = "198.51.100.77"

    headers = {
        "CF-Connecting-IP": cf_client_ip,
        "User-Agent": test_ua
    }

    # First visit to /shop
    payload1 = {
        "visit_token": "vtok_test_001",
        "page_type": "SHOP",
        "target_slug": "",
        "target_title": "Arsenal Catalog",
        "duration_seconds": 12,
        "max_scroll_pct": 35,
        "user_agent": test_ua
    }
    r1 = client.post("/api/v1/sync/state", json=payload1, headers=headers)
    assert r1.status_code == 200
    res1_data = r1.get_json()
    assert res1_data["visitor_id"] == visitor_id, f"Expected {visitor_id}, got {res1_data['visitor_id']}"
    assert res1_data["ip"] == cf_client_ip, f"Expected {cf_client_ip}, got {res1_data['ip']}"

    # Repeated visit/refresh to /shop 5 seconds later by the same user with a new visit_token
    payload2 = {
        "visit_token": "vtok_test_002",
        "page_type": "SHOP",
        "target_slug": "",
        "target_title": "Arsenal Catalog",
        "duration_seconds": 45,
        "max_scroll_pct": 80,
        "user_agent": test_ua
    }
    r2 = client.post("/api/v1/sync/state", json=payload2, headers=headers)
    assert r2.status_code == 200
    res2_data = r2.get_json()
    assert res2_data["visitor_id"] == visitor_id, "Visitor ID changed across requests!"

    # Verify database: only ONE pageview record exists for this user on /shop, and it updated duration/scroll!
    conn = get_db()
    rows = conn.execute("""
        SELECT id, visit_token, visitor_id, page_type, target_slug, duration_seconds, max_scroll_pct, user_agent, ip_address
        FROM analytics_pageviews
        WHERE visitor_id = ? AND page_type = 'SHOP'
    """, (visitor_id,)).fetchall()
    conn.close()

    assert len(rows) == 1, f"Expected exactly 1 deduplicated pageview for same user on /shop, found {len(rows)}!"
    row = dict(rows[0])
    assert row["duration_seconds"] == 45, f"Expected duration 45, got {row['duration_seconds']}"
    assert row["max_scroll_pct"] == 80, f"Expected scroll 80%, got {row['max_scroll_pct']}"
    assert row["user_agent"] == test_ua, f"Expected exact client user agent, got {row['user_agent']}"
    assert row["ip_address"] == cf_client_ip, f"Expected Cloudflare IP {cf_client_ip}, got {row['ip_address']}"
    print("✓ Same user visiting same page repeatedly is tracked as ONE user entity without multiplying pageview rows.")
    print("✓ Full User-Agent preserved in database (not hardcoded Windows/Linux):", row["user_agent"][:40], "...")
    print("✓ Real Cloudflare IP recorded in analytics:", row["ip_address"])

    # -------------------------------------------------------------------------
    # TEST 4: Admin Analytics Summary API returns user_agent and ip_address
    # -------------------------------------------------------------------------
    print("\n[TEST 4] Testing Admin Analytics API Data Stream...")
    with client.session_transaction() as sess:
        sess["admin_id"] = 1
        sess["admin_username"] = "admin"

    resp_summary = client.get("/api/admin/analytics/summary?days=14")
    assert resp_summary.status_code == 200
    summary_data = resp_summary.get_json()

    assert "recent_stream" in summary_data
    stream_items = summary_data["recent_stream"]
    assert len(stream_items) > 0

    latest_item = stream_items[0]
    assert "user_agent" in latest_item, "user_agent field missing from recent_stream!"
    assert "ip_address" in latest_item, "ip_address field missing from recent_stream!"
    assert "browser_breakdown" in summary_data, "browser_breakdown missing from summary data!"
    print("✓ Admin analytics summary API successfully delivers 'user_agent', 'ip_address', and 'browser_breakdown'.")

    print("\n=== ALL ANALYTICS, COOKIE, USER AGENT & CLOUDFLARE IP TESTS PASSED 100%! ===")

if __name__ == "__main__":
    test_analytics_cookie_ua_and_cloudflare_ip()
