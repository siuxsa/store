# ZERO//FORM — Architectural Cybersecurity Arsenal & Threat Intelligence Matrix
> **Scandinavian Minimalist & High-Assurance Digital Security Store, Threat Intelligence Journal, Custom Tool Procurement Desk & Telemetry Command Matrix**

---

## 1. Executive Summary & Platform Overview

**ZERO//FORM** is an enterprise-grade digital cybersecurity e-commerce, threat intelligence, and custom tool sourcing platform. Built with Scandinavian architectural minimalism, high-assurance security principles, and strict airgap compliance, it serves security researchers, red teams, penetration testers, and enterprise security operations centers (SOC).

### Core Platform Capabilities
1. **Digital Arsenal Storefront (`/shop`):**
   - **Enterprise Security Licenses & Toolkits:** Commercial binary analysis platforms (*IDA Pro*, *Ghidra Enterprise*, *Binary Ninja*), red team C2 suites (*Cobalt Strike*, *Metasploit Pro*), web application scanners (*Burp Suite Pro*, *Caido*, *Acunetix*), SIEM platforms (*Splunk Enterprise*, *Nessus Pro*), and private threat intelligence feeds.
   - **Downloadable Packages & Cryptographic Proofs:** Offline installation archives, exploit proof-of-concepts, and audit scripts published with reproducible **SHA-256 integrity checksums**.
   - **Instant Telegram Concierge Dispatch:** Frictionless checkout generating a unique order ticket (`#ORD-XXXXX`) dispatched to an encrypted Telegram concierge desk with automated cart manifests.

2. **Custom Sourcing & Procurement Desk (`/request`):**
   - **Unlisted Asset Intake:** Dedicated procurement portal for operators seeking zero-days, enterprise license seats, reverse-engineering suites, hardware implants, or custom C2 development not listed in the public catalog.
   - **Encrypted Intake Pipeline:** Submits operational requirements, budget allocations ($1k to $20k+), urgency tiers (Standard, High, Immediate), and encrypted contact channels, generating procurement tickets (`#REQ-XXXXX`).
   - **Admin Broker Queue:** Complete intake lifecycle management in the admin dashboard (`PENDING`, `SOURCING`, `ALLOCATED`, `DELIVERED`, `CANCELLED`) with internal broker notes and escrow tracking.

3. **Threat Intelligence Journal (`/journal`):**
   - **Vulnerability Disclosures & CVE Advisories:** High-fidelity technical research, binary dissection, and practical exploitation walk-throughs.
   - **Smart Native Ad Engine:** Injects contextual tool shortcodes (`[product:SKU]`), mid-article recommendation cards, sticky sidebar toolboxes, and end-of-post deployment bundles.
   - **Login-Gated & Moderated Reader Comments:** Authenticated operator commenting with an administrative moderation queue (`PENDING`, `APPROVED`, `REJECTED`) keeping discussions professional and verified.

4. **Operator Security Vault (`/vault`):**
   - **Client License Enclave:** Dedicated portal where authenticated operators access activated software licenses, provisioned license keys, copy-to-clipboard tokens, offline download links, and order transaction history.
   - **API Token Provisioning:** Generates secure `X-API-Token` credentials for automated license provisioning and telemetry sync.

5. **Visual Inspect Studio & Multi-Studio Admin Panel (`/admin`):**
   - **Visual Inspect Studio:** Interactive point-and-click live storefront inspector with responsive viewport toggles (Desktop 1280px, Tablet 768px, Mobile 390px).
   - **Text-Based Content Studio:** Comprehensive form-based copy editor for headlines, descriptions, timeline steps, hero banners, and brand manifestos across all routes.
   - **Dedicated SEO & Metadata Studio:** Real-time Google SERP simulator, OpenGraph card previews, per-page meta titles, and Schema.org structured data.
   - **Brand Logo & Browser Favicon Studio:** Live upload and preview support for SVG, PNG, WebP, and ICO assets.
   - **Telemetry & Data Management System:** Decoupled analytics dashboard with independent export (JSON/CSV) and purge controls isolated from core website data.

