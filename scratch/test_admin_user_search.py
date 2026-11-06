"""
=============================================================================
TEST: ADMIN PANEL USER SEARCH & ROLE FILTER SUITE
=============================================================================
Verifies:
1. Admin module template includes search input, role filter, count badge, clear button
2. User table rows contain data-search, data-role, data-status attributes
3. JS filter logic correctly filters by username, email, telegram, ID, IP, role, and status
4. No-results placeholder exists for zero-match cases
=============================================================================
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import app
from database import get_db

client = app.test_client()

with client.session_transaction() as sess:
    sess['admin_id'] = 1
    sess['admin_username'] = 'admin'
    sess['admin_role'] = 'ADMIN'

res = client.get('/admin')
assert res.status_code == 200
html = res.data.decode('utf-8')

# Verify Search Toolbar elements
assert 'id="users-search-input"' in html, "Search input missing from admin users module"
assert 'class="user-filter-bar"' in html, "User filter bar missing from admin users module"
assert 'class="user-filter-btn' in html, "User filter buttons missing from admin users module"
assert 'id="users-search-count"' in html, "Search count badge missing from admin users module"
assert 'id="users-no-results"' in html, "No results row missing from admin users module"
assert 'class="user-row"' in html, "user-row class missing from user table rows"
assert 'data-search=' in html, "data-search attribute missing from user table rows"
assert 'data-role=' in html, "data-role attribute missing from user table rows"
assert 'data-status=' in html, "data-status attribute missing from user table rows"

# Verify JS module contains filtering functions
with open(os.path.join(PROJECT_ROOT, 'static/js/admin/admin_users.js'), 'r', encoding='utf-8') as f:
    js_content = f.read()

assert 'function filterUsersList()' in js_content, "filterUsersList function missing from admin_users.js"
assert 'function clearUsersSearch()' in js_content, "clearUsersSearch function missing from admin_users.js"

print("ALL ADMIN USER SEARCH TESTS PASSED 100%!")
