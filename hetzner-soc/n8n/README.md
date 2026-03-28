# n8n Workflow Engine — Hetzner VPS

n8n is co-located with Wazuh on the Hetzner VPS. Wazuh webhooks go to `http://localhost:5678/webhook/wazuh-alert` — a local call, no external network hop.

## Access

```
http://<HETZNER_IP>:5678
```

Port 5678 is restricted in UFW to trusted IPs only — do not expose publicly without authentication.

## Workflows

### 1. Wazuh Alert Triage Pipeline

Main automation pipeline. Nodes in order:

| # | Node | Purpose |
|---|------|---------|
| 1 | Webhook | Receives raw alert JSON from Wazuh at `/webhook/wazuh-alert` |
| 2 | Function | Extracts: rule.id, rule.description, rule.level, agent.name, data.srcip, data.dstip, rule.mitre |
| 3 | HTTP Request | POST to Claude API (https://api.anthropic.com/v1/messages) with structured prompt |
| 4 | Function | Parses Claude JSON response — extracts severity, summary, mitre_technique, confidence |
| 5 | Switch | Routes by severity: noise / low / medium / critical |
| 6 | Telegram | Sends formatted alert to operator (medium + critical) |
| 7 | HTTP Request | POST to PagerDuty EU endpoint (critical only) |
| 8 | Function | Appends to ~/argus/logs/all_events.jsonl for reporting |

### 2. WireGuard Down Alert

Triggered by `wg_monitor.sh` on Pi 5 when Pi 3B+ tunnel is unreachable. Routes directly to Telegram + PagerDuty — no AI triage needed. An offline edge sensor is always a critical alert.

### 3. Monthly Report Generator

Triggers on the 1st of each month. Reads all_events.jsonl, generates PDF via Jinja2 + WeasyPrint, saves to ~/argus/reports/output/.

## PagerDuty Configuration

**Always use the EU endpoint:**
```
https://events.eu.pagerduty.com/v2/enqueue
```

NOT the global endpoint `https://events.pagerduty.com/v2/enqueue` — EU accounts require the EU endpoint or alerts silently fail.

## Exporting Workflows

To export a workflow for this repository:
1. Open n8n UI
2. Select the workflow
3. Click ⋮ → Download
4. Save the JSON file here

> **Important:** Sanitise any API keys, tokens, or credentials from exported workflow JSON before committing. Check for hardcoded Telegram tokens, PagerDuty keys, and Anthropic API keys.
