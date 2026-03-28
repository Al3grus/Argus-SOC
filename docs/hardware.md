# Hardware Inventory and Purpose

Every piece of hardware serves a specific, documented purpose. Nothing is included for decoration.

---

## Devices

| Device | Role | Specifications | Why It Is Needed |
|--------|------|---------------|-----------------|
| **Hetzner CX23 VPS** | Cloud SOC Platform | 2 vCPU x86_64, 4GB RAM, 40GB SSD, Ubuntu 24.04, Helsinki | Full Wazuh stack (Indexer + Dashboard require x86_64), n8n, Velociraptor. GDPR-compliant. Always-on regardless of home network state. |
| **Raspberry Pi 5 (8GB)** | Client Infrastructure + Physical Security | 8GB RAM, quad-core Cortex-A76, 128GB microSD, Raspberry Pi OS Bookworm, wired ethernet | Pi-hole DNS, WireGuard VPN server, Grafana, MediaMTX, Frigate NVR, OV5647 camera, Metasploitable 2 + DVWA Docker containers. 8GB comfortably hosts all services. |
| **Raspberry Pi 3B+** | MSSP Remote Edge Sensor | 1GB RAM, quad-core Cortex-A53 1.4GHz, 128GB microSD, Pi OS Lite 64-bit, vented aluminium case, wired ethernet | Wazuh Agent, Suricata NIDS, Zeek, Cowrie honeypot, Velociraptor agent. 1GB RAM is tight but sufficient — tuning under constraint is a real operational skill. |
| **Cisco SG300-10MP** | Managed Switch / SPAN | 10-port gigabit PoE managed switch, full 802.1Q VLAN support, SPAN/RSPAN | SPAN port mirrors ALL switch traffic to Pi 3B+ monitoring interface. Without this, Suricata and Zeek only see traffic addressed to the Pi itself — the most common homelab NIDS mistake. |
| **TP-Link Archer AX55** | Home Router | Wi-Fi 6, AX3000 | Main subnet (192.168.1.0/24) routing and DHCP. Does NOT support 802.1Q LAN VLANs — flat subnet used instead. |
| **USB Ethernet Adapter** | SPAN Interface for Pi 3B+ | Any USB 2.0/3.0 to RJ45 | Pi 3B+ has only one built-in NIC. USB adapter provides eth1 dedicated exclusively to SPAN mirror traffic — promiscuous mode, no IP address assigned. |
| **OV5647 NoIR Camera** | Physical Security Camera | 5MP, CSI interface, no infrared filter | Video feed for Frigate AI detection. NoIR enables better low-light performance. CSI ribbon connects to Pi 5. |
| **Lenovo ThinkPad T480** | Red Team Workstation | i5-8350U, 24GB RAM, 512GB SSD, VMware Workstation | Hosts Kali Linux VM. Operates from guest WiFi (isolated from client network). Never runs defensive tools. |
| **Alert Phone** | Operator Alert Receiver | Any phone with Telegram installed | Receives real-time Telegram Bot notifications with AI-classified alerts, severity, and Wazuh dashboard links. |

---

## Hardware Budget

| Item | Estimated Cost (EUR) | Required? |
|------|---------------------|-----------|
| Raspberry Pi 5 (8GB) + PSU + SD card | €95–120 | Yes |
| Raspberry Pi 3B+ + PSU + SD card + case | €35–55 | Yes |
| USB Ethernet Adapter | €10–15 | Yes |
| OV5647 NoIR Camera | €15–25 | Yes (Phase 6) |
| Ethernet cables (x4) | €10–15 | Yes |
| Hetzner CX23 VPS | €3.62/month | Yes (ongoing) |
| Cisco SG300-10MP | €0–60 (secondhand) | Yes |
| TP-Link Archer AX55 router | €70–90 | If no existing router |
| **Total hardware** | **€165–330** | |
| **Total monthly** | **€3.62/mo** | |

> The Cisco SG300-10MP used in this build was borrowed. Secondhand units are commonly available for €20–40. Any managed switch with SPAN capability works — the SG300 exceeds the minimum requirement.

---

## Monthly Operating Costs

| Service | Cost | Notes |
|---------|------|-------|
| Hetzner CX23 VPS | €3.62/month | Central SOC platform |
| Anthropic API (Claude) | €5–10/month | ~500–1000 triage calls/month at homelab scale |
| PagerDuty | Free | Free tier: 1 user, 1 service, unlimited incidents |
| Telegram Bot | Free | No rate limits for personal bots |
| Electricity (2x Pi + switch + router) | €3–5/month | ~25W continuous draw |
| GitHub | Free | Public repository |
| **Total** | **€11.62–18.62/month** | |

---

## Physical Cabling

```
Internet
    │
TP-Link Archer AX55 (192.168.1.1)
    │
    └── Cisco SG300-10MP (192.168.1.2)
         ├── GE1  ←→ Pi 3B+ eth0 (192.168.1.20)
         ├── GE2  ←→ Pi 3B+ eth1 USB adapter (SPAN destination — NO IP)
         ├── GE5  ←→ Pi 5 eth0 (192.168.1.10)
         └── GE10 ←→ Router LAN port (uplink)
```

Pi 5 connects to the switch (GE5), not directly to the router. All devices share the same 192.168.1.0/24 subnet via the switch uplink (GE10 → Router).

---

## Notes on the Pi 3B+ USB Adapter

The bottom USB ports on the Pi 3B+ may fail to enumerate USB ethernet adapters (`error -32: device not accepting address`). If this happens, move to a top USB port before concluding the adapter is faulty — this resolved the issue in this build immediately.

Verify the adapter is detected and in promiscuous mode:

```bash
ip link show eth1
# Expected: <BROADCAST,MULTICAST,PROMISC,UP,LOWER_UP>
```
