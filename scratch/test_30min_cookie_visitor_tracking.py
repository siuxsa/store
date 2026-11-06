import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import time
from datetime import datetime, timedelta

from app import app
from database import get_db
from core.security import VISITOR_COOKIE_NAME, SESSION_COOKIE_NAME, VISITOR_COOKIE_MAX_AGE

def test_cryptographic_cookie_and_number_counting():
    print("=== TESTING CRYPTOGRAPHIC COOKIE & VISITOR NUMBER COUNTING ===")
    assert VISITOR_COOKIE_MAX_AGE == 1800, f"Expected 1800 seconds (30 mins), got {VISITOR_COOKIE_MAX_AGE}"
    print("✓ VISITOR_COOKIE_MAX_AGE is 1800 seconds (30 minutes).")

    client = app.test_client()

    # Step 1: Clean test tables
    conn = get_db()
    conn.execute("DELETE FROM analytics_pageviews WHERE id > 1100")
    conn.execute("DELETE FROM visitor_cookie_registry")
    conn.commit()
    conn.close()

    # Step 2: First Visit to Home (No Cookie)
    res1 = client.get("/", headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/128.0", "CF-Connecting-IP": "198.51.100.99"})
    assert res1.status_code == 200
    
    # Check Set-Cookie headers
    cookie_header = res1.headers.get_all("Set-Cookie")
    vid_cookie = None
    for ch in cookie_header:
        if VISITOR_COOKIE_NAME in ch:
            vid_cookie = ch
            break
    
    assert vid_cookie is not None, "Visitor cookie not set on first visit!"
    assert "Max-Age=1800" in vid_cookie, f"Max-Age=1800 missing from Set-Cookie: {vid_cookie}"
    raw_cookie_1 = client.get_cookie(VISITOR_COOKIE_NAME).value
    
    # 1. VERIFY COOKIE IS HIGH-ENTROPY CRYPTOGRAPHIC (e.g. 64-char hex token)
    assert len(raw_cookie_1) == 64, f"Expected 64-char 256-bit cryptographic cookie, got length {len(raw_cookie_1)}: {raw_cookie_1}"
    print(f"✓ Visit 1: Browser received 256-bit CRYPTOGRAPHIC cookie: {raw_cookie_1[:12]}...{raw_cookie_1[-8:]} (Max-Age=1800).")

    # Sync telemetry for Home visit
    sync_res1 = client.post("/api/v1/sync/state",
        data=json.dumps({
            "page_type": "HOME",
            "target_slug": "",
            "target_title": "Home // Threat Matrix",
            "duration_seconds": 15,
            "max_scroll_pct": 25,
            "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/128.0"
        }),
        content_type="application/json",
        headers={"CF-Connecting-IP": "198.51.100.99"}
    )
    assert sync_res1.status_code == 200

    conn = get_db()
    row_1 = conn.execute("SELECT visit_token, visitor_id, session_id FROM analytics_pageviews ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()

    assert row_1 is not None
    # 2. VERIFY DB STORES ONLY THE VISITOR NUMBER COUNT (NOT THE FULL CRYPTOGRAPHIC COOKIE!)
    assert row_1["visitor_id"] != raw_cookie_1, "CRITICAL ERROR: Full cryptographic cookie must NOT be stored in analytics!"
    assert row_1["visitor_id"] == "1", f"Expected visitor number '1', got: {row_1['visitor_id']}"
    assert row_1["session_id"] == "1", f"Expected session number '1', got: {row_1['session_id']}"
    assert row_1["visit_token"] == "1", f"Expected visit_token number '1', got: {row_1['visit_token']}"
    print(f"✓ DB verified: Stored ONLY the visitor count number (visitor_id='{row_1['visitor_id']}', session_id='{row_1['session_id']}'). Full cookie is NOT stored!")

    # Step 3: Second Visit to a DIFFERENT page (/shop) with same cryptographic cookie
    res2 = client.get("/shop", headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/128.0", "CF-Connecting-IP": "198.51.100.99"})
    assert res2.status_code == 200
    raw_cookie_2 = client.get_cookie(VISITOR_COOKIE_NAME).value
    assert raw_cookie_2 == raw_cookie_1, "Cryptographic cookie changed despite active session!"

    sync_res2 = client.post("/api/v1/sync/state",
        data=json.dumps({
            "page_type": "SHOP",
            "target_slug": "shop",
            "target_title": "Arsenal Catalog",
            "duration_seconds": 20,
            "max_scroll_pct": 50,
            "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/128.0"
        }),
        content_type="application/json",
        headers={"CF-Connecting-IP": "198.51.100.99"}
    )
    assert sync_res2.status_code == 200

    conn = get_db()
    uniques_2 = conn.execute("SELECT COUNT(DISTINCT visitor_id) FROM analytics_pageviews WHERE visitor_id = '1'").fetchone()[0]
    total_rows_2 = conn.execute("SELECT COUNT(*) FROM analytics_pageviews WHERE visitor_id = '1'").fetchone()[0]
    updated_row = conn.execute("SELECT page_type, target_slug, duration_seconds FROM analytics_pageviews WHERE visitor_id = '1'").fetchone()
    conn.close()

    assert uniques_2 == 1, f"Expected 1 unique visitor count, got {uniques_2}"
    assert total_rows_2 == 1, f"Expected 1 total row for whole website, got {total_rows_2}"
    assert updated_row["page_type"] == "SHOP"
    print(f"✓ Whole website maintains 1 user (visitor #1) across all pages! Location updated to SHOP.")

    # Step 4: Third Visit to a Product Page (/product/burp-suite-professional-license)
    res3 = client.get("/product/burp-suite-professional-license", headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/128.0", "CF-Connecting-IP": "198.51.100.99"})
    assert res3.status_code == 200

    sync_res3 = client.post("/api/v1/sync/state",
        data=json.dumps({
            "page_type": "PRODUCT",
            "target_slug": "burp-suite-professional-license",
            "target_title": "Burp Suite Professional (v2026.10)",
            "duration_seconds": 35,
            "max_scroll_pct": 75,
            "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/128.0"
        }),
        content_type="application/json",
        headers={"CF-Connecting-IP": "198.51.100.99"}
    )
    assert sync_res3.status_code == 200

    conn = get_db()
    total_rows_3 = conn.execute("SELECT COUNT(*) FROM analytics_pageviews WHERE visitor_id = '1'").fetchone()[0]
    prod_event = conn.execute("SELECT COUNT(*) FROM analytics_events WHERE visitor_id = '1' AND event_type = 'PRODUCT_VIEW' AND target_sku = 'burp-suite-professional-license'").fetchone()[0]
    conn.close()

    assert total_rows_3 == 1
    assert prod_event >= 1
    print("✓ Product view recorded in analytics_events; whole website session remains 1 user.")

    # Step 5: Simulation of 30-min cookie destruction (session ends, cookie destroyed)
    client.delete_cookie(VISITOR_COOKIE_NAME)
    client.delete_cookie(SESSION_COOKIE_NAME)

    res4 = client.get("/", headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/128.0", "CF-Connecting-IP": "198.51.100.99"})
    assert res4.status_code == 200
    raw_cookie_3 = client.get_cookie(VISITOR_COOKIE_NAME).value
    assert len(raw_cookie_3) == 64
    assert raw_cookie_3 != raw_cookie_1, "Expected new cryptographic cookie after 30-min destruction!"

    sync_res4 = client.post("/api/v1/sync/state",
        data=json.dumps({
            "page_type": "HOME",
            "target_slug": "",
            "target_title": "Home // Threat Matrix",
            "duration_seconds": 10,
            "max_scroll_pct": 10,
            "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/128.0"
        }),
        content_type="application/json",
        headers={"CF-Connecting-IP": "198.51.100.99"}
    )
    assert sync_res4.status_code == 200

    conn = get_db()
    row_new = conn.execute("SELECT visitor_id, session_id FROM analytics_pageviews ORDER BY id DESC LIMIT 1").fetchone()
    total_uniques = conn.execute("SELECT COUNT(DISTINCT visitor_id) FROM analytics_pageviews WHERE visitor_id IN ('1', '2')").fetchone()[0]
    conn.close()

    assert row_new["visitor_id"] == "2", f"Expected visitor number '2', got: {row_new['visitor_id']}"
    assert total_uniques == 2, f"Expected 2 unique visitor numbers, got {total_uniques}"
    print(f"✓ Next session assigned visitor number '2'! Total counted visitors: {total_uniques}.")

    print("\nALL CRYPTOGRAPHIC COOKIE & VISITOR NUMBER COUNTING TESTS PASSED 100%!")

if __name__ == "__main__":
    test_cryptographic_cookie_and_number_counting()
