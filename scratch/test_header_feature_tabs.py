import requests
from bs4 import BeautifulSoup

BASE_URL = "http://127.0.0.1:5000"

def test_header_feature_tabs():
    print("=== TESTING ADMIN HEADER FEATURE BUTTONS & PRODUCT/FEATURE SUBTABS ===")
    session = requests.Session()

    # 1. Login as Master Admin
    login_resp = session.post(f"{BASE_URL}/admin/login", data={"identifier": "admin", "password": "Admin@2026"})
    assert login_resp.status_code == 200, f"Master Admin login failed: {login_resp.status_code}"
    print("✓ Master Admin authenticated successfully.")

    # 2. Fetch Admin Dashboard HTML
    admin_resp = session.get(f"{BASE_URL}/admin")
    assert admin_resp.status_code == 200, f"Admin panel failed: {admin_resp.status_code}"
    soup = BeautifulSoup(admin_resp.text, 'html.parser')

    # 3. Verify Header Navigation & Primary Feature Buttons
    header_nav = soup.find('nav', class_='admin-header-nav')
    assert header_nav is not None, "Missing .admin-header-nav in header!"
    print("✓ Verified .admin-header-nav exists in admin header.")

    feature_btns = header_nav.find_all('button', class_='admin-header-btn')
    feature_names = [btn.get('data-feature') for btn in feature_btns]
    print(f"✓ Found header feature buttons: {feature_names}")

    assert 'analytics' in feature_names, "Missing analytics header button"
    assert 'products' in feature_names, "Missing products header button"
    assert 'journal' in feature_names, "Missing journal header button"
    assert 'orders' in feature_names, "Missing orders header button"
    assert 'system' in feature_names, "Missing system & security header button"

    # Verify default button is active analytics
    analytics_btn = header_nav.find('button', attrs={'data-feature': 'analytics'})
    assert 'active' in analytics_btn.get('class', []), "Default analytics header button must have 'active' class!"
    print("✓ Verified ANALYTICS is the default active button in header.")

    # 4. Verify Subtab Strip & Groups
    subnav_strip = soup.find('nav', class_='admin-subnav-strip')
    assert subnav_strip is not None, "Missing .admin-subnav-strip navigation strip!"
    print("✓ Verified .admin-subnav-strip exists beneath header.")

    # Verify Subtabs for Products
    prod_subtabs = soup.find(id='subtabs-products')
    assert prod_subtabs is not None, "Missing #subtabs-products container!"
    prod_subtab_btns = prod_subtabs.find_all('button', class_='subnav-item')
    prod_subtab_names = [b.get('data-subtab') for b in prod_subtab_btns]
    print(f"✓ Found Product subtabs: {prod_subtab_names}")
    assert 'catalog' in prod_subtab_names, "Missing 'catalog' subtab under products"
    assert 'studio' in prod_subtab_names, "Missing 'studio' subtab under products"
    assert 'curation' in prod_subtab_names, "Missing 'curation' subtab under products"
    assert 'reviews' in prod_subtab_names, "Missing 'reviews' subtab under products"

    # Verify Subtabs for Journal
    journal_subtabs = soup.find(id='subtabs-journal')
    assert journal_subtabs is not None, "Missing #subtabs-journal container!"
    journal_subtab_names = [b.get('data-subtab') for b in journal_subtabs.find_all('button', class_='subnav-item')]
    print(f"✓ Found Journal subtabs: {journal_subtab_names}")
    assert 'dispatches' in journal_subtab_names
    assert 'studio' in journal_subtab_names
    assert 'curation' in journal_subtab_names
    assert 'comments' in journal_subtab_names

    # Verify Subtabs for Orders
    order_subtabs = soup.find(id='subtabs-orders')
    assert order_subtabs is not None, "Missing #subtabs-orders container!"
    order_subtab_names = [b.get('data-subtab') for b in order_subtabs.find_all('button', class_='subnav-item')]
    print(f"✓ Found Orders subtabs: {order_subtab_names}")
    assert 'all' in order_subtab_names
    assert 'pending' in order_subtab_names

    # Verify Subtabs for System & Security
    sys_subtabs = soup.find(id='subtabs-system')
    assert sys_subtabs is not None, "Missing #subtabs-system container!"
    sys_subtab_names = [b.get('data-subtab') for b in sys_subtabs.find_all('button', class_='subnav-item')]
    print(f"✓ Found System & Security subtabs: {sys_subtab_names}")
    assert 'settings' in sys_subtab_names
    assert 'seo' in sys_subtab_names
    assert 'themes-visual' in sys_subtab_names
    assert 'themes-text' in sys_subtab_names
    assert 'users' in sys_subtab_names
    assert 'audit' in sys_subtab_names

    # 5. Verify All Target Modules Exist in DOM
    expected_modules = [
        'mod-analytics',
        'mod-analytics-matrix',
        'mod-products',
        'mod-product-editor',
        'mod-curation-products',
        'mod-reviews',
        'mod-posts',
        'mod-post-editor',
        'mod-curation-posts',
        'mod-comments',
        'mod-orders',
        'mod-settings',
        'mod-seo',
        'mod-themes-visual',
        'mod-themes-text',
        'mod-users',
        'mod-audit'
    ]
    for mod_id in expected_modules:
        mod_el = soup.find(id=mod_id)
        assert mod_el is not None, f"Module #{mod_id} missing from admin template!"
    print(f"✓ Verified all {len(expected_modules)} feature modules are cleanly present in DOM.")

    # 6. Verify Curation Inputs for Products & Posts
    for s in range(1, 5):
        assert soup.find('select', attrs={'name': f'home_featured_product_{s}'}) is not None
        assert soup.find('select', attrs={'name': f'home_featured_post_{s}'}) is not None
    print("✓ Verified all 4 Product and 4 Journal curation inputs are wired up.")

    print("\n=== ALL HEADER & SUBTAB TESTS PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    test_header_feature_tabs()
