# Scenario 2: Credential Brute Force

## Summary

> *This scenario will be fully documented once the build is complete.*

Hydra performs a dictionary attack against the Cowrie SSH honeypot on port 22. Once Cowrie "accepts" credentials, an interactive session is started to simulate post-compromise attacker behaviour. The full session — every credential tried, every command typed — is captured in Cowrie's JSON logs and forwarded to Wazuh.

## MITRE ATT&CK

| Field | Value |
|-------|-------|
| Technique | T1110.001 — Brute Force: Password Guessing |
| Tactic | Credential Access |

## Attack Details

| Field | Value |
|-------|-------|
| Tool | Hydra (Kali Linux VM) |
| Target | Cowrie SSH honeypot on Pi 3B+, port 22 |
| Attack Surface | SSH service (Cowrie masquerading as OpenSSH) |
| Wordlist | rockyou.txt |
| Expected Detection | Cowrie full session log + Wazuh brute force correlation |

## Commands Executed

*(to be added)*

## Detection Evidence

### Cowrie
*(full session transcript to be added — credentials tried, commands executed, download attempts)*

### Wazuh
*(to be added)*

### Claude AI Classification
*(to be added)*

### Operator Alert
*(to be added)*

## Detection Gaps

**Honeypot fingerprinting:** Sophisticated attackers can identify Cowrie via timing anomalies, virtual filesystem inconsistencies, or banner analysis. If identified, the attacker pivots to port 2222 (real SSH) — Cowrie sees nothing. Suricata and Wazuh must catch attacks on the real service.

## Lessons Learned

*(to be added)*