---

## 2. Visual Identity: "Nordic Minimalist Cyberpunk"

ZERO//FORM operates at the convergence of Scandinavian architectural minimalism and zero-tolerance offensive security engineering.

### Color Palette Tokens
| Swatch | Token | Hex Code | Purpose |
| :--- | :--- | :--- | :--- |
| **Obsidian Core** | `--bg` | `#0c0d0e` | Deep canvas, terminal backdrops, root background |
| **Surface Dark** | `--surface` | `#141618` | Cards, article containers, modal backdrops |
| **Surface Elevated** | `--surface-elevated`| `#1a1c1f` | Hover overlays, active inspection panels |
| **Electric Cyan** | `--accent-cyan` | `#00e5ff` | Primary tactical accent, highlights, live pulses |
| **Emerald Terminal** | `--accent-green`| `#10b981` | Verification badges, activated licenses, success states |
| **Amber Warning** | `--accent-amber`| `#f59e0b` | High urgency badges, escrow indicators |
| **Crimson Alert** | `--accent-red` | `#ef4444` | Critical CVE tags, access denied, purge buttons |
| **Ghost White** | `--text` | `#f0f0f2` | Primary typography, headers, high-contrast labels |
| **Matrix Muted** | `--muted` | `#8c9096` | Technical sublabels, timestamps, secondary metadata |
| **Tactical Border** | `--border` | `rgba(255, 255, 255, 0.1)` | Structural 1px division lines |

---

## 3. System Architecture & Tech Stack

```mermaid
flowchart TD
    subgraph Client ["Client Interface (Storefront, Vault & Studios)"]
        Public["Storefront (/shop, /journal, /about)"]
        RequestDesk["Custom Tool Procurement (/request)"]
        Vault["Operator Vault (/vault)"]
        TelemetryAgent["First-Party Telemetry & Dwell-Time Agent"]
        AdminUI["Command Center (/admin - Visual, Text, SEO, Orders)"]
    end

    subgraph Server ["Python 3 Flask Backend"]
        Routing["Application Router (Blueprint/Route Modules)"]
        AuthModule["RBAC & Session Security (PBKDF2-SHA256)"]
        SmartAds["Smart Native Ad Shortcode Parser"]
        AdminAPI["Admin REST APIs (Theme, SEO, Catalog, Data)"]
        TelemetryIngest["Telemetry Ingestion & Radar Stream"]
        UploadEngine["Media & Asset Upload Engine (.ico, .svg, .webp)"]
    end

    subgraph Storage ["SQLite3 High-Performance Database (cyber.db)"]
        DBCore[("Users, Products, Posts, Comments, Reviews, Orders, Tool Requests")]
        DBSettings[("Dynamic System & Visual Theme Settings")]
        DBAnalytics[("Analytics Pageviews, Events, Dwell Time")]
        DBAudit[("Immutable Security Audit Logs")]
    end

    subgraph External ["External Communication"]
        TelegramDesk["Encrypted Telegram Concierge Desk (@Handle)"]
    end

    Public & RequestDesk & Vault --> TelemetryAgent
    TelemetryAgent -->|"Heartbeat ping (5s) + sendBeacon"| TelemetryIngest
    Public -->|"Cart Checkout"| Routing --> TelegramDesk
    RequestDesk -->|"Submit Sourcing Brief"| Routing --> DBCore
    AdminUI <-->|"Live API Management"| AdminAPI
    Routing <--> Storage
    AdminAPI <--> Storage
```

### Technology Highlights
- **Backend Framework:** Python 3 with Flask, Werkzeug security, and Jinja2 templating.
- **Persistence:** SQLite3 (`cyber.db`) with WAL mode, foreign keys, and atomic transactions.
- **Frontend Layer:** Semantic HTML5, CSS custom properties, vanilla ES6+ JavaScript modules.
- **Security Engineering:** PBKDF2 password hashing, secure session cookies, CSRF protection, sanitized admin gateway (zero credential leaks), and strict input validation.
- **Telemetry System:** Non-blocking first-party beaconing tracking dwell time, scroll percentage, and conversions without third-party tracking scripts.

