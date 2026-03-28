# Telegram Alert Screenshots

Operator alert screenshots from the five red team scenarios, added during Phase 4.

Each screenshot shows the formatted Telegram message as it appears on the operator's phone, demonstrating the full pipeline from detection to notification.

## Files (added in Phase 4)

| File | Scenario | Severity | Description |
|------|----------|----------|-------------|
| `02-brute-critical.png` | Brute Force | critical | Cowrie login success — immediate escalation |
| `03-rce-critical.png` | RCE | critical | vsftpd exploit detected — PagerDuty fired |
| `04-web-medium.png` | Web Attacks | medium | SQL injection attempt |
| `05-lateral-critical.png` | Lateral Movement | critical | Internal host SSH pivot |

## Message Format

Telegram messages follow this format:

```
🔴 CRITICAL — Argus SOC Alert

Summary: [Claude plain-English summary]

Technique: T1190 — Exploit Public-Facing Application
Confidence: 97%
Action: respond_immediately

Source: 10.0.0.3 → 192.168.1.10
Agent: argus-edge-01
Rule: [Suricata rule name]

🔗 Wazuh Dashboard
```
