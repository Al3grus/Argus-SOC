# Scenario 4: Web Application Attacks

## Summary

> *This scenario will be fully documented once the build is complete.*

SQL injection, XSS, command injection, and file upload attacks are executed against DVWA (Damn Vulnerable Web App). Suricata's web attack rules detect injection patterns in HTTP traffic. The scenario is run at DVWA Low, Medium, and High security levels to test how defensive controls on the target affect network-layer detection.

## MITRE ATT&CK

| Field | Value |
|-------|-------|
| Techniques | T1190 — Exploit Public-Facing Application; T1059.007 — Command and Scripting: JavaScript |
| Tactics | Initial Access, Execution |

## Attack Details

| Field | Value |
|-------|-------|
| Tools | SQLmap (automated SQLi), Burp Suite (manual XSS/command injection) |
| Target | DVWA on Lab VLAN |
| Attack Surface | HTTP web application — SQLi, XSS, command injection, file upload endpoints |
| Attack Types | SQL injection, reflected XSS, stored XSS, command injection, file upload |

## Commands Executed

*(to be added)*

## Detection Evidence

### Suricata
*(to be added — ET Open web rules: UNION SELECT patterns, script tags, event handlers)*

### Wazuh
*(to be added)*

### Claude AI Classification
*(to be added)*

### Operator Alert
*(to be added)*

## Detection Gaps

**Critical TLS inspection gap:** If DVWA were served over HTTPS, Suricata would see only the TLS handshake — no SQL injection strings, no XSS payloads. The entire network-layer web attack detection capability depends on unencrypted HTTP. In production, SSL inspection (mitmproxy, Squid SSL bump) would be required between the NIDS and HTTPS endpoints. This is a genuine enterprise SOC challenge — document it thoroughly.

## Lessons Learned

*(to be added)*