---

## 4. Complete Module Guide

### Module 1: Digital Arsenal & E-Commerce (`/shop`, `/product/<slug>`)
- **Product Categorization:** Web & AppSec, Offensive & Red Team, SIEM & Blue Team, Reverse Engineering, OSINT & Recon, Downloadable Tools.
- **Technical Integrity Badges:** Product type (`LICENSE_KEY`, `DOWNLOADABLE_TOOL`, `FREE_TOOL`), version strings, supported OS platforms, SHA-256 integrity hashes, and retail savings calculation.
- **Cart & Concierge Checkout:** Drawer cart modal supporting multi-item selection with instant Telegram dispatch pre-formatting order reference tickets.
- **Customer Reviews Studio:** Product reviews with verified deployment badges, star ratings, and custom editorial curation controls.

### Module 2: Custom Tool Sourcing & Procurement (`/request`)
- **Intake Desk:** Public procurement form allowing operators to request unlisted tools, enterprise licenses, zero-days, and custom payloads.
- **Ticket Generation:** Automatically assigns unique reference tickets (`#REQ-XXXXX`).
- **Admin Intake Queue (`ADMIN` → `ORDERS` → `CUSTOM TOOL REQUESTS`):**
  - Live filtering by status (`PENDING`, `SOURCING`, `ALLOCATED`, `DELIVERED`, `CANCELLED`).
  - Modal editor to update status, append internal broker notes, and view contact handles.
  - Permanent deletion and audit logging.
- **Full Studio Editability:** All headlines, form card labels, timeline protocol steps, and concierge cards on `/request` are fully editable via Text, Visual, and SEO studios.

### Module 3: Threat Intelligence Journal & Moderated Comments (`/journal`)
- **Dispatches & CVE Advisories:** Markdown and HTML rendering of security disclosures, severity ratings (`CRITICAL`, `HIGH`, `MEDIUM`, `INFO`), and CVSS scores.
- **Smart Product Ads:** Dynamic shortcodes (`[product:SKU]`), automated midpoint recommendation cards, and sticky sidebar countermeasure toolboxes.
- **Login-Gated Reader Comments:**
  - Unauthenticated visitors see an authentication requirement gate.
  - Authenticated operators submit comments that enter an administrative moderation queue (`PENDING`).
  - Master Admin can approve, reject, or permanently purge comments. Only approved comments render on public dispatches.

### Module 4: Operator Vault (`/vault`)
- **License Provisioning:** Lists all fulfilled orders with unmasked cryptographic license keys, copy-to-clipboard helpers, and direct download links.
- **Transaction History:** Real-time log of previous order tickets with direct concierge link support.
- **API Access:** Generates unique operator tokens for programmatic license synchronization.

### Module 5: Visual Inspect Studio (`ADMIN` → `THEMES` → `VISUAL INSPECT MODE`)
- **Responsive Viewport Canvas:** Emulates Desktop (1280px), Tablet (768px), and Mobile (390px) inside an interactive sandboxed canvas.
- **Route Switcher:** 1-click navigation between `/` (Home), `/about` (Manifesto), `/shop` (Arsenal), `/journal` (Threat Intel), and `/request` (Tool Procurement).
- **Point-and-Click Inspector:** Clicking any element with `data-theme-bind` on the canvas opens an instant quick-edit popup that updates the live DOM in real time.

