import os

DATABASE_NAME = "cyber.db"
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "svg"}
BAN_COOKIE_NAME = "zd_sanction_token"

DEFAULT_SITE_SETTINGS = {
    "site_name": "ZERO//FORM",
    "site_tagline": "ARCHITECTURAL SECURITY SYSTEMS & VERIFIED ENTERPRISE LICENSES",
    "ticker_text": "SS26 SECURITY ARCHITECTURE // SYSTEMS FOR THE UNPREDICTABLE — INSTANT DISPATCH VIA TELEGRAM CONCIERGE",
    "ticker_subtext": "INSTANT TELEGRAM DISPATCH ON ALL LICENSES",
    "telegram_user": "ZeroFormConcierge",
    "telegram_channel": "https://t.me/ZeroFormSystems",
    "telegram_msg_prefix": "Hello ZERO//FORM Concierge! I want to order the following security systems:",
    "footer_disclaimer": "ALL SOFTWARE SYSTEMS AND AUDIT PACKAGES ARE DISTRIBUTED FOR AUTHORIZED DEFENSIVE AUDITING, COMPLIANCE AND RESEARCH.",
    "footer_desc": "Engineered for security researchers, penetration testers, and purple team operators.",
    "footer_motto": "SYSTEMS FOR THE UNPREDICTABLE.\nEDITION 01.26 // SCANDINAVIAN MINIMALISM",
    "footer_col1_title": "SECURITY ARSENAL",
    "footer_col2_title": "THREAT INTELLIGENCE",
    "footer_col3_title": "CONCIERGE & TELEGRAM",
    "footer_telegram_desc": "Instant license provisioning and BTC/USDT order verification via our encrypted concierge desk.",
    "footer_badge": "SHA256 VERIFIED · AIRGAP SAFE",

    # Global SEO & Metadata
    "seo_meta_title": "ZERO//FORM — Architectural Security Systems & Verified Enterprise Licenses",
    "seo_meta_description": "Commercial security auditing suites, binary analysis frameworks and verified threat intelligence. Engineered for authorized penetration testers, reverse engineers, and enterprise security operations.",
    "seo_meta_keywords": "cybersecurity, reverse engineering, exploit development, penetration testing, airgap security, threat intelligence, zero day, SIEM, red team, binary analysis",
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

    # Navigation Labels
    "nav_shop_label": "ARSENAL",
    "nav_blog_label": "THREAT INTEL",
    "nav_orders_label": "ORDER LOOKUP",
    "nav_about_label": "ABOUT",

    # Home Page
    "hero_image": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=2200&q=90",
    "hero_badge": "SS26 // SYSTEM PROTOTYPE",
    "hero_title": "SYSTEMS\nFOR THE\nUNPREDICTABLE.",
    "hero_subtitle": "Commercial security auditing suites, binary analysis frameworks and verified threat intelligence. Engineered for authorized penetration testers, reverse engineers, and enterprise security operations.",
    "hero_cta_primary": "EXPLORE ARSENAL →",
    "hero_cta_primary_url": "/shop",
    "hero_cta_secondary": "THREAT JOURNAL →",
    "hero_cta_secondary_url": "/journal",

    "manifesto_eyebrow": "// SECURITY MANIFESTO",
    "manifesto_sublabel": "EST. 2026 // SCANDINAVIAN MINIMALISM",
    "manifesto_title": "ENGINEERED FOR\nTHE ELEMENTS.",
    "manifesto_lead": "Every software package and audit license is cryptographically verified, packaged with instant activation manifests, and provisioned without retail subscription overhead. Built for high-stakes operational environments.",

    "featured_eyebrow": "// CURATED ARSENAL",
    "featured_title": "FEATURED SYSTEMS",
    "featured_cta": "VIEW ALL SYSTEMS",

    # Home Page Category Navigation One-Line Banner Text
    "category_strip_text": "ALL SYSTEMS // WEB & APPSEC // OFFENSIVE & RED TEAM // SIEM & BLUE TEAM // REVERSE ENGINEERING // OSINT & RECON",

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
    "cat_chip_all": "ALL SYSTEMS",
    "cat_chip_web": "WEB & APPSEC",
    "cat_chip_offensive": "OFFENSIVE & RED TEAM",
    "cat_chip_siem": "SIEM & BLUE TEAM",
    "cat_chip_re": "REVERSE ENGINEERING",
    "cat_chip_osint": "OSINT & RECON",

    "showcase_eyebrow": "// OPERATIONAL INTEGRITY",
    "showcase_title": "UNCOMPROMISED PRECISION.\nZERO SUBSCRIPTION LOCK-IN.",
    "showcase_desc": "Every binary and license is verified using SHA-256 cryptographic hashes against vendor release manifests. Provisioned for airgapped environments with full offline execution capability.",
    "showcase_stat1_val": "100%",
    "showcase_stat1_label": "AIRGAP SAFE",
    "showcase_stat2_val": "< 5 MIN",
    "showcase_stat2_label": "TELEGRAM DISPATCH",
    "showcase_stat3_val": "SHA-256",
    "showcase_stat3_label": "CRYPTO VERIFIED",

    "journal_section_eyebrow": "// RESEARCH & CVE DISCLOSURES",
    "journal_section_title": "THREAT JOURNAL",
    "journal_section_cta": "VIEW ALL RESEARCH",

    # About Page
    "about_eyebrow": "// BRAND ARCHITECTURE & SYSTEM MANIFESTO",
    "about_title": "SYSTEMS FOR THE\nUNPREDICTABLE.",
    "about_desc": "NORTH//FORM / ZERO//FORM operates at the convergence of Scandinavian architectural minimalism and zero-tolerance offensive security engineering.",
    "about_banner_image": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=1800&q=85",
    "about_banner_badge": "FOUNDATION MANIFESTO",
    "about_banner_title": "ENGINEERED FOR EXTREME ENVIRONMENTS & MISSION-CRITICAL DEFENSE.",
    "about_banner_meta": "EST. 2026 // ZERO-DAY MATRIX",
    "about_tenet1_eyebrow": "// 01 · ARCHITECTURAL MINIMALISM",
    "about_tenet1_title": "PRECISION OVER EXCESS.",
    "about_tenet1_desc": "Traditional enterprise software sales channels are bloated by endless marketing funnels, intrusive subscription locks, and excessive telemetry tracking. We reject generic SaaS models in favor of sharp, functional, and permanent tooling.",
    "about_tenet1_tag": "TENET: ZERO CLOUD LOCK-IN",
    "about_tenet2_eyebrow": "// 02 · DIGITAL & PHYSICAL AIRGAP",
    "about_tenet2_title": "LOCAL-FIRST EXECUTION.",
    "about_tenet2_desc": "Zero dependencies on persistent cloud beacons. Once an operator acquires and verifies an operational package, it executes fully self-contained across isolated networks.",
    "about_tenet2_tag": "TENET: AUTONOMOUS RUNTIME",
    "about_tenet3_eyebrow": "// 03 · CRYPTOGRAPHIC VERIFICATION",
    "about_tenet3_title": "TRUST VIA INTEGRITY HASHES.",
    "about_tenet3_desc": "Every binary distribution, patch advisory, and software license seat is published alongside reproducible SHA-256 integrity checksums and signed PGP release tags.",
    "about_tenet3_tag": "TENET: RIGOROUS PROVENANCE",

    "about_metrics_eyebrow": "// OPERATIONAL METRICS & COMPLIANCE STANDARDS",
    "about_metric1_val": "100%",
    "about_metric1_title": "AIRGAP SAFE BINARIES",
    "about_metric1_desc": "Complete offline execution capability with zero mandatory cloud beaconing or telemetry.",
    "about_metric2_val": "< 5 MIN",
    "about_metric2_title": "DISPATCH SLA",
    "about_metric2_desc": "Direct ticket provisioning via Telegram concierge with verified download links.",
    "about_metric3_val": "SHA-256",
    "about_metric3_title": "PGP INTEGRITY ASSURANCE",
    "about_metric3_desc": "Cryptographically hashed and validated manifests for audit reproduction.",
    "about_metric4_val": "PERPETUAL",
    "about_metric4_title": "STANDALONE LICENSING",
    "about_metric4_desc": "Permanent seat allocations and unrestricted local installations for red teams.",

    "about_cta_eyebrow": "// EXPLORE ZERO//FORM DEPLOYMENTS",
    "about_cta_title": "READY TO AUDIT OUR ARSENAL?",
    "about_cta_desc": "Inspect enterprise reverse engineering suites, web security licenses, and red team platforms in our catalog.",
    "about_cta_btn1": "EXPLORE ARSENAL →",
    "about_cta_btn2": "THREAT JOURNAL →",

    # Catalog & Journal Pages
    "shop_eyebrow": "// ARSENAL INVENTORY",
    "shop_title": "DIGITAL ARSENAL.",
    "shop_subtitle": "Commercial security suites, binary analysis frameworks, and verified enterprise seats.",
    "journal_eyebrow": "// RESEARCH DISCLOSURES & INTEL",
    "journal_title": "THREAT JOURNAL.",
    "journal_subtitle": "Zero-day vulnerability disclosures, offensive security tradecraft, and verified threat research."
}


