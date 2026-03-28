# Pi-hole DNS — Pi 5 (argus-central)

Pi-hole v6 serves as DNS resolver for the entire client site. Provides DNS filtering and query logging as a telemetry source forwarded to Wazuh.

## Access

```
http://192.168.1.10/admin
```

## Configuration

- **Upstream DNS:** Cloudflare (1.1.1.1, 1.0.0.1)
- **Interface:** eth0 (192.168.1.10)
- **Listening mode:** All interfaces

## Required Allowlist

The following domains must be whitelisted or Pi-hole will block essential project services:

```bash
sudo pihole allow api.anthropic.com          # Claude API
sudo pihole allow api.telegram.org           # Telegram Bot
sudo pihole allow app.pagerduty.com          # PagerDuty UI
sudo pihole allow events.eu.pagerduty.com    # PagerDuty EU alerts endpoint
sudo pihole allow packages.wazuh.com         # Wazuh packages
sudo pihole allow raw.githubusercontent.com
sudo pihole allow github.com
sudo pihole allow deb.nodesource.com         # Node.js packages (n8n)
```

> **Note:** Pi-hole v6 uses `pihole allow` not `pihole -w`. If the CLI fails due to known v6 bugs, use the web UI: Domains → Add to allowed domains.

## DNS as Telemetry

Pi-hole query logs are forwarded to Wazuh Agent on Pi 5, then to Hetzner Wazuh Manager. Suspicious DNS queries (C2 domains, DGA patterns, high-risk TLDs) trigger custom Wazuh rule 100006.

Pi-hole log location: `/var/log/pihole/pihole.log`

Wazuh Agent config entry (in `/var/ossec/etc/ossec.conf` on Pi 5):
```xml
<localfile>
  <log_format>syslog</log_format>
  <location>/var/log/pihole/pihole.log</location>
</localfile>
```

## Router DHCP Configuration

Set router Primary DNS to `192.168.1.10` so all network clients use Pi-hole automatically. This means every DNS query from every device on the network becomes a telemetry data point.
