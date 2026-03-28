# SPAN Port Setup — Cisco SG300-10MP

## Why SPAN Matters

Without a SPAN port, Suricata and Zeek only see traffic **addressed to the Pi 3B+ itself** — not traffic between Metasploitable, Kali, DVWA, and Pi 5. With SPAN, both tools see **ALL traffic between ALL devices on the switch**, including lateral movement between hosts that never involves the Pi 3B+ directly. This is how every enterprise SOC deploys network monitoring.

## Physical Cabling

| Switch Port | Connection | Purpose |
|-------------|-----------|---------|
| GE1 | Pi 3B+ eth0 (192.168.1.20) | Normal network connectivity |
| GE2 | Pi 3B+ eth1 (USB ethernet adapter) | SPAN mirror destination — NO IP, promiscuous mode |
| GE5 | Pi 5 (192.168.1.10) | Client infrastructure |
| GE10 | Router LAN port | Internet uplink |

## Cisco SG300-10MP Web UI Configuration

### Access the Switch

1. Browse to `http://192.168.1.2` (static management IP)
2. Login: username `cisco`, password `<your password>`

### SPAN Port Mirroring

Navigate to **Administration → Diagnostics → Port and VLAN Mirroring**

Click **Add** and create one entry per source port:

| Destination Port | Source Interface | Type |
|-----------------|-----------------|------|
| GE2 | GE1 | Tx and Rx |
| GE2 | GE5 | Tx and Rx |
| GE2 | GE10 | Tx and Rx |

Each source port must be a separate entry. GE2 is the destination (Pi 3B+ eth1). GE1, GE5, and GE10 are the sources.

### Disable Spanning Tree Protocol

STP generates constant BPDU frames that appear as noise in SPAN captures.

Navigate to **Spanning Tree → STP Status & Global Settings** → uncheck **Enable STP** → Apply.

### Save Configuration

After all changes: **Administration → File Management → Copy/Save Configuration**

- Source: Running configuration
- Destination: Startup configuration
- Click Apply

Without this step, all configuration is lost on reboot.

---

## Pi 3B+ SPAN Interface Setup

### Make eth1 Promiscuous

```bash
sudo ip link set eth1 promisc on
sudo ip link set eth1 up
```

### Make Persistent on Boot

```bash
# Create systemd service
sudo nano /etc/systemd/system/span-promisc.service
```

```ini
[Unit]
Description=Set eth1 promiscuous mode for SPAN interface
After=network.target

[Service]
Type=oneshot
ExecStart=/sbin/ip link set eth1 promisc on
ExecStart=/sbin/ip link set eth1 up
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable span-promisc
sudo systemctl start span-promisc
```

### Verify

```bash
ip link show eth1
# Should show: <BROADCAST,MULTICAST,PROMISC,UP,LOWER_UP>
```

---

## SPAN Verification

This is the most critical verification in Phase 0. If SPAN is not working, the entire NIDS deployment is blind.

```bash
# On Pi 3B+, capture traffic from another device on the network:
sudo tcpdump -i eth1 -c 20 -n

# While capturing, ping Pi 5 from the ThinkPad:
# ping 192.168.1.10

# You MUST see ICMP packets between ThinkPad and Pi 5 in the tcpdump output.
# If you only see Pi 3B+'s own traffic, SPAN is not working.
```

Expected output includes packets between other hosts:
```
IP 192.168.1.197 > 192.168.1.10: ICMP echo request
IP 192.168.1.10 > 192.168.1.197: ICMP echo reply
```

### Troubleshooting

1. Verify GE2 is the SPAN destination and GE1/GE5/GE10 are sources in the switch UI
2. Verify eth1 is the USB adapter, not the built-in eth0 (`ip link show`)
3. Verify eth1 shows PROMISC flag
4. Check the USB adapter is in a working USB port (top ports on Pi 3B+ are more reliable)
5. Save running config to startup config — reboot clears unsaved config
