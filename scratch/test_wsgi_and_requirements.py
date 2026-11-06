import os
import sys
import subprocess

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

def test_wsgi_and_requirements():
    print("=== TESTING WSGI PRODUCTION RUNNER & REQUIREMENTS ===")

    # 1. Test requirements.txt dependency resolution
    req_file = os.path.join(PROJECT_DIR, "requirements.txt")
    assert os.path.exists(req_file), "requirements.txt not found!"
    print(f"✓ Found requirements.txt at {req_file}.")

    # Test pip install dry-run
    pip_res = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--dry-run", "-r", req_file, "--break-system-packages"],
        capture_output=True,
        text=True
    )
    assert pip_res.returncode == 0, f"pip dry-run failed: {pip_res.stderr}"
    print("✓ All requirements.txt packages and version constraints resolve 100% cleanly.")

    # 2. Test importing wsgi module
    import wsgi
    assert hasattr(wsgi, "app"), "wsgi module must expose 'app'"
    assert hasattr(wsgi, "application"), "wsgi module must expose 'application'"
    assert hasattr(wsgi, "create_app"), "wsgi module must expose 'create_app' factory"
    assert callable(wsgi.create_app), "'create_app' must be callable"
    assert wsgi.create_app() is wsgi.app, "'create_app()' must return the Flask app"
    print("✓ WSGI callables verified: wsgi.app, wsgi.application, and wsgi.create_app().")

    # 3. Test ProxyFix middleware attachment
    from werkzeug.middleware.proxy_fix import ProxyFix
    assert isinstance(wsgi.app.wsgi_app, ProxyFix), "ProxyFix middleware should wrap wsgi_app for production reverse proxies"
    print("✓ Production ProxyFix middleware correctly active on WSGI pipeline.")

    # 4. Test Gunicorn configuration check on both callables
    gun_app = subprocess.run(["gunicorn", "--check-config", "wsgi:app"], cwd=PROJECT_DIR, capture_output=True, text=True)
    assert gun_app.returncode == 0, f"gunicorn wsgi:app check failed: {gun_app.stderr}"

    gun_appl = subprocess.run(["gunicorn", "--check-config", "wsgi:application"], cwd=PROJECT_DIR, capture_output=True, text=True)
    assert gun_appl.returncode == 0, f"gunicorn wsgi:application check failed: {gun_appl.stderr}"
    print("✓ Gunicorn syntax and configuration check verified for both wsgi:app and wsgi:application.")

    # 5. Test direct WSGI Client dispatch
    client = wsgi.app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200, f"Test client GET / returned {resp.status_code}"
    print("✓ WSGI application dispatches HTTP 200 OK via test client.")

    # Test request with reverse proxy headers
    resp_proxied = client.get("/", headers={
        "X-Forwarded-For": "203.0.113.195",
        "X-Forwarded-Proto": "https",
        "X-Forwarded-Host": "matrix.security"
    })
    assert resp_proxied.status_code == 200
    print("✓ WSGI application handles proxied headers (HTTPS / X-Forwarded-For) without error.")

    print("\n=== ALL WSGI & REQUIREMENTS TESTS PASSED 100%! ===")

if __name__ == "__main__":
    test_wsgi_and_requirements()
