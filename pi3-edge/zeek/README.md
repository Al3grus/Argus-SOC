# Zeek Protocol Analysis — Pi 3B+ (argus-edge-01)

Zeek complements Suricata. Where Suricata fires on signature matches, Zeek generates protocol metadata for everything — including traffic that matches no signature. Together they provide complete network visibility.

## Log Files Generated

| Log | Contents | Key Use Case |
|-----|----------|-------------|
| `conn.log` | Every connection: src/dst IP, port, bytes, duration | Reconnaissance detection, lateral movement |
| `dns.log` | All DNS queries and responses | C2 domain detection, DGA identification |
| `http.log` | HTTP method, URI, user-agent, response code | Web attack detection, C2 beacons |
| `ssl.log` | TLS version, cipher, certificate | Encrypted C2, JA3 fingerprinting |
| `ssh.log` | SSH version, authentication outcome | Brute force correlation |
| `ftp.log` | FTP commands and responses | vsftpd exploit detection (Scenario 3) |
| `files.log` | File transfers and hashes | Malware staging detection |
| `notice.log` | Zeek-generated alerts | SSH brute force, policy violations |

## Wazuh Integration

Wazuh Agent on Pi 3B+ reads Zeek JSON logs via these entries in `/var/ossec/etc/ossec.conf`:

```xml
<localfile>
  <log_format>json</log_format>
  <location>/var/log/zeek/current/conn.log</location>
  <label key="zeek_log">conn</label>
</localfile>

<localfile>
  <log_format>json</log_format>
  <location>/var/log/zeek/current/dns.log</location>
  <label key="zeek_log">dns</label>
</localfile>

<localfile>
  <log_format>json</log_format>
  <location>/var/log/zeek/current/http.log</location>
  <label key="zeek_log">http</label>
</localfile>

<localfile>
  <log_format>json</log_format>
  <location>/var/log/zeek/current/notice.log</location>
  <label key="zeek_log">notice</label>
</localfile>
```

## Auto-start

Zeek is started on boot via crontab (systemd service is not available for standalone mode on Pi OS):

```bash
@reboot sleep 30 && /usr/bin/zeekctl deploy
```

The 30-second delay ensures the network interface is fully up before Zeek attempts to start.

## Useful Commands

```bash
# Check Zeek status
sudo zeekctl status

# Deploy config changes
sudo zeekctl deploy

# Check current log output
tail -f /var/log/zeek/current/conn.log | python3 -m json.tool

# Check notice log for automated alerts
cat /var/log/zeek/current/notice.log | python3 -m json.tool
```
