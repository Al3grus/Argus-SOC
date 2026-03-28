# MITRE ATT&CK Coverage Map

Evidence-based detection coverage across the five red team scenarios. Every row will link to documented evidence of detection — or documented non-detection with root cause analysis — once Phase 4 is complete.

## Coverage Table

| Technique ID | Name | Tactic | Scenario | Primary Detection | Secondary Detection | Confidence |
|-------------|------|--------|----------|------------------|--------------------|-----------| 
| T1046 | Network Service Discovery | Discovery | 1 — Reconnaissance | Suricata ET SCAN signatures | Zeek conn.log (SYN sweep pattern) | High (aggressive) / Low (stealth) |
| T1110.001 | Brute Force: Password Guessing | Credential Access | 2 — Brute Force | Cowrie session logs | Wazuh auth correlation | High |
| T1190 | Exploit Public-Facing Application | Initial Access | 3 — RCE, 4 — Web Attacks | Suricata payload signature | Zeek http.log | High (known CVE) |
| T1059.007 | Command and Scripting: JavaScript | Execution | 4 — Web Attacks | Suricata XSS/injection rules | Zeek http.log (HTTP only) | Medium |
| T1021 | Remote Services | Lateral Movement | 5 — Lateral Movement | Wazuh auth logs + custom rule 100001 | Zeek conn.log | Medium |
| T1083 | File and Directory Discovery | Discovery | 5 — Lateral Movement | Velociraptor VQL + Wazuh FIM | — | Medium |
| T1078 | Valid Accounts | Defence Evasion | 5 — Lateral Movement | Wazuh custom rule 100002 | — | Low (requires UEBA for High) |
| T1071.004 | Application Layer Protocol: DNS | C2 | Ongoing | Wazuh custom rule 100006 (high-risk TLD) | Pi-hole query logs | Medium |
| T1105 | Ingress Tool Transfer | Command and Control | 2 — Brute Force | Cowrie file download log | Wazuh custom rule 100004 | High (within honeypot) |

## Detection Confidence Definitions

| Confidence | Meaning |
|-----------|---------|
| High | Detection fires reliably. Documented evidence from scenario execution. |
| Medium | Detection fires in most cases. Known gaps documented. |
| Low | Detection requires additional tooling or manual analysis. Gap documented with remediation recommendation. |

## Known Detection Gaps

> *Gaps will be verified and expanded after Phase 4 execution. The following are anticipated based on tool capabilities.*

### Gap 1: Low-and-Slow Reconnaissance (T1046)
Suricata ET SCAN rules use threshold-based detection (X events in Y seconds). T1/T2 timing scans fall below these thresholds. Zeek conn.log captures the pattern over time but requires manual review or a custom Zeek script for automated alerting.

**Recommendation:** Custom Zeek notice script for SYN sweeps below Suricata thresholds.

### Gap 2: Encrypted Post-Exploitation C2 (T1071)
Once an attacker establishes an encrypted reverse shell, Suricata and Zeek see only encrypted traffic. The initial exploit is detectable; subsequent commands are not.

**Recommendation:** JA3/JA3S fingerprinting via Zeek ssl.log for unusual TLS client fingerprints. Velociraptor process inspection to detect reverse shell processes.

### Gap 3: Valid Credential Lateral Movement (T1078)
When an attacker uses harvested valid credentials, the SSH login succeeds and appears normal. Without UEBA, the anomalous source IP may not trigger an alert.

**Remediation implemented:** Custom Wazuh rule 100002 alerts on SSH logins from unexpected internal hosts. See `hetzner-soc/wazuh/local_rules.xml`.

### Gap 4: HTTPS Web Attacks (T1190)
If DVWA were served over HTTPS, Suricata and Zeek would see only encrypted traffic. No SQL injection or XSS detection is possible without SSL inspection.

**Recommendation:** In production, deploy an SSL inspection proxy between the NIDS and HTTPS endpoints. Document the complexity and privacy tradeoffs — this is a genuine enterprise SOC challenge.

### Gap 5: Cowrie Fingerprinting
Sophisticated attackers can identify Cowrie via timing anomalies or filesystem inconsistencies. If identified, they may pivot to port 2222 (real SSH) which is not captured by Cowrie.

## Evidence Links

Evidence for each detection is documented in the scenario write-ups:

- [Scenario 1 — Reconnaissance](../docs/detection-scenarios/01-reconnaissance.md)
- [Scenario 2 — Brute Force](../docs/detection-scenarios/02-brute-force.md)
- [Scenario 3 — Remote Code Execution](../docs/detection-scenarios/03-exploitation.md)
- [Scenario 4 — Web Application Attacks](../docs/detection-scenarios/04-web-attacks.md)
- [Scenario 5 — Lateral Movement](../docs/detection-scenarios/05-lateral-movement.md)