### Module 6: Text-Based Content Studio (`ADMIN` → `THEMES` → `TEXT-BASED EDIT MODE`)
- **Dedicated Subtabs:**
  - `[01] HOME PAGE CONTENT`: Hero headlines, elevator descriptions, key art banners, category banner strip, and curated product/journal serials.
  - `[02] ABOUT & MANIFESTO`: Tenet blocks, compliance metrics, key art banner, and bottom CTAs.
  - `[03] DIGITAL ARSENAL (SHOP)`: Shop eyebrows, catalog headline, and subtitles.
  - `[04] THREAT JOURNAL`: Disclosure alert badge, headline, and editorial subtitle.
  - `[05] CUSTOM TOOL REQUEST PAGE`: Protocol dispatch banner, form headings, 3-phase timeline protocol steps, and concierge card copy.
  - `[06] GLOBAL SHELL & BRANDING`: Brand callsign, tagline, ticker announcements, logo upload, browser favicon upload, and compliance disclaimer.
  - `[07] TYPOGRAPHY, PALETTE & CSS`: 11 custom color tokens, font family configuration, and custom CSS override injection.

### Module 7: Dedicated SEO & Social Metadata Studio (`ADMIN` → `SEO & METADATA`)
- **Real-Time Simulators:** Live Google Search SERP simulator and OpenGraph social share card preview.
- **Per-Page Granular SEO:** Meta titles, meta descriptions, search keywords, and social OG images for Global Defaults, Home (`/`), About (`/about`), Shop (`/shop`), Threat Journal (`/journal`), and Custom Tool Request (`/request`).
- **Live Character Counters:** Real-time validation badges ensuring optimal title (< 60 chars) and description (< 160 chars) length.

### Module 8: Favicon & Brand Logo Management
- **Site Brand Logo:** Upload vector SVG, PNG, or WebP logos with live preview. Replaces text brand across header, mobile slide-out menu, and footer.
- **Browser Tab Favicon:** Upload `.ico`, `.png`, `.svg`, or `.webp` files with live browser tab mockup. Automatically updates `<link rel="icon">`, `<link rel="apple-touch-icon">`, and the `/favicon.ico` redirection endpoint.

### Module 9: Telemetry & Data Management System (`ADMIN` → `SETTINGS`)
- **Decoupled Architecture:** Telemetry tracking is completely decoupled from core website data.
- **Real-Time Readout:** Live pageviews, tracking events, unique visitor entities, and physical database file footprint.
- **Safe Export & Purge Tools:** Export tracking records to JSON or CSV. Purge telemetry records or vacuum the database without ever touching products, orders, user accounts, comments, or reviews.

---

## 5. Database Schema Reference

```mermaid
erDiagram
    USERS ||--o{ ORDERS : places
    USERS ||--o{ POST_COMMENTS : writes
    USERS ||--o{ TOOL_REQUESTS : submits
    PRODUCTS ||--o{ REVIEWS : receives
    POSTS ||--o{ POST_COMMENTS : receives

    USERS {
        int id PK
        string username UK
        string email UK
        string password_hash
        string role "ADMIN | OPERATOR"
        string telegram_handle
        string api_token UK
        boolean is_active
        datetime created_at
    }

    SETTINGS {
        string key PK
        string value
    }

    PRODUCTS {
        int id PK
        string sku UK
        string name
        string slug UK
        string category
        string product_type
        float price
        float retail_price
        string version
        string license_duration
        string platform
        string short_desc
        text specs_json
        string sha256_hash
        string download_url
        string badge_text
        boolean featured
        int views_count
        datetime created_at
    }

    POSTS {
        int id PK
        string title
        string slug UK
        string category
        string severity
        string cve_id
        string cvss_score
        string author
        string read_time
        string summary
        text content
        string related_skus
        string ad_mode
        string ad_custom_pitch
        boolean featured
        int views
        datetime published_at
    }

    POST_COMMENTS {
        int id PK
        int post_id FK
        int user_id FK
        string author_name
        string author_role
        text content
        string status "PENDING | APPROVED | REJECTED"
        string ip_address
        datetime created_at
    }

    REVIEWS {
        int id PK
        int product_id FK
        string product_sku
        string author_name
        string author_role
        string author_org
        int rating
        string title
        text content
        string verified_badge
        boolean featured_manifesto
        datetime created_at
    }

    TOOL_REQUESTS {
        int id PK
        string request_id UK
        int user_id FK
        string tool_name
        string category
        string contact_telegram
        string contact_email
        string preferred_contact
        string urgency
        string budget_range
        text technical_specs
        string status "PENDING | SOURCING | ALLOCATED | DELIVERED | CANCELLED"
        text admin_notes
        string ip_address
        datetime created_at
        datetime updated_at
    }

    ORDERS {
        int id PK
        string order_number UK
        string buyer_telegram
        float total_amount
        string status
        text items_json
        text fulfilled_license_info
        datetime created_at
    }

    ANALYTICS_PAGEVIEWS {
        int id PK
        string visit_token UK
        string visitor_id
        string session_id
        string page_type
        string target_slug
        string target_title
        int duration_seconds
        int max_scroll_pct
        string referrer
        string device_type
        string os_name
        datetime created_at
        datetime last_ping_at
    }

    ANALYTICS_EVENTS {
        int id PK
        string visitor_id
        string session_id
        string event_type
        string source_page
        string target_sku
        string meta_info
        datetime created_at
    }

    AUDIT_LOGS {
        int id PK
        int admin_id
        string admin_username
        string action
        string details
        string ip_address
        datetime created_at
    }
```

