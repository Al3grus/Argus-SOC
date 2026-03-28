# Scenario 5: Lateral Movement and Post-Exploitation

## Summary

Using a foothold on Metasploitable 2 (obtained in Scenario 3) to pivot and attempt lateral movement to the Pi 3B+ edge sensor. This scenario tests east-west traffic detection — most homelab projects never simulate internal-to-internal attack paths. Zeek and Suricata both see all switch traffic via SPAN, enabling detection of lateral movement between hosts regardless of whether the Pi 3B+ is the target or the source.

## MITRE ATT&CK

| Field | Value |
|-------|-------|
| Technique IDs | T1021, T1083, T1078 |
| Technique Names | Remote Services; File and Directory Discovery; Valid Accounts |
| Tactics | Lateral Movement, Discovery, Defence Evasion |

## Attack Details

| Field | Value |
|-------|-------|
| Tools | Metasploit post-exploitation modules, manual SSH |
| Starting Point | Metasploitable 2 root shell (from Scenario 3) |
| Target | Pi 3B+ (192.168.1.20) — pivot attempt |

## Commands Executed

```bash
# From Metasploitable 2 root shell (Docker container on Pi 5):
cat /etc/shadow           # Extract password hashes
cat /etc/passwd           # Enumerate users
arp -a                    # Discover other hosts
ping -c 1 192.168.1.20   # Confirm Pi 3B+ reachable

# Attempt SSH to Pi 3B+ from Metasploitable:
ssh root@192.168.1.20         # Hits Cowrie honeypot (port 22)
ssh pi@192.168.1.20 -p 2222   # Attempt real SSH

# From Kali using Metasploit post modules (active session from Scenario 3):
sessions -l
sessions -i 1
run post/linux/gather/enum_system
run post/linux/gather/hashdump
run post/multi/gather/ping_sweep RHOSTS=192.168.1.0/24
```

## Detection Evidence

### Suricata
> *To be populated after execution — expected: ET SCAN alerts from Metasploitable IP, internal host scanning*

### Zeek
> *To be populated after execution — expected: conn.log showing internal-to-internal traffic patterns from Metasploitable IP*

### Wazuh
> *To be populated after execution — expected: auth log events showing SSH attempts from unexpected internal source, custom rule 100001 firing*

### Claude AI Classification
> *To be populated after execution — expected: CRITICAL with "internal host behaving as attacker" framing*

```json
{
  "severity": "critical",
  "summary": "<to be populated — expected to flag internal lateral movement>",
  "mitre_technique": "T1021",
  "mitre_technique_name": "Remote Services",
  "recommended_action": "respond_immediately",
  "confidence": 0.0,
  "reasoning": "<to be populated>"
}
```

### Operator Alert (Telegram)
> *Screenshot to be added after execution*

### Velociraptor
> *Metasploitable 2 has no agent. Pi 3B+ Velociraptor agent can be queried post-scenario for endpoint evidence of the pivot attempt.*

## Detection Gaps

### Valid Account Evasion (Key Gap)

If the attacker harvests valid credentials from `/etc/shadow` (Scenario 3) and uses them to SSH to Pi 3B+ on port 2222 with legitimate credentials, **the authentication succeeds and looks like a normal login**. No brute force pattern, no invalid credentials. Wazuh sees a successful SSH login from an unexpected source IP, but without UEBA, this may not trigger an alert automatically.

**Detection engineering response:** Custom Wazuh rule to alert on SSH logins from unexpected internal hosts:

```xml
<rule id="100001" level="12">
  <if_sid>5715</if_sid>
  <srcip>192.168.1.10</srcip>
  <description>SSH login from Pi 5 / Metasploitable IP — lateral movement indicator (T1021)</description>
  <mitre>
    <id>T1021</id>
  </mitre>
</rule>
```

This rule is included in `hetzner-soc/wazuh/local_rules.xml`.

**Longer term:** Behavioural analytics (UEBA) would be needed to detect legitimate credential usage from anomalous source hosts at high confidence.

## Lessons Learned

> *To be populated after execution*
