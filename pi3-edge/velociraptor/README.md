# Velociraptor Agent — Pi 3B+ (argus-edge-01)

The Velociraptor agent runs on the edge sensor and connects to the Velociraptor server on Hetzner.

## Installation

See `hetzner-soc/velociraptor/README.md` for server setup first. Then:

```bash
# Copy the client package from Hetzner (generated during server setup):
scp pi@<HETZNER_IP>:/tmp/velociraptor_client*.deb /tmp/

sudo dpkg -i /tmp/velociraptor_client*.deb
sudo systemctl enable velociraptor_client
sudo systemctl start velociraptor_client
```

## Status Check

```bash
sudo systemctl status velociraptor_client
```

The agent should show as connected in the Velociraptor server UI at `https://<HETZNER_IP>:8889`.

## Client Config

`client.config.yaml` contains the server certificate and connection parameters. **Never commit this file.** The template in this directory has all sensitive values replaced with `<PLACEHOLDER>`.

## Key VQL Queries Run During Scenarios

During Phase 4 red team scenarios, the following VQL will be run from the Hetzner server against this agent:

```sql
-- Check for unexpected processes (post-exploitation detection)
SELECT Pid, Ppid, Name, Exe, CommandLine FROM pslist()
WHERE Name IN ('nc', 'ncat', 'bash', 'sh')

-- Check for new files in /tmp (tool staging)
SELECT FullPath, Size, Mtime FROM glob(globs='/tmp/*')

-- Check recent logins
SELECT * FROM last() ORDER BY Time DESC LIMIT 20

-- Check active network connections
SELECT * FROM netstat() WHERE Status = 'ESTABLISHED'
```
