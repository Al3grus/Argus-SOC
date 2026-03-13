# Scenario 5: Lateral Movement and Post-Exploitation

## Summary

> *This scenario will be fully documented once the build is complete.*

From the compromised Metasploitable host (obtained in Scenario 3), lateral movement is simulated: host enumeration, network discovery, and SSH attempts to Pi 3B+. Most homelab projects never test internal-to-internal attack paths. This is a senior SOC detection engineering exercise.

## MITRE ATT&CK

| Field | Value |
|-------|-------|
| Techniques | T1021 — Remote Services; T1083 — File and Directory Discovery; T1078 — Valid Accounts |
| Tactics | Lateral Movement, Discovery, Defence Evasion |

## Attack Details

| Field | Value |
|-------|-------|
| Tools | Metasploit post-exploitation modules, manual SSH from compromised host |
| Starting Point | Metasploitable 2 root shell (via Scenario 3) |
| Pivot Target | Pi 3B+ (192.168.10.20) |
| Attack Surface | East-west Lab VLAN traffic — internal host behaving as attacker |

## Commands Executed

*(to be added — planned: arp discovery, ping sweep, SSH lateral movement to Cowrie + real SSH)*

## Detection Evidence

### Wazuh
*(to be added — anomalous auth: Metasploitable IP attempting SSH to other hosts)*

### Suricata
*(to be added — internal-to-internal scanning detected via SPAN port)*

### Cowrie
*(to be added — lateral movement attempt captured as full honeypot session)*

### Claude AI Classification
*(to be added — expected: CRITICAL, internal host behaving as attacker)*

### Operator Alert
*(to be added)*

## Detection Gaps

**Valid credential evasion (T1078):** If credentials harvested from `/etc/shadow` are used to SSH to Pi 3B+ on port 2222, the authentication *succeeds* and looks like a normal login. No brute force pattern, no failed credentials. Without UEBA (User and Entity Behaviour Analytics), this may not alert.

**Detection engineering exercise:** Write a custom Wazuh rule alerting on SSH logins *from* the Metasploitable IP to any other Lab VLAN host. This custom rule is in [`pi5-central/wazuh/local_rules.xml`](../../pi5-central/wazuh/).

## Lessons Learned

*(to be added)*