---

## 6. Directory Structure

```text
/home/siuxsa/cyber/
├── README.md                          # Full Architecture, Engineering & Operational Blueprint
├── app.py                             # Core Flask Application & Bootstrap Engine
├── database.py                        # SQLite3 Schema Migrations & Initial Seed Data
├── cyber.db                           # Primary SQLite3 Database
├── requirements.txt                   # Production Python Dependencies
├── wsgi.py                            # Production WSGI Server Entrypoint
├── core/
│   ├── config.py                      # System Configuration, Allowed Extensions, Default Schema
│   ├── helpers.py                     # Markdown Processor, Smart Ads Engine, Audit Logger
│   └── security.py                    # Session Management, Authentication Guards, RBAC
├── routes/
│   ├── __init__.py                    # Central Route Registration Gateway
│   ├── frontend.py                    # Public Storefront, Catalog, Journal, Custom Request Desk
│   ├── auth.py                        # Operator Vault Auth, Registration, Sanitized Admin Login
│   ├── orders.py                      # Checkout API, Cart Processing, Telemetry Ingestion
│   └── admin/
│       ├── panel.py                   # Master Admin Dashboard Controller
│       ├── products.py                # Arsenal Catalog Management APIs
│       ├── posts.py                   # Threat Intelligence & Smart Ad Editor APIs
│       ├── comments.py                # Reader Comments Moderation APIs
│       ├── reviews.py                 # Customer Reviews CRUD & Home Curation APIs
│       ├── tool_requests.py           # Custom Tool Sourcing Intake Management APIs
│       ├── settings.py                # System Settings, Data Management & Telemetry Purge APIs
│       ├── theme.py                   # Theme Colors, Media Uploads, Home Curation APIs
│       ├── users.py                   # Operator Account Management APIs
│       └── audit.py                   # Immutable Audit Log Viewer APIs
├── static/
│   ├── css/
│   │   ├── style.css                  # Nordic Cyberpunk Core Design System
│   │   ├── responsive.css             # Viewport Layouts & Media Queries
│   │   └── admin.css                  # Modular Admin Command Center Styles
│   ├── js/
│   │   ├── main.js                    # Storefront Interactivity, Search & Mobile Nav
│   │   ├── cart.js                    # Slide-Out Cart Drawer & Telegram Dispatch
│   │   ├── telemetry.js               # First-Party Dwell Time & Scroll Beaconing
│   │   └── admin/
│   │       ├── admin_core.js          # Tab Switching, Toasts & Global Helpers
│   │       ├── admin_analytics.js     # Live Telemetry Charts & Visitor Radar Stream
│   │       ├── admin_orders.js        # Order Fulfillment & Key Provisioning
│   │       ├── admin_tool_requests.js # Custom Tool Sourcing Intake Queue Controller
│   │       ├── admin_products.js      # Product Catalog Studio
│   │       ├── admin_posts.js         # Journal Editor, Markdown Preview & Smart Ads
│   │       ├── admin_comments.js      # Comment Moderation Controller
│   │       ├── admin_reviews.js       # Verified Reviews CRUD
│   │       ├── admin_curation.js      # Homepage Curated Product & Journal Selector
│   │       ├── admin_settings.js      # Branding, Logo/Favicon Upload, Telemetry Purge
│   │       ├── admin_themes.js        # Visual Inspect Studio & Text Content Studio
│   │       └── admin_users.js         # Account & Role Management
│   └── uploads/                       # Verified Uploaded Media, Logos & Favicons
├── templates/
│   ├── base.html                      # Global Storefront Shell, Navigation, Header, Footer
│   ├── index.html                     # Minimalist Hero, Curated Serials, Category Strip
│   ├── shop.html                      # Digital Arsenal Catalog with Category Filters
│   ├── product_detail.html            # Spec Sheet, SHA-256 Proof, Telegram Checkout
│   ├── blog.html                      # Threat Intelligence Wire
│   ├── post_detail.html               # Dispatch Reader, Smart Ads, Login-Gated Comments
│   ├── request_tool.html              # Custom Tool Sourcing & Procurement Desk
│   ├── vault.html                     # Operator Vault, Unlocked Licenses, API Tokens
│   ├── login.html                     # Customer Authentication Page
│   ├── register.html                  # Customer Registration Page
│   ├── admin_login.html               # Sanitized Admin Login Gateway (Zero Leaks)
│   ├── admin.html                     # Master Admin Command Matrix
│   └── admin/
│       ├── modals/                    # Modals for Products, Posts, Reviews, Requests, Themes
│       └── modules/                   # Submodules for Analytics, Catalog, Journal, Orders, SEO, etc.
└── scratch/                           # Automated Verification & Integration Test Suites
```

