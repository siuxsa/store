import requests
from bs4 import BeautifulSoup
import sqlite3

BASE_URL = "http://127.0.0.1:5000"

def test_data_management_and_export():
    print("=== TESTING TELEMETRY & ANALYTICS DATA MANAGEMENT & EXPORT SYSTEM ===")
    session = requests.Session()

    # 1. Block unauthenticated access to export, stats, and purge
    r_stats_unauth = requests.get(f"{BASE_URL}/api/admin/data/stats")
    assert r_stats_unauth.status_code in [302, 401, 403], f"Expected auth block, got {r_stats_unauth.status_code}"
    
    r_export_unauth = requests.get(f"{BASE_URL}/api/admin/analytics/export?format=json")
    assert r_export_unauth.status_code in [302, 401, 403], f"Expected auth block, got {r_export_unauth.status_code}"

    r_purge_unauth = requests.post(f"{BASE_URL}/api/admin/data/purge", json={"action": "analytics_all"})
    assert r_purge_unauth.status_code in [302, 401, 403], f"Expected auth block, got {r_purge_unauth.status_code}"
    print("✓ Unauthenticated access to telemetry export, stats, and purge endpoints properly blocked.")

    # 2. Login as Master Admin
    r_login = session.post(f"{BASE_URL}/admin/login", data={"identifier": "admin", "password": "Admin@2026"})
    assert r_login.status_code == 200, "Master Admin login failed"
    print("✓ Master Admin authenticated successfully.")

    # 3. Test stats endpoint
    r_stats = session.get(f"{BASE_URL}/api/admin/data/stats")
    assert r_stats.status_code == 200, f"Stats failed: {r_stats.text}"
    stats_data = r_stats.json()
    assert stats_data.get("ok") is True
    st = stats_data["stats"]
    assert "pageviews" in st and "events" in st and "unique_visitors" in st and "db_size_kb" in st
    print(f"✓ Retrieved live telemetry metrics: Pageviews={st['pageviews']}, Events={st['events']}, Unique Visitors={st['unique_visitors']}, DB Size={st['db_size_kb']} KB")

    # 4. Insert test telemetry records to verify export and purge mechanics
    conn = sqlite3.connect("cyber.db")
    conn.execute("DELETE FROM analytics_pageviews WHERE visit_token LIKE 'TEST_EXPORT_TOKEN_%'")
    conn.execute("DELETE FROM analytics_events WHERE visitor_id LIKE 'vis_test_export%'")
    conn.execute("""
        INSERT INTO analytics_pageviews (visit_token, visitor_id, session_id, page_type, target_slug, duration_seconds, max_scroll_pct, created_at, last_ping_at)
        VALUES ('TEST_EXPORT_TOKEN_99', 'vis_test_export', 'sess_test_export', 'TEST', 'test-slug', 15, 75, '2020-01-01 00:00:00', '2020-01-01 00:00:15')
    """)
    conn.execute("""
        INSERT INTO analytics_events (visitor_id, session_id, event_type, source_page, target_sku, created_at)
        VALUES ('vis_test_export', 'sess_test_export', 'TEST_EVENT', '/test', 'TEST_SKU', '2020-01-01 00:00:00')
    """)
    conn.commit()

    # Capture core data counts before purge
    reviews_before = conn.execute("SELECT COUNT(*) FROM product_reviews").fetchone()[0]
    comments_before = conn.execute("SELECT COUNT(*) FROM post_comments").fetchone()[0]
    products_before = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    orders_before = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    conn.close()

    # 5. Test Export Endpoints
    # 5a. JSON Export
    r_json_export = session.get(f"{BASE_URL}/api/admin/analytics/export?format=json")
    assert r_json_export.status_code == 200, f"JSON export failed: {r_json_export.status_code}"
    assert "attachment; filename=" in r_json_export.headers.get("Content-Disposition", "")
    assert "application/json" in r_json_export.headers.get("Content-Type", "")
    export_json = r_json_export.json()
    assert "analytics_pageviews" in export_json and "analytics_events" in export_json
    assert any(pv.get("visit_token") == "TEST_EXPORT_TOKEN_99" for pv in export_json["analytics_pageviews"])
    print(f"✓ JSON Export successful: {len(export_json['analytics_pageviews'])} pageviews and {len(export_json['analytics_events'])} events exported.")

    # 5b. CSV Export - Pageviews
    r_csv_pv = session.get(f"{BASE_URL}/api/admin/analytics/export?format=csv&type=pageviews")
    assert r_csv_pv.status_code == 200, f"CSV pageviews export failed: {r_csv_pv.status_code}"
    assert "text/csv" in r_csv_pv.headers.get("Content-Type", "")
    assert "Visit Token,Visitor ID,Session ID" in r_csv_pv.text
    assert "TEST_EXPORT_TOKEN_99" in r_csv_pv.text
    print("✓ CSV Pageviews Export successful and contains header and records.")

    # 5c. CSV Export - Events
    r_csv_ev = session.get(f"{BASE_URL}/api/admin/analytics/export?format=csv&type=events")
    assert r_csv_ev.status_code == 200, f"CSV events export failed: {r_csv_ev.status_code}"
    assert "text/csv" in r_csv_ev.headers.get("Content-Type", "")
    assert "Event Type,Source Page,Target SKU" in r_csv_ev.text
    assert "TEST_EVENT" in r_csv_ev.text
    print("✓ CSV Events Export successful and contains header and records.")

    # 6. Verify core data protection: illegal purge actions MUST fail with 400
    for illegal_target in ["reviews", "comments", "orders", "users", "audit_logs", "all"]:
        r_illegal = session.post(f"{BASE_URL}/api/admin/data/purge", json={"action": illegal_target})
        assert r_illegal.status_code == 400, f"Expected 400 for illegal purge action '{illegal_target}', got {r_illegal.status_code}"
        assert "Strict Data Isolation" in r_illegal.json().get("error", "")
    print("✓ Core data security verified: Attempting to purge reviews, comments, orders, users, or audit logs is strictly rejected.")

    # 7. Test Purge older than 30 days
    r_purge_old = session.post(f"{BASE_URL}/api/admin/data/purge", json={"action": "analytics_all", "older_than_days": 30})
    assert r_purge_old.status_code == 200, f"Purge failed: {r_purge_old.text}"
    p_data = r_purge_old.json()
    assert p_data.get("ok") is True
    assert p_data["deleted_count"] >= 2, f"Expected at least 2 deleted rows, got {p_data['deleted_count']}"
    print(f"✓ Successfully purged telemetry records older than 30 days (deleted {p_data['deleted_count']} rows).")

    # 8. Verify core site content remains 100% UNTOUCHED
    conn = sqlite3.connect("cyber.db")
    reviews_after = conn.execute("SELECT COUNT(*) FROM product_reviews").fetchone()[0]
    comments_after = conn.execute("SELECT COUNT(*) FROM post_comments").fetchone()[0]
    products_after = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    orders_after = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    conn.close()

    assert reviews_before == reviews_after, f"Reviews changed! Before={reviews_before}, After={reviews_after}"
    assert comments_before == comments_after, f"Comments changed! Before={comments_before}, After={comments_after}"
    assert products_before == products_after, f"Products changed! Before={products_before}, After={products_after}"
    assert orders_before == orders_after, f"Orders changed! Before={orders_before}, After={orders_after}"
    print(f"✓ Zero Core Side-Effects Verified: Reviews ({reviews_after}), Comments ({comments_after}), Products ({products_after}), Orders ({orders_after}) are 100% preserved.")

    # 9. Verify UI elements exist in Settings HTML
    r_admin = session.get(f"{BASE_URL}/admin")
    assert r_admin.status_code == 200
    soup = BeautifulSoup(r_admin.text, "html.parser")
    assert soup.find(id="dms-count-pageviews") is not None, "Missing #dms-count-pageviews"
    assert soup.find(id="dms-count-events") is not None, "Missing #dms-count-events"
    assert soup.find(id="dms-count-visitors") is not None, "Missing #dms-count-visitors"
    assert soup.find(id="dms-count-dbsize") is not None, "Missing #dms-count-dbsize"
    assert soup.find(id="dms-status-banner") is not None, "Missing #dms-status-banner"
    assert "Strict Data Isolation Guarantee" in r_admin.text
    assert "EXPORT COMPLETE TELEMETRY (JSON)" in r_admin.text
    assert "PAGEVIEWS (CSV)" in r_admin.text
    assert "AD EVENTS (CSV)" in r_admin.text
    print("✓ Verified all Telemetry Data Management & Export UI components exist in Settings module.")

    # 10. Test vacuum optimization endpoint
    r_vac = session.post(f"{BASE_URL}/api/admin/data/purge", json={"action": "vacuum"})
    assert r_vac.status_code == 200, f"Vacuum failed: {r_vac.text}"
    vac_data = r_vac.json()
    assert vac_data.get("ok") is True
    print(f"✓ Successfully executed SQLite VACUUM & REINDEX: {vac_data['message']} (Current size: {vac_data['db_size_kb']} KB)")

    print("\n=== ALL TELEMETRY & ANALYTICS DATA MANAGEMENT TESTS PASSED 100%! ===")

if __name__ == "__main__":
    test_data_management_and_export()
