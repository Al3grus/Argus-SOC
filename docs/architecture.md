# Architecture — Argus SOC

## Overview

Argus SOC uses a **two-node architecture** connected over a WireGuard VPN tunnel. The design deliberately mirrors how Managed Security Service Providers (MSSPs) and MDR providers operate: a central SOC platform receives telemetry from remote edge sensors deployed at client sites over encrypted backhaul.

- **Pi 5 = Central SOC platform** (Wazuh Manager, AI triage, dashboards, orchestration)
- **Pi 3B+ = Remote edge sensor** (Wazuh Agent, Suricata NIDS, Cowrie honeypot)
- **WireGuard VPN = Encrypted backhaul** (mirrors MSSP client-site-to-SOC tunnel)

Running everything on a single Pi would be technically possible but would fail to demonstrate the MSSP topology pattern that makes this project portfolio-grade.

---

## Network Segmentation

| VLAN | Name | Subnet | Hosts | Purpose |
|------|------|--------|-------|---------|
| VLAN 1 | Main | 192.168.1.0/24 | Pi 5 (192.168.1.10), ThinkPad | Management network. SOC platform, red team workstation. |
| VLAN 10 | Lab | 192.168.10.0/24 | Pi 3B+ (192.168.10.20), Metasploitable 2, DVWA | Attack surface. All vulnerable targets and the edge sensor. |
| VLAN 20 | IoT | 192.168.20.0/24 | (future) | Isolated segment for untrusted devices. |

---

## SPAN Port Architecture

The TL-SG105E managed switch sits between the router and the Lab VLAN. Its SPAN port mirrors **all traffic on Lab VLAN ports** to the Pi 3B+ monitoring interface (`eth1`, USB ethernet adapter, promiscuous mode, no IP address).

**Why this matters:** Without a SPAN port, Suricata only sees traffic addressed to the Pi 3B+ itself. With SPAN, Suricata sees ALL traffic between ALL Lab VLAN hosts — including Kali-to-Metasploitable traffic that never touches the Pi. This is how every enterprise SOC deploys network monitoring.

### Physical Cabling

```
Switch Port 1 ←→ Router (Lab VLAN uplink)
Switch Port 2 ←→ Pi 3B+ eth0 (192.168.10.20, normal connectivity)
Switch Port 3 ←→ Pi 3B+ eth1 / USB adapter (SPAN destination, NO IP, promiscuous)
Switch Port 4 ←→ ThinkPad (Metasploitable/DVWA traffic on Lab VLAN)
Switch Port 5 ←→ Spare
```

**Mirror config:** Source ports 1, 2, 4 (both directions) → Destination port 3.

---

## WireGuard VPN

| Endpoint | IP | Role |
|----------|----|------|
| Pi 5 | 10.0.0.1/24 | VPN Server, listens on UDP 51820 |
| Pi 3B+ | 10.0.0.2/24 | VPN Peer, connects to Pi 5 endpoint |

All Wazuh Agent-to-Manager communication uses the WireGuard tunnel IPs (`10.0.0.1`), not LAN IPs. PersistentKeepalive (25s) enables offline node detection — if the tunnel drops, the WireGuard monitor script fires a Critical alert.

---

## Data Flow — Security Event Lifecycle

```
1. TRAFFIC CAPTURE
   Suricata on Pi 3B+ monitors eth1 (SPAN-mirrored interface)
   Sees ALL Lab VLAN traffic — not just traffic addressed to the Pi

2. SIGNATURE DETECTION
   ET Open community ruleset (~40,000 rules)
   Rule match → JSON alert written to /var/log/suricata/eve.json

3. LOG FORWARDING
   Wazuh Agent reads eve.json in real time
   Forwards to Wazuh Manager on Pi 5 via WireGuard tunnel (port 1514, encrypted)

4. SIEM CORRELATION
   Wazuh Manager correlates with: host logs, FIM events, Pi-hole DNS, Cowrie events
   Multi-source correlation is a core SIEM function

5. WEBHOOK TRIGGER
   Alert level ≥ 3 → Wazuh fires webhook to n8n (http://localhost:5678/webhook/wazuh-alert)

6. AI TRIAGE
   n8n routes raw alert JSON to Claude API
   Claude returns: severity, plain-English summary, MITRE technique, recommended action, confidence

7. SEVERITY ROUTING
   n8n Switch node routes by Claude's classification:
   Noise → silent log | Low → daily digest | Medium → Telegram | Critical → Telegram + PagerDuty

8. OPERATOR ALERT
   Telegram Bot: severity emoji, Claude summary, IPs, Suricata SID, MITRE, Wazuh dashboard link

9. ESCALATION (Critical only)
   PagerDuty: push + email + SMS
   Unacknowledged within 5 min → phone call → secondary contact

10. LOGGING & REPORTING
    n8n logs all events to structured JSONL
    Monthly: Jinja2 + WeasyPrint generates PDF incident report
```