---

## 7. Quickstart & Deployment Guide

### Prerequisites
- Python 3.10+
- SQLite3

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd cyber
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize Database:**
   The SQLite database (`cyber.db`) is automatically initialized and seeded on first run with default catalog items, dispatches, settings, and an initial master administrator account.

4. **Launch Application:**

   **Development Mode:**
   ```bash
   python3 app.py
   ```
   Server will start on `http://127.0.0.1:5000`.

   **Production WSGI (Gunicorn - Linux):**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
   ```

   **Production WSGI (Waitress - Cross-Platform):**
   ```bash
   python3 wsgi.py
   ```

---

## 8. Verification & Test Suites

The codebase includes an extensive suite of automated integration and security regression tests located in `scratch/`:

```bash
# 1. Admin Login Security & Zero-Credential Leak Verification
python3 scratch/test_admin_login_security.py

# 2. Browser Tab Favicon & Brand Logo Update Suite
python3 scratch/test_favicon_and_logo.py

# 3. Custom Tool Procurement Pipeline & Order Lookup Transition Suite
python3 scratch/test_tool_requests.py

# 4. Request Page Multi-Studio Admin Editability Suite
python3 scratch/test_request_page_admin_editing.py

# 5. Full Comprehensive Feature Verification Suite (Comments, Themes, Catalog, Reviews, Checkout)
python3 scratch/test_comprehensive_manual_features.py
```

All suites execute cleanly with a 100% pass rate.

---

## 9. Security & Compliance Declarations

- **Zero Credential Exposure:** Login gateways load with clean, unpopulated inputs, zero client-side credential scripts, and strict server-side authentication validation.
- **Airgap & Offline Execution:** Digital tool distributions include verified cryptographic SHA-256 hashes for operational reproduction on isolated, non-beaconing networks.
- **Strict Data Decoupling:** Visitor telemetry and tracking records are physically and logically segregated from customer accounts, orders, reviews, and editorial content.
- **Audit Provenance:** Administrative actions (theme updates, product modifications, status transitions, purges) are permanently recorded in the immutable `audit_logs` table.
