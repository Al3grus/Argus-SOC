# Grafana Dashboards — Pi 5 (argus-central)

Grafana provides client-facing security posture reporting. It is separate from the Wazuh Dashboard (ops-facing) — Grafana is the "client reporting" layer, showing what the client's security posture looks like over time.

## Access

```
http://192.168.1.10:3000
```

Default credentials on first install: `admin` / `admin` — change immediately.

## Data Source

Connect Grafana to the Wazuh Indexer on Hetzner:

- **Type:** OpenSearch
- **URL:** `https://<HETZNER_IP>:9200`
- **Auth:** Basic — username: `kibanaserver`, password: from wazuh-passwords.txt
- **TLS:** Skip certificate verification (self-signed cert)

## Planned Dashboards

Dashboard JSON exports go in this directory once built in Phase 3.

| Dashboard | File | Audience | Key Panels |
|-----------|------|----------|------------|
| SOC Operations | `soc-operations.json` | SOC Analyst | Alert timeline, severity distribution, top source IPs, active agents |
| MITRE ATT&CK Heatmap | `mitre-heatmap.json` | SOC Analyst / Portfolio | ATT&CK matrix with technique coverage |
| Network Threat Intel | `network-threat-intel.json` | SOC Analyst | Suricata/Zeek rule hits, top signatures, traffic volume |
| Client Security Posture | `client-posture.json` | Simulated MSSP client | Alert trend, mean time to detect, severity breakdown |
| Camera + Physical Security | `camera-physical.json` | SOC Analyst | Live HLS feed, Frigate event count, motion alert timeline |

## Camera Feed Panel

Embed the HLS stream directly in Grafana using a Text panel (HTML mode):

```html
<video width="100%" autoplay muted controls>
  <source src="http://192.168.1.10:8888/cam0/index.m3u8" type="application/x-mpegURL">
</video>
```

## Exporting Dashboards

Export via: Dashboard → Share → Export → Save to file.

> Sanitise any credentials or server IPs before committing.
