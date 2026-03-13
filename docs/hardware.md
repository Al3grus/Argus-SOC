# Hardware Inventory

Every piece of hardware serves a specific, documented purpose.

## Devices

| Device | Role | Specifications | Why It's Needed |
|--------|------|----------------|-----------------|
| **Raspberry Pi 5 (8GB)** | Central SOC Server (Node A) | 8GB RAM, quad-core Cortex-A76, 128GB A2 microSD, Debian 12 Bookworm, wired ethernet | Runs Wazuh Manager + Indexer + Dashboard, n8n, Grafana, Claude API integration, WireGuard VPN server, Pi-hole DNS. 8GB RAM is the minimum for Wazuh Indexer (OpenSearch) + all supporting services. |
| **Raspberry Pi 3B+** | Edge Sensor (Node B) | 1GB RAM, quad-core Cortex-A53 1.4GHz, 128GB microSD, Pi OS Lite 64-bit, vented aluminium case | Runs Wazuh Agent, Suricata NIDS, Cowrie honeypot. Simulates a remote client site sensor. 1GB constraint forces real memory management — an operational skill. |
| **TP-Link TL-SG105E** | Network Traffic Visibility | 5-port managed gigabit switch with SPAN/port mirroring | SPAN port mirrors ALL Lab VLAN traffic to Pi 3B+ monitoring interface. Without this, Suricata only sees traffic addressed to the Pi itself — the most common homelab SOC mistake. |
| **Lenovo ThinkPad T480** | Red Team Workstation | i5-8350U, 24GB RAM, 512GB SSD, VMware Workstation | Hosts Kali Linux VM (attack platform), Metasploitable 2 VM (exploitation target), DVWA Docker container (web attack target). |
| **USB Ethernet Adapter** | SPAN Interface for Pi 3B+ | Any USB 2.0/3.0 to RJ45 | Pi 3B+ has only one built-in NIC. The USB adapter provides a second interface dedicated to SPAN mirror traffic in promiscuous mode. |
| **TP-Link Archer AX55** | Home Network Router | Wi-Fi 6, AX3000, VLAN support | Provides VLAN segmentation (Main, Lab, IoT). DHCP, inter-VLAN routing control, upstream connectivity. |
| **OnePlus 6 (or any phone)** | Alert Receiver | Telegram installed | Receives real-time Telegram Bot notifications: AI-classified alerts with severity, summary, and Wazuh dashboard links. |

## Estimated Budget

| Item | Est. Cost (EUR) | Required? |
|------|-----------------|-----------|
| Raspberry Pi 5 (8GB) + PSU + SD card | €95–120 | ✅ Yes |
| Raspberry Pi 3B+ + PSU + SD card + case | €35–55 | ✅ Yes |
| TP-Link TL-SG105E managed switch | €25–35 | ✅ Yes |
| USB Ethernet Adapter | €10–15 | ✅ Yes |
| Ethernet cables (×4) | €10–15 | ✅ Yes |
| TP-Link Archer AX55 router | €70–90 | If no VLAN-capable router |
| Alfa AWUS036ACH (wireless, Phase 6+) | €40–55 | ❌ No (future) |
| **TOTAL (minimum required)** | **€175–240** | |

## Memory Planning

Memory is the critical constraint on Pi 3B+ (1GB). Plan before deploying.

### Pi 5 (8GB) — Node A

| Service | Est. RAM | Tuning Notes |
|---------|----------|--------------|
| Wazuh Indexer (OpenSearch) | 1.0–1.5 GB | JVM heap: `-Xms1g -Xmx1g` in jvm.options |
| Wazuh Manager | 300–500 MB | Scales with agent count |
| Wazuh Dashboard | 300–500 MB | Chromium-based backend |
| n8n | 200–400 MB | SQLite mode, not PostgreSQL |
| Grafana | 150–250 MB | Stop when not actively viewing |
| Pi-hole + WireGuard + OS | 200–300 MB | Very lightweight |
| **TOTAL** | **2.2–3.5 GB** | Comfortable within 8GB |

### Pi 3B+ (1GB) — Node B

| Service | Est. RAM | Tuning Notes |
|---------|----------|--------------|
| Wazuh Agent | 50–80 MB | Lightweight agent process |
| Suricata | 200–350 MB | `stream.memcap=32mb`, `flow.memcap=32mb` |
| Cowrie | 50–80 MB | Python-based, lightweight |
| WireGuard + OS | 150–200 MB | Kernel module, minimal overhead |
| **TOTAL** | **450–710 MB** | Fits in 1GB with ~300–550MB margin |

> **⚠ Critical:** Monitor with `htop` continuously during build. If Pi 3B+ approaches 900MB, something is misconfigured. Most common culprit: Suricata with default `memcap` settings (256MB each for stream and flow).
