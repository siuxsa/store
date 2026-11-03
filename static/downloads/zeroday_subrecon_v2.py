#!/usr/bin/env python3
"""
ZERODAY // ARSENAL — Subdomain & Certificate Transparency Recon Scanner (v2.4)
Community Free Edition — For Authorized Security Auditing Only
"""
import socket
import sys
import urllib.request
import json

def scan_crtsh(domain: str):
    print(f"[*] Querying Certificate Transparency logs for: {domain}")
    url = f"https://crt.sh/?q=%.{domain}&output=json"
    req = urllib.request.Request(url, headers={"User-Agent": "ZeroDay-Recon/2.4"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            subs = sorted({entry.get("name_value", "").lower() for entry in data})
            for sub in subs:
                print(f"[+] Discovered: {sub}")
            print(f"[✓] Total unique records: {len(subs)}")
    except Exception as exc:
        print(f"[!] Error querying crt.sh: {exc}")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "example.com"
    scan_crtsh(target)
