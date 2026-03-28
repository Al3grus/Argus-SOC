# Velociraptor DFIR — Hetzner VPS

Velociraptor provides live endpoint forensics, artifact collection, and threat hunting capabilities. Server runs on Hetzner alongside Wazuh. Agent runs on Pi 3B+ (argus-edge-01).

## Access

```
https://<HETZNER_IP>:8889
```

## Installation

### Server (Hetzner VPS)

```bash
wget https://github.com/Velocidex/velociraptor/releases/latest/download/velociraptor-linux-amd64
chmod +x velociraptor-linux-amd64

# Generate server config interactively:
./velociraptor-linux-amd64 config generate -i
# Set bind address to 0.0.0.0:8889

# Create and install Debian package:
./velociraptor-linux-amd64 --config server.config.yaml debian server
sudo dpkg -i velociraptor_server*.deb
sudo systemctl enable velociraptor_server && sudo systemctl start velociraptor_server
```

### Agent (Pi 3B+)

```bash
# On Hetzner — generate client package:
./velociraptor-linux-amd64 --config server.config.yaml config client > client.config.yaml
./velociraptor-linux-amd64 --config server.config.yaml debian client

# Copy to Pi 3B+ and install:
scp velociraptor_client*.deb pi@192.168.1.20:/tmp/
# On Pi 3B+:
sudo dpkg -i /tmp/velociraptor_client*.deb
sudo systemctl enable velociraptor_client && sudo systemctl start velociraptor_client
```

## Key VQL Queries for Argus SOC Scenarios

| Use Case | VQL | Scenario |
|----------|-----|----------|
| Live process inspection | `SELECT * FROM pslist()` | Scenario 3 — post-exploitation |
| Network connections | `SELECT * FROM netstat()` | All scenarios |
| File system changes in /tmp | `SELECT * FROM glob(globs='/tmp/*')` | Scenario 3, 5 |
| Scheduled tasks | `SELECT * FROM cron()` | Persistence detection |
| Bash history | `SELECT * FROM glob(globs='/home/*/.bash_history')` | Scenario 5 |
| Login history | `SELECT * FROM last()` | Scenario 2, 5 |
| Running services | `SELECT * FROM services()` | Scenario 3 |

## Correlation with Network Events

Velociraptor endpoint timeline correlates with:
- Suricata `eve.json` — network-layer detection timestamps
- Zeek `conn.log` — connection metadata
- Wazuh alerts — SIEM correlation events

This three-way correlation gives complete incident reconstruction that no single tool alone provides.

## Security Note

Server config file (`server.config.yaml`) contains TLS certificates and admin credentials. **Never commit this file to the repository.** The `server.config.yaml` template in this directory has all sensitive values replaced with `<PLACEHOLDER>`.
