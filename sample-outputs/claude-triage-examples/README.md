# Claude API Triage Examples

Real Claude API JSON responses from the five red team scenarios, added during Phase 4.

Each file shows the full request context and response for a representative alert from each scenario, covering all four severity levels.

## Files (added in Phase 4)

| File | Scenario | Severity | Description |
|------|----------|----------|-------------|
| `01-recon-noise.json` | Reconnaissance | noise | Single port probe from known scanner |
| `01-recon-medium.json` | Reconnaissance | medium | Aggressive nmap -sS -sV sweep |
| `02-brute-medium.json` | Brute Force | medium | Hydra SSH attempt pattern |
| `02-brute-critical.json` | Brute Force | critical | Cowrie login success + command execution |
| `03-rce-critical.json` | RCE | critical | vsftpd 2.3.4 backdoor trigger (CVE-2011-2523) |
| `04-web-medium.json` | Web Attacks | medium | SQL injection attempt in HTTP |
| `04-web-low.json` | Web Attacks | low | XSS probe, no success indicator |
| `05-lateral-critical.json` | Lateral Movement | critical | SSH from Metasploitable IP to Pi 3B+ |

## Format

Each file contains:

```json
{
  "alert_sent": {
    "rule": { ... },
    "agent": { ... },
    "data": { ... }
  },
  "claude_response": {
    "severity": "...",
    "summary": "...",
    "mitre_technique": "...",
    "mitre_technique_name": "...",
    "recommended_action": "...",
    "confidence": 0.0,
    "reasoning": "..."
  }
}
```
