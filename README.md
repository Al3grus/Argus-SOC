# Argus SOC
## AI-Augmented Security Operations Center

> *Edge to cloud. Threat to response.*

**Status:** 🔨 Under active construction - Phase 0 complete, Phase 1 in progress (2026)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform: Raspberry Pi](https://img.shields.io/badge/Platform-Raspberry%20Pi-C51A4A?logo=raspberrypi&logoColor=white)](docs/hardware.md)
[![Cloud: Hetzner](https://img.shields.io/badge/Cloud-Hetzner-D50C2D?logo=hetzner&logoColor=white)](hetzner-soc/)
[![SIEM: Wazuh](https://img.shields.io/badge/SIEM-Wazuh-blue)](hetzner-soc/wazuh/)
[![NIDS: Suricata](https://img.shields.io/badge/NIDS-Suricata-orange)](pi3-edge/suricata/)
[![Protocol: Zeek](https://img.shields.io/badge/Protocol-Zeek-brightgreen)](pi3-edge/zeek/)
[![DFIR: Velociraptor](https://img.shields.io/badge/DFIR-Velociraptor-purple)](hetzner-soc/velociraptor/)
[![AI: Claude API](https://img.shields.io/badge/AI-Claude%20API-6B48FF)](hetzner-soc/scripts/)

---

A fully functional, AI-powered Security Operations Centre built on home lab hardware and a cloud-hosted central platform, designed to demonstrate hands-on proficiency across the full security kill chain: network monitoring, threat detection, AI-powered alert triage, live endpoint forensics, incident response, physical security monitoring, and automated reporting.

> **This is not a tool installation walkthrough.** Argus SOC is an operational environment where attacks are executed, detections are verified, AI classifies threats in real time, operators are alerted, and incidents are documented with evidence - including evidence of what the stack *failed* to detect.

---

## 🎬 Demo

> *Demo GIF will be added in Phase 7 once the build is complete.*  
> It will show: Kali terminal → Metasploit RCE against Metasploitable 2 on Pi 5 → Suricata alert → Wazuh dashboard (Hetzner) → Claude AI classification → Telegram notification. Full pipeline in ~30 seconds.

---

## 🏗️ Architecture - MSSP Topology

The lab uses a three-tier architecture that mirrors how Managed Security Service Providers (MSSPs) operate: a cloud-hosted central SOC platform (Hetzner), a client site with existing infrastructure and intentionally vulnerable services (Pi 5), and an MSSP-deployed edge sensor that monitors everything (Pi 3B+). The attacker (Kali on ThinkPad) operates from outside the client network on an isolated guest WiFi - exactly how a real external threat actor would.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                  HETZNER VPS - Helsinki, Finland (GDPR)                      │
│                          argus-soc · <HETZNER_IP>                            │
│                                                                              │
│   Wazuh Manager + Indexer + Dashboard (full stack, x86_64)                   │
│   n8n Workflow Engine · Velociraptor Server · Claude API Triage              │
│   Jinja2 + WeasyPrint PDF Reporting                                          │
└────────────────────────────────┬─────────────────────────────────────────────┘
                                 │ Internet
                        ┌────────┴─────────┐
                        │  Wazuh Agent     │
                        │  port 1514       │
                        │  (direct - not   │
                        │  via WireGuard)  │
                        └────────┬─────────┘
┌────────────────────────────────┼──────────────────────────────────────────────┐
│                   CLIENT SITE - 192.168.1.0/24                                │
│                                │                                              │
│   ┌────────────────────────────┴───────────────────────────────────────────┐  │
│   │          TP-Link Archer AX55 Router (192.168.1.1)                      |  |
|   └────────────────────────────┬───────────────────────────────────────────┘  |
|   ┌────────────────────────────┴───────────────────────────────────────────┐  |
│   │  Cisco SG300-10MP Managed Switch (192.168.1.2)                         │  │
│   │  GE10: router  GE5: Pi 5 | GE1: Pi 3B+(eth0) | GE2: Pi 3B+(SPAN)       │  │
│   │  SPAN: GE1+GE5+GE10 → GE2  (all directions, mirrors ALL traffic)       │  │
│   └────────────────────────┬──────────────────────┬────────────────────────┘  │
│                            │                      │                           │
│   ┌────────────────────────┴──────────┐  ┌────────┴─────────────────────┐     │
│   │  Pi 5 - argus-central             │  │  Pi 3B+ - argus-edge-01      │     │
│   │  192.168.1.10                     │  │  192.168.1.20                │     │
│   │                                   │  │                              │     │
│   │  Pi-hole DNS                      │  │  Wazuh Agent                 │     │
│   │  WireGuard VPN Server (10.0.0.1)  │  │  Suricata NIDS (eth1, SPAN)  │     │
│   │  Grafana Dashboards               │  │  Zeek Protocol Analysis      │     │
│   │  MediaMTX RTSP / Frigate NVR      │  │  Cowrie SSH Honeypot         │     │
│   │  OV5647 Camera                    │  │  Velociraptor Agent          │     │
│   │                                   │  │                              │     │
│   │  ┌─────────────────────────────┐  │  │  eth0: 192.168.1.20 (main)   │     │
│   │  │  Attack Targets (Docker)    │  │  │  eth1: SPAN, no IP, PROMISC  │     │
│   │  │  Metasploitable 2           │  │  │  (Cisco SG300 GE2)           │     │
│   │  │  DVWA                       │  │  └──────────────────────────────┘     │
│   │  └─────────────────────────────┘  │                                       │
│   └───────────────────────────────────┘                                       │
└───────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│      EXTERNAL ATTACKER - GUEST WiFi (isolated from client network)            │
│                                                                               │
│   ┌──────────────────────────────────────────────────────────────────────┐    │
│   │  Lenovo ThinkPad T480                                                │    │
│   │  Kali Linux VM - Nmap · Metasploit · Hydra · Burp Suite · SQLmap     │    │
│   │  WireGuard tunnel (10.0.0.3) for management access when needed       │    │
│   └──────────────────────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────────────────────┘
```

**[→ Full architecture documentation](docs/architecture.md)**

---

## 🖥️ Node Roles

| Node | Hardware | Role | Key Services |
|------|----------|------|--------------|
| **argus-soc** | Hetzner CX23 (2 vCPU, 4GB, x86_64, Helsinki) | MSSP Cloud SOC Platform | Wazuh Manager + Indexer + Dashboard, n8n, Velociraptor server, Claude API triage, PDF reporting |
| **argus-central** | Raspberry Pi 5 (8GB) · 192.168.1.10 | Client Infrastructure + Physical Security | Pi-hole DNS, WireGuard VPN server, Grafana, MediaMTX RTSP, Frigate NVR, OV5647 camera, Metasploitable 2 (Docker), DVWA (Docker) |
| **argus-edge-01** | Raspberry Pi 3B+ (1GB) · 192.168.1.20 | MSSP Remote Edge Sensor | Wazuh Agent, Suricata NIDS (SPAN), Zeek protocol analysis, Cowrie SSH honeypot, Velociraptor agent |
| **Red Team** | Lenovo ThinkPad T480 · GUEST WiFi | External Attacker | Kali Linux VM |

---

## ⚡ The AI Detection Loop

Every Wazuh alert above threshold flows through an automated triage pipeline on the Hetzner VPS:

```
Traffic Capture (Suricata + Zeek on SPAN interface - eth1)
       ↓
Detection Layer
  ├── Suricata: Signature matching (ET Open ruleset, 49,325 rules)
  └── Zeek: Protocol metadata (conn.log, dns.log, http.log, ssl.log)
       ↓
Log Forwarding (Wazuh Agent → Hetzner Manager - direct over internet, port 1514)
       ↓
SIEM Correlation (Wazuh: multi-source, MITRE ATT&CK mapping)
       ↓
Webhook Trigger (Wazuh → n8n at level 3+, localhost:5678)
       ↓
AI Triage (Claude API: classify severity, MITRE tag, plain-English summary)
       ↓
Severity Routing (n8n Switch node)
    ├── Noise     → Silent log
    ├── Low       → Daily digest
    ├── Medium    → Telegram alert
    └── Critical  → Telegram + PagerDuty escalation (EU: events.eu.pagerduty.com)
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

> In testing, Claude correctly classifies ~80% of ET Open rule hits as noise - transforming hundreds of daily raw alerts into ~20–40 actionable items, with critical events surfaced immediately.

---

## 📹 Physical Security Detection Path

Camera events flow through the same unified SOC pipeline as network security events:

```
OV5647 NoIR Camera (Pi 5 CSI)
       ↓
MediaMTX - RTSP :8554 / HLS :8888 / WebRTC :8889
       ↓
Frigate - AI object/motion detection (person, vehicle)
       ↓
Wazuh Agent (Pi 5) → Hetzner Manager
       ↓
n8n → Claude API → Telegram notification
       ↓
Grafana - live HLS feed embedded in SOC dashboard
```

---

## 🎯 Attack Scenarios - Detection Coverage

Five fully documented red team scenarios covering the full kill chain. Kali (ThinkPad, guest WiFi) attacks targets on Pi 5 (Metasploitable 2, DVWA via Docker) and Pi 3B+ (Cowrie honeypot). Pi 3B+ SPAN captures all traffic through the switch.

| # | Scenario | MITRE Technique | Primary Detection | Status |
|---|----------|----------------|-------------------|--------|
| [1](docs/detection-scenarios/01-reconnaissance.md) | Reconnaissance | T1046 - Network Service Discovery | Suricata ET SCAN + Zeek conn.log | 🔨 Planned |
| [2](docs/detection-scenarios/02-brute-force.md) | Credential Brute Force | T1110.001 - Password Guessing | Cowrie + Wazuh correlation | 🔨 Planned |
| [3](docs/detection-scenarios/03-exploitation.md) | Remote Code Execution | T1190 - Exploit Public-Facing App | Suricata payload signature | 🔨 Planned |
| [4](docs/detection-scenarios/04-web-attacks.md) | Web Application Attacks | T1190, T1059.007 | Suricata web rules (HTTP) | 🔨 Planned |
| [5](docs/detection-scenarios/05-lateral-movement.md) | Lateral Movement | T1021, T1083, T1078 | Wazuh + Zeek + custom rule | 🔨 Planned |

Each scenario documents: exact commands, Wazuh alert ID, Suricata SID + Zeek log entry, full Claude API JSON response, Telegram screenshot, Velociraptor VQL output where applicable, and **detection gaps with root cause analysis**.

---

## 🛠️ Tech Stack

| Layer | Tool | Why This Tool |
|-------|------|---------------|
| Cloud Platform | Hetzner CX23 (Helsinki) | GDPR-compliant, x86_64 (required for Wazuh Indexer/Dashboard), always-on, €3.62/mo |
| SIEM | Wazuh v4.14.4 | Multi-agent architecture, built-in MITRE ATT&CK mapping, ARM64 agent packages for Pi |
| NIDS | Suricata | Multi-threaded, ET Open ruleset (49,325 rules), TLS/JA3 fingerprinting, native JSON output |
| Protocol Analysis | Zeek | Protocol metadata regardless of signature matches - complements Suricata, not a replacement |
| DFIR | Velociraptor | Live endpoint forensics, VQL hunting queries, artifact collection |
| Traffic Visibility | Cisco SG300-10MP SPAN | Hardware SPAN mirrors ALL switch traffic to Pi 3B+ eth1 - GE1+GE5+GE10 → GE2 |
| AI Triage | Claude API (Anthropic) | Structured JSON classification, MITRE mapping, ~80% noise reduction |
| Workflow Engine | n8n (self-hosted, Hetzner) | Co-located with Wazuh - webhooks stay localhost. Visual automation pipeline. |
| Operator Alerting | Telegram Bot | Free, instant, clean formatting for alert data |
| Escalation | PagerDuty (EU free tier) | Auto-escalation chain on unacknowledged critical incidents - EU endpoint |
| VPN | WireGuard | Pi 5 server (10.0.0.1), Pi 3B+ peer (10.0.0.2), ThinkPad peer (10.0.0.3) |
| Honeypot | Cowrie SSH | Full attacker session logs: credentials, commands, file uploads |
| Attack Targets | Metasploitable 2 + DVWA (Docker on Pi 5) | Vulnerable services running on client infrastructure - monitored by MSSP edge sensor |
| Physical Security | MediaMTX + Frigate (Pi 5) | RTSP/HLS/WebRTC streaming + AI object detection integrated into SOC alerts |
| Dashboards | Grafana (Pi 5) | Client-facing security posture reporting, camera feed embed, Suricata/Zeek stats |
| DNS | Pi-hole v6 (Pi 5) | DNS filtering + query logging forwarded to Wazuh as telemetry |
| Reporting | Jinja2 + WeasyPrint | Auto-generated PDF incident reports from structured event data |
| Red Team | Kali Linux (ThinkPad, GUEST WiFi) | External attacker platform - isolated from client network |

**[→ Full tool selection rationale with rejected alternatives](/docs/architecture.md#tool-selection-rationale)**

---

## 📁 Repository Structure

```
argus-soc/
├── README.md
├── docs/
│   ├── architecture.md                  # Full architecture + tool rationale
│   ├── hardware.md                      # Hardware inventory, budget, memory planning
│   ├── assets/
│   │   ├── demo.gif                     # 30-second pipeline demo (Phase 7)
│   │   └── architecture.png             # Network diagram
│   └── detection-scenarios/
│       ├── 01-reconnaissance.md
│       ├── 02-brute-force.md
│       ├── 03-exploitation.md
│       ├── 04-web-attacks.md
│       └── 05-lateral-movement.md
├── hetzner-soc/                         # Cloud SOC platform configuration
│   ├── wazuh/                           # Custom rules, ossec.conf, integration config
│   ├── n8n/                             # Workflow JSON exports
│   ├── velociraptor/                    # Server config template (keys redacted)
│   └── scripts/                         # ai_triage.py, report generation
├── pi5-central/                         # Client infrastructure configuration
│   ├── pihole/                          # Allowlist, config
│   ├── wireguard/                       # wg0.conf template (keys redacted)
│   ├── grafana/                         # Dashboard JSON exports
│   └── camera/
│       ├── mediamtx/                    # mediamtx.yml
│       └── frigate/                     # config.yml
├── pi3-edge/                            # Edge sensor configuration
│   ├── suricata/                        # suricata.yaml, custom rules
│   ├── zeek/                            # node.cfg, local.zeek
│   ├── cowrie/                          # cowrie.cfg
│   ├── velociraptor/                    # Client config template
│   └── wireguard/                       # wg0.conf template (keys redacted)
├── network/
│   └── span-port-setup.md               # Cisco SG300-10MP SPAN configuration guide
├── sample-outputs/                      # Evidence from red team scenarios
│   ├── claude-triage-examples/          # Real Claude API responses per scenario
│   ├── telegram-alert-screenshots/
│   └── sample-incident-report.pdf
└── reports/
    └── mitre-coverage.md                # ATT&CK coverage map with confidence ratings
```

---

## 📂 Sample Outputs

Evidence from the red team scenarios, added as the build progresses:

| Output | Description | Link |
|--------|-------------|------|
| Claude triage examples | Full Claude API JSON responses for each scenario - noise, low, medium, and critical classifications | [claude-triage-examples/](sample-outputs/claude-triage-examples/) |
| Telegram alert screenshots | Operator alert screenshots showing the formatted notification for each severity level | [telegram-alert-screenshots/](sample-outputs/telegram-alert-screenshots/) |
| Sample incident report | Auto-generated PDF monthly report from the Jinja2 + WeasyPrint pipeline | [sample-incident-report.pdf](sample-outputs/sample-incident-report.pdf) |

---

## 🗺️ MITRE ATT&CK Coverage

| Technique | Name | Tactic | Primary Detection | Confidence |
|-----------|------|--------|-------------------|------------|
| T1046 | Network Service Discovery | Discovery | Suricata ET SCAN + Zeek conn.log | High (aggressive) / Low (stealth) |
| T1110.001 | Brute Force: Password Guessing | Credential Access | Cowrie + Wazuh | High |
| T1190 | Exploit Public-Facing Application | Initial Access | Suricata payload signature | High (known CVE) |
| T1059.007 | Command and Scripting: JavaScript | Execution | Suricata web rules (HTTP only) | Medium |
| T1021 | Remote Services | Lateral Movement | Wazuh + Zeek + custom rule | Medium |
| T1083 | File and Directory Discovery | Discovery | Velociraptor VQL + Wazuh FIM | Medium |
| T1078 | Valid Accounts | Defence Evasion | Wazuh custom rule (anomalous auth) | Low (requires UEBA for High) |

**[→ Full coverage map with evidence links](reports/mitre-coverage.md)**

---

## 🚀 Build Progress

| Phase | Description | Status |
|-------|-------------|--------|
| **Phase 0** | Core Infrastructure - Pi 5, Pi 3B+, Hetzner VPS, Wazuh, WireGuard, Pi-hole, Cisco SG300 SPAN | ✅ Complete |
| **Phase 1** | AI Triage Pipeline - n8n, Claude API, Telegram Bot, PagerDuty | ✅ Complete |
| **Phase 2** | Network Detection, Threat Intel, Honeypot - Suricata, Zeek, Cowrie, attack targets | ✅ Complete |
| **Phase 3** | Pre-Attack Setup — Velociraptor, Grafana dashboards | ✅ Complete |
| **Phase 4** | Red Team Attack Scenarios — 5 documented scenarios, full kill chain | 🔄 In Progress |
| **Phase 5** | Detection Engineering + Reporting — custom rules, PDF reports | ⏳ Pending |
| **Phase 6** | Physical Security — Camera stack, Frigate, SOC integration | ⏳ Pending |
| **Phase 7** | Polish, Portfolio, GitHub — Demo GIF, scenario evidence, sample outputs | ⏳ Pending |

---

## 🔧 Setup Overview

> *Full step-by-step instructions are in the Project Book. This is the build order summary.*

```
Phase 0 - Core Infrastructure
  [x] Flash Pi 5 (argus-central) + Pi 3B+ (argus-edge-01)
  [x] Configure router DHCP - single subnet 192.168.1.0/24
  [x] Configure Cisco SG300-10MP - SPAN (GE1+GE5+GE10 → GE2)
  [x] Install Pi-hole v6 on Pi 5
  [x] Install WireGuard VPN (Pi 5 server / Pi 3B+ peer / ThinkPad peer)
  [x] Deploy Hetzner CX23 VPS (Helsinki) - install full Wazuh stack v4.14.4
  [x] Install Wazuh Agent on Pi 3B+ → register with Hetzner manager (Active)
  [x] Install Suricata on Pi 3B+ (eth1 SPAN, ET Open ruleset)
  [x] Install Zeek on Pi 3B+ (eth1 SPAN, JSON logs to Wazuh)
  [x] Deploy Metasploitable 2 + DVWA Docker containers on Pi 5

Phase 1 - AI Triage Pipeline
  [x] Install n8n on Hetzner (co-located with Wazuh, port 5678)
  [x] Build ai_triage.py (Claude API structured prompting) - tested
  [x] Configure Telegram Bot + PagerDuty EU instance
  [x] Build n8n alert workflow (Wazuh webhook → Claude → routing → Telegram/PagerDuty)
  [x] Configure Wazuh webhook integration in ossec.conf

Phase 2 - Threat Intel + Honeypot
  [x] Deploy Cowrie SSH honeypot on Pi 3B+
  [x] Configure Kali Linux VM on ThinkPad

Phase 3 - Pre-Attack Setup
  [x] Deploy Velociraptor server (Hetzner) + agent (Pi 3B+)
  [x] Install Grafana on Pi 5 + build dashboards

Phase 4 - Red Team Scenarios
  [ ] Execute and document all 5 attack scenarios with full evidence

Phase 5 - Detection Engineering + Reporting
  [ ] Write custom Wazuh detection rules from red team findings
  [ ] Build Jinja2 + WeasyPrint PDF report pipeline
  [ ] Generate sample incident report from scenario data

Phase 6 - Physical Security
  [ ] Configure Frigate AI detection (pulling from MediaMTX RTSP)
  [ ] Integrate Frigate events → Wazuh Agent (Pi 5) → Hetzner
  [ ] Embed HLS feed in Grafana SOC dashboard

Phase 7 - Portfolio
  [ ] Record 30-second demo GIF (Scenario 3 full pipeline)
  [ ] Populate all scenario evidence, screenshots, Claude JSON responses
```

---

## 📝 Build Blog

Each phase is documented as it completes at **[al3grus.github.io](https://al3grus.github.io)** - including real-world complications, troubleshooting, and lessons learned.

---

## ⚠️ Disclaimer

All work uses sanitised data in controlled lab environments. No unauthorised access or testing of real systems.

---

## 📄 License

[MIT](LICENSE) - configurations and scripts are free to use and adapt. Attribution appreciated.

---
