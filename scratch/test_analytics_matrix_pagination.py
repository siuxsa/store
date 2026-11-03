import requests
from bs4 import BeautifulSoup

BASE_URL = "http://127.0.0.1:5000"

def test_analytics_matrix_and_pagination():
    print("=== TESTING ANALYTICS SUBTABS, 10-PREVIEW & 20/PAGE MATRIX ===")
    session = requests.Session()

    # 1. Login as Master Admin
    login_resp = session.post(f"{BASE_URL}/admin/login", data={"identifier": "admin", "password": "Admin@2026"})
    assert login_resp.status_code == 200, f"Master Admin login failed: {login_resp.status_code}"
    print("✓ Master Admin authenticated successfully.")

    # 2. Fetch Admin Dashboard HTML
    admin_resp = session.get(f"{BASE_URL}/admin")
    assert admin_resp.status_code == 200, f"Admin panel failed: {admin_resp.status_code}"
    soup = BeautifulSoup(admin_resp.text, 'html.parser')

    # 3. Check Analytics Subtabs
    subtabs_analytics = soup.find(id='subtabs-analytics')
    assert subtabs_analytics is not None, "Missing #subtabs-analytics!"
    subtab_btns = subtabs_analytics.find_all('button', class_='subnav-item')
    subtab_keys = [b.get('data-subtab') for b in subtab_btns]
    print(f"✓ Found Analytics subtabs: {subtab_keys}")
    assert 'overview' in subtab_keys, "Missing 'overview' subtab"
    assert 'matrix-full' in subtab_keys, "Missing 'matrix-full' subtab"
    assert len(subtab_keys) == 2, f"Expected exactly 2 clean subtabs, got {len(subtab_keys)}"

    # Ensure confusing old subtabs are gone
    for deprecated in ['prod-telemetry', 'journal-telemetry', 'stream', 'threat-telemetry']:
        assert deprecated not in subtab_keys, f"Deprecated subtab {deprecated} still present!"
    print("✓ Confusing previous subtabs successfully removed.")

    # 4. Check Granular Matrix header & preview section
    matrix_header = soup.find(string=lambda t: t and "// GRANULAR PERFORMANCE & TELEMETRY MATRIX" in t)
    assert matrix_header is not None, "Missing '// GRANULAR PERFORMANCE & TELEMETRY MATRIX' header"
    print("✓ Found '// GRANULAR PERFORMANCE & TELEMETRY MATRIX' section.")

    # Verify badge showing last 10
    badge_10 = soup.find(string=lambda t: t and "SHOWING LAST 10" in t)
    assert badge_10 is not None, "Missing 'SHOWING LAST 10' badge"
    print("✓ Verified 'SHOWING LAST 10' badge.")

    # Verify SHOW ALL button exists
    show_all_btn = soup.find(lambda el: el.name == 'button' and 'SHOW ALL (20 / PAGE)' in el.text)
    assert show_all_btn is not None, "Missing 'SHOW ALL (20 / PAGE)' button"
    print("✓ Found 'SHOW ALL (20 / PAGE)' button.")

    # 5. Check Dedicated Full Matrix Module
    matrix_mod = soup.find(id='mod-analytics-matrix')
    assert matrix_mod is not None, "Missing #mod-analytics-matrix module!"
    print("✓ Found #mod-analytics-matrix dedicated section.")

    # Check tables in matrix module
    assert soup.find(id='full-matrix-products') is not None, "Missing #full-matrix-products"
    assert soup.find(id='full-matrix-blogs') is not None, "Missing #full-matrix-blogs"
    assert soup.find(id='full-matrix-stream') is not None, "Missing #full-matrix-stream"
    print("✓ Found all 3 full matrix tables (Catalog, Intel Reach, Live Client Stream).")

    # Verify Pinned Header and Viewport Scroll Classes
    header_pinned = soup.find('div', class_='matrix-header-pinned')
    assert header_pinned is not None, "Missing .matrix-header-pinned!"
    card_wrap = soup.find('div', class_='matrix-card-wrap')
    assert card_wrap is not None, "Missing .matrix-card-wrap!"
    viewports = soup.find_all('div', class_='matrix-table-viewport')
    assert len(viewports) == 3, f"Expected 3 .matrix-table-viewport elements, found {len(viewports)}"
    pagination_footer = soup.find('div', class_='matrix-pagination-footer')
    assert pagination_footer is not None, "Missing .matrix-pagination-footer!"
    print("✓ Verified .matrix-header-pinned, .matrix-card-wrap, 3x .matrix-table-viewport, and .matrix-pagination-footer.")

    # Check pagination elements
    assert soup.find(id='matrix-page-range') is not None, "Missing #matrix-page-range"
    assert soup.find(id='matrix-total-count') is not None, "Missing #matrix-total-count"
    assert soup.find(id='matrix-current-page') is not None, "Missing #matrix-current-page"
    assert soup.find(id='matrix-total-pages') is not None, "Missing #matrix-total-pages"
    assert soup.find(id='btn-matrix-prev') is not None, "Missing #btn-matrix-prev"
    assert soup.find(id='btn-matrix-next') is not None, "Missing #btn-matrix-next"
    print("✓ Found all pagination controls (PREV, NEXT, PAGE X/Y, RANGE indicator).")

    # 6. Verify Analytics Summary API endpoint
    api_resp = session.get(f"{BASE_URL}/api/admin/analytics/summary?days=7")
    assert api_resp.status_code == 200, f"Analytics API failed: {api_resp.status_code}"
    api_data = api_resp.json()
    assert 'kpis' in api_data, "Missing kpis in analytics data"
    assert 'products' in api_data, "Missing products in analytics data"
    assert 'blogs' in api_data, "Missing blogs in analytics data"
    assert 'recent_stream' in api_data, "Missing recent_stream in analytics data"
    print(f"✓ Analytics API valid: {len(api_data.get('products', []))} products, {len(api_data.get('blogs', []))} blogs, {len(api_data.get('recent_stream', []))} stream records.")

    print("\n=== ALL ANALYTICS MATRIX & PAGINATION TESTS PASSED! ===")

if __name__ == '__main__':
    test_analytics_matrix_and_pagination()
