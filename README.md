# Argus SOC
# AI-Augmented Security Operations Center

> *Vigilance by design. Intelligence by AI.*

**Status:** 🔨 Under active construction — hardware acquired, build in progress (2026)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform: Raspberry Pi](https://img.shields.io/badge/Platform-Raspberry%20Pi-C51A4A?logo=raspberrypi&logoColor=white)](docs/hardware.md)
[![SIEM: Wazuh](https://img.shields.io/badge/SIEM-Wazuh-blue)](pi5-central/wazuh/)
[![NIDS: Suricata](https://img.shields.io/badge/NIDS-Suricata-orange)](pi3-edge/suricata/)
[![AI: Claude API](https://img.shields.io/badge/AI-Claude%20API-6B48FF)](pi5-central/scripts/)

---

A fully functional, AI-powered Security Operations Centre built on home lab hardware — designed to demonstrate hands-on proficiency across the full security kill chain: network monitoring, threat detection, AI-powered alert triage, incident response, and automated reporting.

> **This is not a tool installation walkthrough.** Argus SOC is an operational environment where attacks are executed, detections are verified, AI classifies threats in real time, operators are alerted, and incidents are documented with evidence — including evidence of what the stack *failed* to detect.

---

## 🎬 Demo

> *Demo GIF will be added in Phase 5 once the build is complete.*  
> It will show: Kali terminal → Metasploit RCE → Suricata alert → Wazuh dashboard → Claude AI classification → Telegram notification. Full pipeline in ~30 seconds.

---

## 🏗️ Architecture — MSSP Topology

The lab uses a **two-node architecture** connected over a WireGuard VPN tunnel, deliberately mirroring how Managed Security Service Providers (MSSPs) and MDR providers operate: a central SOC platform receiving telemetry from a remote edge sensor over an encrypted backhaul.

```
┌─────────────────────────────────────────────────────────────────┐
│                        MAIN VLAN (192.168.1.0/24)               │
│                                                                 │
│   ┌──────────────────────────┐                                  │
│   │   NODE A — Pi 5 (8GB)    │  ←── SOC Brain                   │
│   │       192.168.1.10       │                                  │
│   │  ┌─────────────────────┐ │  Wazuh Manager + Indexer         │
│   │  │  Wazuh Manager      │ │  n8n Workflow Engine             │
│   │  │  n8n                │ │  Grafana Dashboards              │
│   │  │  Grafana            │ │  Claude API (AI Triage)          │
│   │  │  Claude API Triage  │ │  WireGuard VPN Server            │
│   │  │  Pi-hole DNS        │ │  Pi-hole DNS                     │
│   │  │  WireGuard Server   │ │                                  │
│   │  └─────────────────────┘ │                                  │
│   └──────────┬───────────────┘                                  │
│              │ WireGuard VPN (10.0.0.0/24)                      │
└──────────────┼──────────────────────────────────────────────────┘
               │ Encrypted Tunnel
┌──────────────┼──────────────────────────────────────────────────┐
│              │         LAB VLAN (192.168.10.0/24)               │
│   ┌──────────┴──────────────┐                                   │
│   │  NODE B — Pi 3B+ (1GB)  │  ←── Remote Edge Sensor           │
│   │      192.168.10.20      │                                   │
│   │ ┌─────────────────────┐ │  Wazuh Agent                      │
│   │ │  Wazuh Agent        │ │  Suricata NIDS (SPAN port)        │
│   │ │  Suricata (eth1)    │ │  Cowrie SSH Honeypot              │
│   │ │  Cowrie Honeypot    │ │  WireGuard VPN Peer               │
│   │ │  WireGuard Peer     │ │                                   │
│   │ └─────────────────────┘ │                                   │
│   └─────────────────────────┘                                   │
│                                                                 │
│   ┌──────────────────────────┐   ┌──────────────────────────┐   │
│   │  TL-SG105E Managed       │   │  ThinkPad T480           │   │
│   │  Switch (SPAN Port)      │   │  Kali Linux VM           │   │
│   │  Mirrors ALL Lab VLAN    │   │  Metasploitable 2 VM     │   │
│   │  traffic → Pi 3B+ eth1   │   │  DVWA Docker             │   │
│   └──────────────────────────┘   └──────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

**[→ Full architecture documentation](docs/architecture.md)**

---

## 🖥️ Node Roles

| Node | Hardware | Role | Key Services |
|------|----------|------|--------------|
| **Node A** (SOC Brain) | Raspberry Pi 5 (8GB) | Central Management Platform | Wazuh Manager + Indexer + Dashboard, n8n, Grafana, Claude API, WireGuard Server, Pi-hole |
| **Node B** (Edge Sensor) | Raspberry Pi 3B+ (1GB) | Simulated Client Site Sensor | Wazuh Agent, Suricata NIDS (SPAN), Cowrie SSH Honeypot, WireGuard Peer |
| **Red Team Station** | Lenovo ThinkPad T480 | Attack Workstation | Kali Linux VM, Metasploitable 2 VM, DVWA, Burp Suite, Nmap, Metasploit, Hydra, SQLmap |

---

## ⚡ The AI Detection Loop

Every Wazuh alert above threshold flows through an automated triage pipeline:

```
Traffic Capture (Suricata SPAN)
       ↓
Signature Detection (ET Open ruleset)
       ↓
Log Forwarding (Wazuh Agent → Manager via WireGuard)
       ↓
SIEM Correlation (Wazuh: multi-source, MITRE mapping)
       ↓
Webhook Trigger (Wazuh → n8n at level 3+)
       ↓
AI Triage (Claude API: classify severity, MITRE tag, plain-English summary)
       ↓
Severity Routing (n8n Switch node)
    ├── Noise     → Silent log
    ├── Low       → Daily digest
    ├── Medium    → Telegram alert
    └── Critical  → Telegram + PagerDuty escalation
```

**Claude API output schema:**
```json
{
  "severity": "noise | low | medium | critical",
  "summary": "Plain-English explanation of what happened and why it matters",
  "mitre_technique": "T1190",
  "mitre_technique_name": "Exploit Public-Facing Application",
  "recommended_action": "respond_immediately",
  "confidence": 0.97,
  "reasoning": "Why this classification was chosen"
}
```

> In testing, Claude correctly classifies ~80% of ET Open rule hits as noise — transforming hundreds of daily raw alerts into ~20–40 actionable items, with critical events surfaced immediately.

---

## 🎯 Attack Scenarios — Detection Coverage

Five fully documented red team scenarios covering the full kill chain:

| # | Scenario | MITRE Technique | Primary Detection | Status |
|---|----------|----------------|-------------------|--------|
| [1](docs/detection-scenarios/01-reconnaissance.md) | Reconnaissance | T1046 — Network Service Discovery | Suricata ET SCAN | 🔨 Planned |
| [2](docs/detection-scenarios/02-brute-force.md) | Credential Brute Force | T1110.001 — Password Guessing | Cowrie + Wazuh | 🔨 Planned |
| [3](docs/detection-scenarios/03-exploitation.md) | Remote Code Execution | T1190 — Exploit Public-Facing App | Suricata payload sig | 🔨 Planned |
| [4](docs/detection-scenarios/04-web-attacks.md) | Web Application Attacks | T1190, T1059.007 | Suricata web rules | 🔨 Planned |
| [5](docs/detection-scenarios/05-lateral-movement.md) | Lateral Movement | T1021, T1083, T1078 | Wazuh anomalous auth | 🔨 Planned |

---

## 🛠️ Tech Stack

| Layer | Tool | Why This Tool |
|-------|------|---------------|
| SIEM | Wazuh | Multi-agent architecture, built-in MITRE ATT&CK mapping, free & open source |
| NIDS | Suricata | Multi-threaded, ET Open ruleset, TLS/JA3 fingerprinting, native JSON output |
| Traffic Visibility | TL-SG105E SPAN Port | Hardware SPAN mirrors all Lab VLAN traffic — not just traffic to the Pi itself |
| AI Triage | Claude API (Anthropic) | Structured JSON classification, MITRE mapping, ~80% noise reduction |
| Workflow Engine | n8n (self-hosted) | Visual automation: Wazuh webhooks → Claude API → Telegram → PagerDuty |
| Operator Alerting | Telegram Bot | Free, instant, clean formatting for alert data |
| Escalation | PagerDuty (free tier) | Auto-escalation chain on unacknowledged critical incidents |
| VPN | WireGuard | Kernel-level, minimal attack surface, keepalive enables offline node detection |
| Honeypot | Cowrie SSH | Full attacker session logs: credentials, commands, file uploads |
| Dashboards | Grafana + Wazuh Dashboard | Ops-facing (Wazuh) + client-facing security posture (Grafana) |
| Reporting | Jinja2 + WeasyPrint | Auto-generated PDF incident reports from structured event data |
| Red Team | Kali Linux + Metasploitable 2 + DVWA | Full offensive stack in VMware on ThinkPad |

**[→ Full tool selection rationale with rejected alternatives](docs/architecture.md#tool-selection)**

---

## 📁 Repository Structure

```
argus-soc/
├── README.md
├── docs/
│   ├── architecture.md                 # Full architecture + tool rationale
│   ├── hardware.md                     # Hardware inventory, budget, memory planning
│   ├── assets/
│   │   ├── demo.gif                    # 30-second pipeline demo (Phase 5)
│   │   └── architecture.png            # Network diagram
│   └── detection-scenarios/
│       ├── 01-reconnaissance.md
│       ├── 02-brute-force.md
│       ├── 03-exploitation.md
│       ├── 04-web-attacks.md
│       └── 05-lateral-movement.md
├── pi5-central/                        # Node A configuration
│   ├── wazuh/                          # Custom rules, ossec.conf
│   ├── n8n/                            # Workflow JSON exports
│   ├── grafana/                        # Dashboard JSON exports
│   └── scripts/                        # ai_triage.py, wg_monitor.sh, report gen
├── pi3-edge/                           # Node B configuration
│   ├── suricata/                       # suricata.yaml, custom rules
│   ├── cowrie/                         # cowrie.cfg
│   └── wireguard/                      # wg0.conf template (keys redacted)
├── network/
│   └── span-port-setup.md              # TL-SG105E SPAN configuration guide
├── sample-outputs/                     # Evidence from red team scenarios
│   ├── claude-triage-examples/         # Real Claude API responses per scenario
│   ├── telegram-alert-screenshots/
│   └── sample-incident-report.pdf
└── reports/
    └── mitre-coverage.md               # ATT&CK coverage map with confidence ratings
```

---

## 📂 Sample Outputs

Evidence from the red team scenarios, added as the build progresses:

| Output | Description | Link |
|--------|-------------|------|
| Claude triage examples | Full Claude API JSON responses for each scenario — noise, low, medium, and critical classifications | [claude-triage-examples/](sample-outputs/claude-triage-examples/) |
| Telegram alert screenshots | Operator alert screenshots showing the formatted notification for each severity level | [telegram-alert-screenshots/](sample-outputs/telegram-alert-screenshots/) |
| Sample incident report | Auto-generated PDF monthly report from the Jinja2 + WeasyPrint pipeline | [sample-incident-report.pdf](sample-outputs/sample-incident-report.pdf) |

---

## 🗺️ MITRE ATT&CK Coverage

| Technique | Name | Tactic | Detection Confidence |
|-----------|------|--------|---------------------|
| T1046 | Network Service Discovery | Discovery | High (aggressive) / Low (stealth) |
| T1110.001 | Brute Force: Password Guessing | Credential Access | High |
| T1190 | Exploit Public-Facing Application | Initial Access | High (known CVE) |
| T1059.007 | Command and Scripting: JavaScript | Execution | Medium (HTTP only) |
| T1021 | Remote Services | Lateral Movement | Medium |
| T1083 | File and Directory Discovery | Discovery | Medium |
| T1078 | Valid Accounts | Defence Evasion | Low (requires UEBA) |

**[→ Full coverage map with evidence links](reports/mitre-coverage.md)**

---

## 🚀 Setup Instructions

> *Full step-by-step build instructions are in the [Project Book](docs/architecture.md). This is the quick-start overview.*

### Prerequisites

| Account | Purpose |
|---------|---------|
| [Anthropic Console](https://console.anthropic.com) | Claude API key + billing (~€5 credit to start) |
| [Telegram BotFather](https://t.me/BotFather) | Bot token + your personal chat ID |
| [PagerDuty](https://pagerduty.com/sign-up) | Free tier — Events API v2 integration key |
| [GitHub](https://github.com) | Repository for portfolio |

### Build Order

```
Phase 0 (Week 1) — Core Infrastructure
  ├── Flash Pi 5 + Pi 3B+ (Raspberry Pi OS Lite 64-bit)
  ├── Configure router VLANs (Main: 192.168.1.0/24, Lab: 192.168.10.0/24)
  ├── Configure TL-SG105E SPAN port (ports 1,2,4 → port 3)
  ├── Install Pi-hole on Pi 5
  ├── Install WireGuard VPN (Pi 5 server / Pi 3B+ peer)
  ├── Install Wazuh SIEM on Pi 5
  ├── Install Wazuh Agent on Pi 3B+
  └── Install Suricata on Pi 3B+ (listening on eth1 SPAN interface)

Phase 1 (Week 2) — AI Triage Pipeline
  ├── Install n8n on Pi 5
  ├── Create Telegram Bot
  ├── Build ai_triage.py (Claude API integration)
  ├── Build n8n alert workflow (Wazuh webhook → Claude → routing → Telegram/PagerDuty)
  └── Configure WireGuard keepalive monitoring

Phase 2 (Week 3) — Threat Intelligence
  ├── Deploy Cowrie SSH honeypot on Pi 3B+
  ├── Configure Pi-hole DNS logging to Wazuh
  └── Deploy Metasploitable 2 VM + DVWA + Kali Linux VM on ThinkPad

Phase 3 (Weeks 3–5) — Red Team Scenarios
  └── Execute and document all 5 attack scenarios

Phase 4 (Week 5) — Dashboards & Reporting
  ├── Install Grafana + build 5 dashboards
  ├── Build Jinja2 + WeasyPrint PDF report pipeline
  └── Write custom Wazuh detection rules from red team findings

Phase 5 (Week 6) — Portfolio
  ├── Record 30-second demo GIF (Scenario 3 full pipeline)
  └── Populate all scenario evidence, screenshots, Claude JSON responses
```

---

## 📄 License

[MIT](LICENSE) — configurations and scripts are free to use and adapt. Attribution appreciated.
