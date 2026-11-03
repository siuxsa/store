import requests
import json
import re

session = requests.Session()
login_res = session.post("http://127.0.0.1:5000/admin/login", data={"identifier": "admin", "password": "Admin@2026"})
assert login_res.status_code == 200

admin_res = session.get("http://127.0.0.1:5000/admin")
assert admin_res.status_code == 200
html = admin_res.text

# Extract window.INITIAL_ANALYTICS_DATA
match = re.search(r'window\.INITIAL_ANALYTICS_DATA\s*=\s*(\{.*?\});\s*\n', html, re.DOTALL)
assert match is not None, "INITIAL_ANALYTICS_DATA not found in HTML!"
data_str = match.group(1)
data = json.loads(data_str)
print("✓ INITIAL_ANALYTICS_DATA parsed successfully:", list(data.keys()))
print("  kpis:", data.get('kpis'))
print("  products count:", len(data.get('products', [])))
print("  blogs count:", len(data.get('blogs', [])))
print("  recent_stream count:", len(data.get('recent_stream', [])))

# Extract window.ORIGINAL_THEME_SETTINGS
settings_match = re.search(r'window\.ORIGINAL_THEME_SETTINGS\s*=\s*(\{.*?\});\s*\n', html, re.DOTALL)
assert settings_match is not None, "ORIGINAL_THEME_SETTINGS not found in HTML!"
settings = json.loads(settings_match.group(1))
print("✓ ORIGINAL_THEME_SETTINGS parsed successfully, keys:", len(settings.keys()))

print("\nAll injected server data is 100% valid JSON!")
