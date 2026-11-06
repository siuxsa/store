import os

DATABASE_NAME = "cyber.db"
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "svg", "ico"}
BAN_COOKIE_NAME = "zd_sanction_token"

DEFAULT_ROBOTS_TXT = """User-agent: *
Allow: /
Allow: /shop
Allow: /arsenal
Allow: /product/
Allow: /journal
Allow: /intel
Allow: /about
Allow: /request
Disallow: /admin
Disallow: /vault
Disallow: /api/

Sitemap: {{SITE_URL}}/sitemap.xml"""

DEFAULT_SITE_SETTINGS = {
    "site_name": "ZERO//FORM",
    "site_tagline": "OFFENSIVE & DEFENSIVE SECURITY TOOLS, EXPLOIT RESEARCH & LICENSES",
    "site_logo": "",
    "site_favicon": "",
    "ticker_text": "VERIFIED SECURITY TOOLS, PENTESTING SUITES & CVE RESEARCH — INSTANT LICENSE DELIVERY VIA TELEGRAM & VAULT",
    "ticker_subtext": "UNLOCKED COMMERCIAL BUILDS · 100% OFFLINE & AIRGAP READY",
    "telegram_user": "ZeroFormConcierge",
    "telegram_channel": "https://t.me/ZeroFormSystems",
    "telegram_msg_prefix": "Hello! I would like to purchase the following security tool license(s):",
    "footer_disclaimer": "ALL SECURITY TOOLS, EXPLOIT MODULES, AND CVE WRITEUPS ARE PROVIDED STRICTLY FOR AUTHORIZED PENETRATION TESTING, RED TEAM OPERATIONS, AND DEFENSIVE SECURITY RESEARCH.",
    "footer_desc": "Offensive & defensive cybersecurity tools, reverse engineering suites, SIEM platforms, and technical CVE writeups for security researchers and red teams.",
    "footer_motto": "OFFENSIVE & DEFENSIVE CYBERSECURITY TOOLS.\nUNLOCKED MODULES · OFFLINE LAB READY",
    "footer_col1_title": "SECURITY TOOLS",
    "footer_col2_title": "PLATFORM",
    "footer_col3_title": "TELEGRAM DESK",
    "footer_telegram_desc": "Instant license provisioning, custom tool sourcing, and technical support via Telegram.",
    "footer_badge": "UNLOCKED MODULES · AIRGAP READY · TELEGRAM DELIVERY",

    # Global SEO & Metadata
    "seo_meta_title": "ZERO//FORM — Cybersecurity Tools, Pentesting Suites & Threat Research",
    "seo_meta_description": "Verified offensive & defensive security tools, reverse engineering frameworks, SIEM licenses, and technical CVE vulnerability research.",
    "seo_meta_keywords": "cybersecurity tools, penetration testing, red team tools, reverse engineering, CVE research, exploit writeups, SIEM, AppSec",
    "seo_og_image": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=1200&q=85",

    # Dedicated Page SEO Overrides (Configurable per page with automatic fallback)
    "seo_home_title": "",
    "seo_home_desc": "",
    "seo_home_keywords": "",
    "seo_home_image": "",

    "seo_about_title": "",
    "seo_about_desc": "",
    "seo_about_keywords": "",
    "seo_about_image": "",

    "seo_shop_title": "",
    "seo_shop_desc": "",
    "seo_shop_keywords": "",
    "seo_shop_image": "",

    "seo_journal_title": "",
    "seo_journal_desc": "",
    "seo_journal_keywords": "",
    "seo_journal_image": "",

    # Request Page SEO
    "seo_request_title": "",
    "seo_request_desc": "",
    "seo_request_keywords": "",
    "seo_request_image": "",

    # Crawler Indexing: robots.txt & sitemap.xml
    "seo_site_url": "",
    "robots_txt_content": DEFAULT_ROBOTS_TXT,
    "sitemap_xml_content": "",
    "sitemap_last_generated": "",
    "sitemap_url_count": "0",

    # Navigation Labels
    "nav_shop_label": "SECURITY TOOLS",
    "nav_blog_label": "THREAT RESEARCH",
    "nav_orders_label": "REQUEST TOOL",
    "nav_about_label": "ABOUT",

    # Custom 404 Error Page Settings (Fully Editable from Admin Panel)
    "error_404_title": "404",
    "error_404_badge": "HTTP 404 · ENDPOINT NOT FOUND",
    "error_404_headline": "RESOURCE NOT FOUND.",
    "error_404_message": "The security tool, license package, or CVE research writeup you requested has been moved, renamed, or is no longer available at this URL.",
    "error_404_cta_text": "← BACK TO HOME",
    "error_404_cta_url": "/",
    "error_404_show_search": "1",

    # Home Page
    "hero_image": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=2200&q=90",
    "hero_badge": "// VERIFIED SECURITY TOOLS & CVE RESEARCH",
    "hero_title": "OFFENSIVE &\nDEFENSIVE\nSECURITY TOOLS.",
    "hero_subtitle": "Enterprise penetration testing suites, reverse engineering frameworks, SIEM platforms, and technical CVE writeups—fully unlocked and ready for local or offline security labs.",
    "hero_cta_primary": "BROWSE SECURITY TOOLS →",
    "hero_cta_primary_url": "/shop",
    "hero_cta_secondary": "THREAT RESEARCH →",
    "hero_cta_secondary_url": "/journal",

    "manifesto_eyebrow": "// SECURITY STANDARDS",
    "manifesto_sublabel": "AIRGAP & OFFLINE READY · UNLOCKED MODULES · ZERO TELEMETRY",
    "manifesto_title": "BUILT FOR PENTESTERS\n& SECURITY TEAMS.",
    "manifesto_lead": "Every security tool and enterprise license in our catalog is pre-tested in isolated lab environments, includes full module access without trial restrictions, and runs 100% offline with zero cloud telemetry.",

    "featured_eyebrow": "// SECURITY CATALOG",
    "featured_title": "FEATURED SECURITY TOOLS",
    "featured_cta": "VIEW ALL SECURITY TOOLS",

    # Home Page Category Navigation One-Line Banner Text
    "category_strip_text": "ALL SECURITY TOOLS // WEB & APPSEC // OFFENSIVE & RED TEAM // SIEM & BLUE TEAM // REVERSE ENGINEERING // OSINT & RECON",

    # Homepage Curated 4 Products & 4 Journals (Serials 1 - 4)
    "home_featured_product_1": "22",
    "home_featured_product_2": "23",
    "home_featured_product_3": "24",
    "home_featured_product_4": "25",
    "home_featured_post_1": "9",
    "home_featured_post_2": "10",
    "home_featured_post_3": "11",
    "home_featured_post_4": "12",

    # Home Page Category Navigation Chips (Fallback)
    "cat_chip_all": "ALL SECURITY TOOLS",
    "cat_chip_web": "WEB & APPSEC",
    "cat_chip_offensive": "OFFENSIVE & RED TEAM",
    "cat_chip_siem": "SIEM & BLUE TEAM",
    "cat_chip_re": "REVERSE ENGINEERING",
    "cat_chip_osint": "OSINT & RECON",

    "showcase_eyebrow": "// LAB & RED TEAM WORKFLOW",
    "showcase_title": "OFFLINE-READY BUILDS.\nNO CLOUD TELEMETRY.",
    "showcase_desc": "All pentesting suites, decompilers, and security tools operate natively in isolated VMs, local labs, and airgapped networks without mandatory cloud logins.",
    "showcase_stat1_val": "100%",
    "showcase_stat1_label": "AIRGAP / OFFLINE READY",
    "showcase_stat2_val": "< 5 MIN",
    "showcase_stat2_label": "TELEGRAM PROVISIONING",
    "showcase_stat3_val": "MULTI-OS",
    "showcase_stat3_label": "LINUX · WIN · MACOS",

    "journal_section_eyebrow": "// VULNERABILITY RESEARCH & CVE WRITEUPS",
    "journal_section_title": "THREAT RESEARCH & ADVISORIES",
    "journal_section_cta": "VIEW ALL RESEARCH",

    # About Page
    "about_eyebrow": "// ABOUT ZERO//FORM",
    "about_title": "ENGINEERED FOR RED TEAMS\n& SECURITY RESEARCHERS.",
    "about_desc": "We provide verified offensive & defensive security tools, reverse engineering licenses, and technical CVE writeups built for real-world security assessments.",
    "about_banner_image": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=1800&q=85",
    "about_banner_badge": "SECURITY INFRASTRUCTURE",
    "about_banner_title": "STANDALONE SECURITY TOOLS FOR ISOLATED LABS & RED TEAM OPS.",
    "about_banner_meta": "EST. 2026 // CYBERSECURITY CATALOG & RESEARCH",
    "about_tenet1_eyebrow": "01 // ZERO CLOUD DEPENDENCY",
    "about_tenet1_title": "100% OFFLINE & AIRGAP READY.",
    "about_tenet1_desc": "Security assessments and lab analysis require strict operational privacy. Our tools run locally without cloud phone-home callbacks or forced SaaS logins.",
    "about_tenet1_tag": "ZERO TELEMETRY · LOCAL EXECUTION",
    "about_tenet2_eyebrow": "02 // CROSS-PLATFORM LAB SUPPORT",
    "about_tenet2_title": "MULTI-OS & VM COMPATIBLE.",
    "about_tenet2_desc": "Our security packages include native builds for Kali Linux, Ubuntu, Windows, and macOS, pre-configured for VMware, VirtualBox, Proxmox, and local security workstations.",
    "about_tenet2_tag": "LINUX · WINDOWS · MACOS · VM READY",
    "about_tenet3_eyebrow": "03 // DIRECT PROVISIONING",
    "about_tenet3_title": "TELEGRAM LICENSE DELIVERY.",
    "about_tenet3_desc": "Orders are fulfilled directly through our Telegram desk and unlocked automatically in your account Vault with download links and setup documentation.",
    "about_tenet3_tag": "INSTANT VAULT & TELEGRAM ACCESS",

    "about_metrics_eyebrow": "// SECURITY & DELIVERY METRICS",
    "about_metric1_val": "100%",
    "about_metric1_title": "AIRGAP & VM COMPATIBLE",
    "about_metric1_desc": "Full offline execution in local VMs, Kali/Linux testbeds, and isolated lab networks.",
    "about_metric2_val": "< 5 MIN",
    "about_metric2_title": "LICENSE PROVISIONING",
    "about_metric2_desc": "Fast order confirmation via Telegram with permanent download links in your Vault.",
    "about_metric3_val": "MULTI-OS",
    "about_metric3_title": "CROSS-PLATFORM BUILDS",
    "about_metric3_desc": "Native packages for Kali Linux, Windows, and macOS security workstations.",
    "about_metric4_val": "PERPETUAL",
    "about_metric4_title": "STANDALONE LICENSES",
    "about_metric4_desc": "Unlocked commercial builds without trial limits, feature locks, or cloud throttling.",

    "about_cta_eyebrow": "// EXPLORE THE CATALOG",
    "about_cta_title": "READY TO EQUIP YOUR SECURITY LAB?",
    "about_cta_desc": "Browse enterprise pentesting suites, reverse engineering decompilers, SIEM platforms, and CVE research writeups.",
    "about_cta_btn1": "BROWSE SECURITY TOOLS →",
    "about_cta_btn2": "THREAT RESEARCH →",

    # Catalog & Journal Pages
    "shop_eyebrow": "// SECURITY TOOLS & LICENSES",
    "shop_title": "SECURITY TOOLS.",
    "shop_subtitle": "Verified penetration testing suites, reverse engineering tools, vulnerability scanners, and SIEM licenses.",
    "products_per_page": "8",
    "journal_eyebrow": "// VULNERABILITY RESEARCH & CVE ADVISORIES",
    "journal_title": "THREAT RESEARCH.",
    "journal_subtitle": "Technical vulnerability writeups, CVE proof-of-concept analysis, exploit research, and defensive mitigation guides.",
    "journal_per_page": "4",

    # Custom Tool Sourcing / Request Page
    "request_breadcrumb": "REQUEST CUSTOM TOOL",
    "request_eyebrow": "// CUSTOM TOOL & EXPLOIT SOURCING",
    "request_title": "REQUEST UNLISTED TOOLS.",
    "request_desc": "Need a specific pentesting suite, reverse-engineering license, exploit module, or security tool not listed in our catalog? Submit your technical requirements below.",
    "request_form_eyebrow": "// TOOL & LICENSE SPECIFICATIONS",
    "request_form_title": "SUBMIT CUSTOM TOOL REQUEST",
    "request_submit_btn": "SUBMIT TOOL REQUEST →",
    "request_security_badge": "ENCRYPTED SUBMISSION · FAST TELEGRAM RESPONSE",
    "request_timeline_eyebrow": "// SOURCING WORKFLOW",
    "request_step1_title": "REQUIREMENTS REVIEW",
    "request_step1_desc": "Our team reviews your target OS, version requirements, and module specifications within a few hours.",
    "request_step2_title": "LAB TESTING & VERIFICATION",
    "request_step2_desc": "We source and test the requested security tool in an isolated lab to verify offline stability and full module functionality.",
    "request_step3_title": "VAULT & TELEGRAM DELIVERY",
    "request_step3_desc": "Download links, setup documentation, and license keys are delivered via Telegram and unlocked in your Vault.",
    "request_concierge_eyebrow": "// DIRECT SECURITY DESK",
    "request_concierge_title": "TALK TO OUR TEAM ON TELEGRAM",
    "request_concierge_desc": "For urgent red team tool requests, custom exploit research, or bulk license inquiries, message our desk directly on Telegram:",
    "request_concierge_btn": "CONTACT ON TELEGRAM →",

    # Security Defense: Rate Limiting & Customizable Admin Gateway Path
    "rate_limit_enabled": "1",
    "rate_limit_login_max": "8",
    "rate_limit_page_max": "120",
    "rate_limit_api_max": "60",
    "rate_limit_block_seconds": "60",
    "admin_custom_path": "admin"
}
