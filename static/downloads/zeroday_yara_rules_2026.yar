/*
 * ZERODAY // INTEL — High-Confidence Ransomware & C2 Beacon YARA Ruleset (2026.11)
 * Compatible with YARA v4.x, Splunk Enterprise Security & Velociraptor
 */

rule APT_Memory_Reflective_Loader_2026 {
    meta:
        author = "ZeroDay Threat Intel Unit"
        severity = "CRITICAL"
        cve = "CVE-2026-4412"
        description = "Detects reflective DLL/SO injection stubs and unbacked RWX memory beacons"
    strings:
        $mz = { 4D 5A 90 00 03 00 00 00 }
        $api1 = "VirtualAllocEx" ascii wide
        $api2 = "NtProtectVirtualMemory" ascii
        $api3 = "CreateRemoteThreadEx" ascii
        $ beacon_magic = { 7F 45 4C 46 02 01 01 00 }
    condition:
        ($mz at 0 or $beacon_magic at 0) and 2 of ($api*)
}

rule WebShell_Obfuscated_JSP_PHP_2026 {
    meta:
        author = "ZeroDay Threat Intel Unit"
        severity = "HIGH"
        description = "Detects runtime eval/base64/aes webshell execution chains"
    strings:
        $s1 = "javax.crypto.Cipher" ascii
        $s2 = "Runtime.getRuntime().exec" ascii
        $s3 = "base64_decode($_POST" ascii nocase
        $s4 = "gzinflate(str_rot13(" ascii nocase
    condition:
        any of them
}
