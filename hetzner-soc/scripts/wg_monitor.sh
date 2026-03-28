#!/bin/bash
# Argus SOC — WireGuard Tunnel Monitor
# Runs every minute via cron on Pi 5 (argus-central)
# Fires a critical webhook to n8n if Pi 3B+ tunnel goes down
#
# Crontab entry:
# * * * * * /home/pi/argus/scripts/wg_monitor.sh
#
# Environment:
#   N8N_HOST — Hetzner VPS IP

N8N_HOST="${N8N_HOST:-<HETZNER_IP>}"
PEER_IP="10.0.0.2"
WEBHOOK_URL="http://${N8N_HOST}:5678/webhook/wg-down"

if ! ping -c 3 -W 5 "${PEER_IP}" > /dev/null 2>&1; then
    curl -s -X POST "${WEBHOOK_URL}" \
        -H 'Content-Type: application/json' \
        -d "{\"alert\": \"Edge sensor argus-edge-01 (${PEER_IP}) WireGuard tunnel DOWN\", \"severity\": \"critical\", \"source\": \"wg-monitor\", \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}"
fi
