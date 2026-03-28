# Scenario 4: Web Application Attacks

## Summary

SQL injection and XSS attacks against DVWA (Damn Vulnerable Web Application) running as a Docker container on Pi 5. This scenario demonstrates OWASP Top 10 detection at the network layer using Suricata and Zeek on unencrypted HTTP traffic. It also documents the TLS inspection gap — one of the most important architectural limitations to understand in production web attack detection.

## MITRE ATT&CK

| Field | Value |
|-------|-------|
| Technique IDs | T1190, T1059.007 |
| Technique Names | Exploit Public-Facing Application; Command and Scripting: JavaScript |
| Tactics | Initial Access, Execution |

## Attack Details

| Field | Value |
|-------|-------|
| Tools | Burp Suite + SQLmap (Kali Linux VM, ThinkPad, guest WiFi) |
| Target | DVWA Docker container on Pi 5 |
| Security Level | Low (initial), then Medium and High |

## Commands Executed

```bash
# SQL Injection (automated):
sqlmap -u 'http://192.168.1.10/vulnerabilities/sqli/?id=1&Submit=Submit' \
  --cookie='PHPSESSID=<session>; security=low' --dbs --batch

# XSS (manual via browser or Burp Suite):
# In DVWA XSS Reflected: input <script>alert('XSS')</script>
# In DVWA XSS Stored:    input <img src=x onerror=alert('XSS')>

# Command Injection:
# In DVWA Command Injection: input 127.0.0.1; cat /etc/passwd

# File Upload (Low security):
# Upload a PHP webshell through DVWA File Upload

# Repeat at Medium and High difficulty levels
```

## Detection Evidence

### Suricata
> *To be populated after execution — expected: ET web attack rules detecting SQL injection patterns (UNION SELECT, OR 1=1) and XSS payloads in HTTP traffic*

### Zeek
> *To be populated after execution — expected: http.log showing suspicious URI patterns and payloads*

### Wazuh
> *To be populated after execution — expected: Suricata web attack alerts correlated, HTTP error patterns*

### Claude AI Classification
> *To be populated after execution — expected: Medium/Critical depending on HTTP response indicators*

```json
{
  "severity": "<to be populated>",
  "summary": "<to be populated>",
  "mitre_technique": "T1190",
  "mitre_technique_name": "Exploit Public-Facing Application",
  "recommended_action": "<to be populated>",
  "confidence": 0.0,
  "reasoning": "<to be populated>"
}
```

### Operator Alert (Telegram)
> *Screenshot to be added after execution*

### Velociraptor
> *N/A — web attacks are network-layer only in this scenario. DVWA runs in Docker with no agent.*

## Detection Gaps

### TLS Inspection Gap (Critical)

**This is the most important limitation to document in this scenario.**

If DVWA were served over HTTPS, Suricata and Zeek would see only the TLS handshake and encrypted payload — no SQL injection strings, no XSS payloads, nothing. The entire web attack detection capability depends on HTTP (unencrypted) traffic.

In production, an SSL inspection proxy (e.g., mitmproxy, Squid SSL bump) would be required between the NIDS and HTTPS endpoints. This adds complexity, certificate management overhead, and privacy concerns.

This is a genuine enterprise SOC challenge, not a lab limitation. Document it as: *"In production, an SSL inspection proxy would be needed for HTTPS endpoints. This adds complexity and privacy tradeoffs that must be evaluated per deployment."*

## Lessons Learned

> *To be populated after execution*