---

## Tool Selection Rationale

### SIEM — Wazuh (over Splunk / Elastic)

- **Splunk rejected:** $150+/GB/day licensing eliminates it at any scale.
- **Elastic SIEM rejected:** 8–16GB RAM minimum for Elasticsearch — impossible on Pi hardware.
- **Wazuh chosen:** Purpose-built manager+agent architecture for multi-node deployments. Built-in MITRE ATT&CK mapping, FIM, GDPR modules. Free and open source.

### NIDS — Suricata (over Snort / Zeek)

- **Snort rejected:** Single-threaded, lower performance on modern benchmarks.
- **Zeek noted:** Protocol analysis (metadata) rather than signature matching — complementary, not a replacement. Planned Phase 6+ addition.
- **Suricata chosen:** Multi-threaded, ET Open ruleset, TLS/JA3 fingerprinting, real-time JSON alert output natively parsed by Wazuh.

### AI Triage — Claude API (over local LLMs / GPT-4)

- **Local LLMs (Ollama/llama.cpp) rejected:** Insufficient structured classification quality at 7B parameter models that fit on Pi.
- **LangChain rejected:** Unnecessary abstraction for single-step API calls.
- **GPT-4 evaluated:** Comparable quality, higher cost per token.
- **Claude chosen:** Reliable structured JSON output, cost-effective (~€5–10/month at homelab scale), consistent MITRE mapping.

### Workflow Engine — n8n (over custom Python)

- **Custom Python scripts rejected:** Harder to maintain and debug. No visual workflow for portfolio demonstration — non-technical reviewers cannot understand a Python script at a glance.
- **n8n chosen:** Visual workflows immediately understandable. Connects Wazuh webhooks, Claude API, Telegram, PagerDuty into maintainable pipelines. Self-hosted on Pi 5.

### VPN — WireGuard (over OpenVPN / Tailscale)

- **OpenVPN rejected:** Heavier, user-space, more complex configuration.
- **Tailscale rejected:** Hides the VPN mechanics you want to demonstrate. Abstraction works against portfolio goals.
- **WireGuard chosen:** Kernel-level, minimal attack surface, simple configuration. Keepalive enables offline node detection.

### Honeypot — Cowrie (over Kippo / Honeyd)

- **Kippo rejected:** Deprecated; Cowrie is the maintained successor.
- **Honeyd rejected:** Lower fidelity, no interactive shell simulation.
- **Cowrie chosen:** Full attacker session logs — commands, keystrokes, file uploads. Masquerades as real OpenSSH. Logs forward to Wazuh for correlation.

---

## Phase Roadmap

| Phase | Focus | Timeline |
|-------|-------|----------|
| Phase 0 | Core Infrastructure | Week 1 |
| Phase 1 | AI Triage Pipeline + Alerting | Week 2 |
| Phase 2 | Threat Intelligence + Honeypot | Week 3 |
| Phase 3 | Red Team Attack Scenarios | Weeks 3–5 |
| Phase 4 | Dashboards, Reporting, Automation | Week 5 |
| Phase 5 | Polish, Portfolio, GitHub | Week 6 |
| Phase 6+ | Physical security, Zeek, cloud migration | Future |

---

## Future — Phase 6+ Roadmap

- **Phase 6:** Physical security layer — RTSP cameras, Frigate NVR, MQTT events into n8n
- **Phase 7:** Zeek alongside Suricata for protocol metadata; VirusTotal IoC enrichment; YARA rules
- **Phase 8:** Migrate Pi 5 to Hetzner CX22 VPS for cloud SOC skills; deploy additional Pi Zero 2W edge sensors
- **Phase 9:** Agentic Claude — query threat intel, check host history, draft response playbooks automatically
- **Phase 10:** Wireless attack scenarios (Alfa AWUS036ACH, Aircrack-ng); supply chain / malicious file scenarios
