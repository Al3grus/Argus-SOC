# Scenario 1: Reconnaissance

## Summary

Nmap-based network and service discovery against the client site. This is the first stage of the kill chain — the attacker maps the attack surface before attempting exploitation. This scenario establishes baseline detection capability and tests Suricata and Zeek's ability to identify scanning activity at different intensity levels, including low-and-slow techniques designed to evade threshold-based detection.

## MITRE ATT&CK

| Field | Value |
|-------|-------|
| Technique ID | T1046 |
| Technique Name | Network Service Discovery |
| Tactic | Discovery |

## Attack Details

| Field | Value |
|-------|-------|
| Tools | Nmap (Kali Linux VM, ThinkPad, guest WiFi) |
| Targets | Pi 5 (192.168.1.10), Pi 3B+ (192.168.1.20), full subnet |
| Attack Surface | All switch-connected devices, visible via SPAN |

## Commands Executed

```bash
# Phase 1: Aggressive scan — triggers immediately
nmap -sS -sV -O -sC 192.168.1.0/24

# Phase 2: Full port scan on Pi 5 (attack targets)
nmap -sS -sV -p 1-65535 192.168.1.10

# Phase 3: Stealth timing — tests evasion
nmap -sS -T1 192.168.1.10    # Paranoid: 1 probe per 5 minutes
nmap -sS -T2 192.168.1.10    # Polite timing

# Phase 4: Fragmented packets
nmap -sS -f 192.168.1.10
```

## Detection Evidence

### Suricata
> *To be populated after execution — expected: ET SCAN signatures, SIDs in 2000000–2099999 range*

### Zeek
> *To be populated after execution — expected: conn.log showing SYN sweep pattern*

### Wazuh
> *To be populated after execution — expected: Suricata alerts correlated by Wazuh, MITRE T1046 tagged*

### Claude AI Classification
> *To be populated after execution — expected: Medium (aggressive scan) / Low or Noise (stealth)*

```json
{
  "severity": "<to be populated>",
  "summary": "<to be populated>",
  "mitre_technique": "T1046",
  "mitre_technique_name": "Network Service Discovery",
  "recommended_action": "<to be populated>",
  "confidence": 0.0,
  "reasoning": "<to be populated>"
}
```

### Operator Alert (Telegram)
> *Screenshot to be added after execution*

### Velociraptor
> *N/A for this scenario — no endpoint compromise*

## Detection Gaps

### Low-and-Slow Reconnaissance
Suricata ET SCAN rules use threshold-based detection (X events in Y seconds). T1 and T2 timing scans fall below these thresholds and do not trigger. Zeek conn.log captures the pattern over time but requires manual review or a custom Zeek script for automated alerting.

**Recommendation:** Custom Zeek notice script for SYN sweeps below Suricata thresholds. Document the exact threshold values from the triggered rules.

### Fragmented Packet Evasion
Some Suricata signature rules may not fire on fragmented packets (-f flag). Test and document which SIDs still fire and which do not.

**Expected finding:** Signature-based detection has inherent limitations against low-and-slow reconnaissance. Behavioural analysis over longer time windows would be needed. This is the expected behaviour of signature-based NIDS — document it honestly.

## Lessons Learned

> *To be populated after execution*
