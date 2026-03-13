# MITRE ATT&CK Coverage Map

Every row links to documented evidence of detection — or documented non-detection with root cause analysis. Detection gaps are as important as detections.

## Coverage by Technique

| Technique ID | Name | Tactic | Scenario | Primary Detection | Detection Confidence |
|-------------|------|--------|----------|------------------|---------------------|
| T1046 | Network Service Discovery | Discovery | [1 — Recon](../docs/detection-scenarios/01-reconnaissance.md) | Suricata ET SCAN | **High** (aggressive scans) / **Low** (stealth) |
| T1110.001 | Brute Force: Password Guessing | Credential Access | [2 — Brute Force](../docs/detection-scenarios/02-brute-force.md) | Cowrie + Wazuh correlation | **High** |
| T1190 | Exploit Public-Facing Application | Initial Access | [3 — Exploitation](../docs/detection-scenarios/03-exploitation.md), [4 — Web Attacks](../docs/detection-scenarios/04-web-attacks.md) | Suricata payload signature | **High** (known CVE) |
| T1059.007 | Command and Scripting: JavaScript | Execution | [4 — Web Attacks](../docs/detection-scenarios/04-web-attacks.md) | Suricata XSS/injection rules | **Medium** (HTTP only — see TLS gap) |
| T1021 | Remote Services | Lateral Movement | [5 — Lateral Movement](../docs/detection-scenarios/05-lateral-movement.md) | Wazuh auth logs + Suricata | **Medium** |
| T1083 | File and Directory Discovery | Discovery | [5 — Lateral Movement](../docs/detection-scenarios/05-lateral-movement.md) | Wazuh FIM + Suricata enum sigs | **Medium** |
| T1078 | Valid Accounts | Defence Evasion | [5 — Lateral Movement](../docs/detection-scenarios/05-lateral-movement.md) | Wazuh anomalous auth (custom rule) | **Low** (requires UEBA for High) |

> *Evidence column links will be populated as scenarios are executed.*

---

## Confidence Definitions

| Rating | Meaning |
|--------|---------|
| **High** | Detection fires reliably and consistently. Suricata rule or Wazuh correlation produces an alert >90% of the time the technique is executed as documented. |
| **Medium** | Detection fires under specific conditions only. May miss variations (e.g., encrypted channels, timing evasion, valid credentials). |
| **Low** | Detection is technically possible but requires additional tooling (UEBA, custom rules, Zeek) or specific conditions not present in the current stack. |
| **Not Detected** | Technique was executed; no alert fired. Documented with root cause. |

---

## Detection Gaps Summary

| Gap | Affected Techniques | Cause | Remediation |
|-----|--------------------|----|-------------|
| Low-and-slow recon evasion | T1046 | ET SCAN rules require N events/second threshold | Zeek connection tracking over hours; custom Suricata rules with longer windows |
| TLS inspection gap | T1190, T1059.007 | Suricata cannot inspect encrypted HTTPS | SSL inspection proxy (mitmproxy, Squid SSL bump) between NIDS and HTTPS endpoints |
| Encrypted post-exploitation | T1190 | Meterpreter HTTPS C2 opaque to Suricata | Suricata JA3/JA3S fingerprinting; Zeek SSL log analysis |
| Valid credential lateral movement | T1078 | Legitimate auth from anomalous source = normal login | UEBA; custom Wazuh rule on auth from Metasploitable IP |
| No host-based coverage on Metasploitable | T1190+ | No Wazuh Agent on target VM | Deploy Wazuh Agent on Metasploitable; YARA for file detection |

---

## MITRE Navigator Export

*(ATT&CK Navigator layer JSON will be added once scenarios are complete — provides visual heatmap of technique coverage)*
