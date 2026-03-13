# SPAN Port Configuration — TP-Link TL-SG105E

The SPAN (Switched Port Analyser) port is the single most important hardware configuration in the entire build. Without it, Suricata only sees traffic addressed to the Pi 3B+ itself — not traffic between other Lab VLAN hosts.

## Why SPAN Matters

```
Without SPAN:                          With SPAN:
                                       
Kali ──→ Metasploitable               Kali ──→ Metasploitable
              (Pi 3B+ sees nothing)          ↓ (copy)
                                       Pi 3B+ eth1
                                       Suricata sees ALL traffic
```

## Physical Cabling

```
Switch Port 1 ←→ Router (Lab VLAN uplink)
Switch Port 2 ←→ Pi 3B+ eth0 / built-in NIC (192.168.10.20)
Switch Port 3 ←→ Pi 3B+ eth1 / USB ethernet adapter (SPAN destination, NO IP)
Switch Port 4 ←→ ThinkPad (bridged to Lab VLAN for VMs)
Switch Port 5 ←→ (spare)
```

## TL-SG105E Configuration

1. Connect ThinkPad directly to the switch with an ethernet cable
2. Temporarily set ThinkPad to a 192.168.0.x address
3. Open browser → `http://192.168.0.1` (default switch IP)
4. Login: `admin` / `admin` (change immediately)
5. Change switch management IP to `192.168.10.254`
6. Navigate: **Monitoring → Port Mirror**
7. Configure:
   - **Mirror Source Ports:** 1, 2, 4
   - **Mirror Destination Port:** 3
   - **Direction:** Both (Ingress + Egress)
8. Enable and save

> ⚠️ **Warning:** Port 3 (SPAN destination) becomes a mirror-only port. Do NOT assign it an IP address or route management traffic through it.

## Pi 3B+ Interface Configuration

```bash
# Identify the USB ethernet adapter:
ip link show
# Look for eth1 or enx<mac> — this is the USB adapter

# Set promiscuous mode, no IP:
sudo ip link set eth1 promisc on
sudo ip link set eth1 up

# Make persistent:
sudo nano /etc/networkd-dispatcher/routable.d/50-span-promisc.sh
#!/bin/bash
ip link set eth1 promisc on

sudo chmod +x /etc/networkd-dispatcher/routable.d/50-span-promisc.sh
```

## Verification

```bash
# From another Lab VLAN host (ThinkPad), ping Metasploitable:
ping 192.168.10.x

# On Pi 3B+, verify Suricata sees this traffic:
sudo tcpdump -i eth1 -c 20 host 192.168.10.x

# You MUST see ICMP packets between ThinkPad and the target
# If you only see Pi 3B+'s own traffic, SPAN is not working
```

**If SPAN is not working:**
1. Verify TL-SG105E mirror config (source ports include the correct ports)
2. Verify eth1 is the USB adapter (not built-in) — check MAC addresses
3. Verify eth1 is UP and PROMISC: `ip link show eth1` must show `PROMISC` flag
