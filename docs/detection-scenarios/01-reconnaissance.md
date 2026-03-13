# Scenario 1: Reconnaissance

## Summary

> *This scenario will be fully documented once the build is complete.*

Nmap is used to perform network and service discovery against the Lab VLAN. Three scan intensities are tested: aggressive (T4/T5), normal, and stealth (T1/T2). The goal is to establish baseline detection capability and measure the threshold at which Suricata's ET SCAN rules fire — and where they don't.

## MITRE ATT&CK

| Field | Value |
|-------|-------|
| Technique | T1046 — Network Service Discovery |
| Tactic | Discovery |

## Attack Details

| Field | Value |
|-------|-------|
| Tool | Nmap (Kali Linux VM) |
| Target | Pi 3B+ (192.168.10.20), Metasploitable 2, full Lab VLAN subnet (192.168.10.0/24) |
| Attack Surface | All Lab VLAN hosts — open ports, service banners, OS fingerprinting |
| Expected Detection | Suricata ET SCAN rules (aggressive + normal scans) |
| Expected Gap | T1/T2 timing scans fall below signature thresholds |

## Commands Executed

*(to be added — planned commands documented in [Project Book](../../README.md))*

## Detection Evidence

### Suricata
*(to be added)*

### Wazuh
*(to be added)*

### Claude AI Classification
*(to be added)*

### Operator Alert
*(to be added)*

## Detection Gaps

**Known gap to document:** ET SCAN rules require N events in Y seconds. Slow timing scans (T1: one probe per 5 minutes) fall below the threshold and are not detected. This is expected behaviour, not a flaw — documenting it honestly demonstrates senior-level analytical thinking.

**Fragmented packets (-f flag):** Some signature rules may not fire on fragmented packets. Will test and document which rules fire and which don't.

## Lessons Learned

*(to be added)*
