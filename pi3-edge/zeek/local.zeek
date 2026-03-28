# Zeek Local Policy — Pi 3B+ (argus-edge-01)
# Location: /etc/zeek/site/local.zeek

# Load default scripts
@load base/protocols/conn
@load base/protocols/dns
@load base/protocols/http
@load base/protocols/ssl
@load base/protocols/ssh
@load base/protocols/ftp
@load base/protocols/smtp

# JSON log output (required for Wazuh Agent to parse)
@load policy/tuning/json-logs

# Notice framework for custom detections
@load base/frameworks/notice

# Track software versions (useful for vulnerability correlation)
@load policy/frameworks/software/vulnerable

# Detect SSH brute force
@load policy/protocols/ssh/detect-bruteforcing

# Log all files transferred
@load base/frameworks/files/hash-all-files
