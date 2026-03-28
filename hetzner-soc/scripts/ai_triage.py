#!/usr/bin/env python3
"""
Argus SOC — AI Triage Script
Classifies Wazuh alerts using the Claude API (Anthropic).

Usage:
  python3 ai_triage.py <alert_json_file>
  echo '<alert_json>' | python3 ai_triage.py

Output: Structured JSON classification to stdout.

Environment variables:
  ANTHROPIC_API_KEY — required
"""

import sys
import json
import os
import re
from datetime import datetime

import anthropic

# ── Configuration ──────────────────────────────────────────────────────────────

MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 1024

# Known network context — update as lab evolves
NETWORK_CONTEXT = {
    "home_net": "192.168.1.0/24",
    "wireguard_net": "10.0.0.0/24",
    "known_hosts": {
        "192.168.1.10": "argus-central (Pi 5 — client infrastructure, hosts Metasploitable 2 + DVWA)",
        "192.168.1.20": "argus-edge-01 (Pi 3B+ — MSSP edge sensor)",
        "10.0.0.1":     "argus-central WireGuard",
        "10.0.0.2":     "argus-edge-01 WireGuard",
        "10.0.0.3":     "ThinkPad WireGuard (red team management access)",
    },
    "honeypot_port": 22,
    "real_ssh_port": 2222,
}

# ── System Prompt ───────────────────────────────────────────────────────────────

SYSTEM_PROMPT = f"""You are a Level 1 SOC analyst performing alert triage for Argus Security Operations Center.

Your task: analyze the Wazuh alert JSON provided and return a structured classification.

SEVERITY DEFINITIONS:
- noise: Benign, expected network behaviour. No security relevance. Examples: DNS to known CDN, ICMP from router, TLS version mismatch on internal service, scheduled scan from known scanner.
- low: Informational. Minor anomaly, no immediate threat. Examples: single failed SSH login, unusual but benign DNS query, low-confidence signature match.
- medium: Suspicious activity requiring investigation. Examples: multiple failed SSH logins, Nmap service scan pattern, SQL injection attempt in HTTP traffic, Suricata medium-confidence signature.
- critical: Active threat requiring immediate response. Examples: successful exploitation (Metasploit payload), brute force success on honeypot, lateral movement from compromised host, reverse shell indicator.

NETWORK CONTEXT:
- HOME_NET (monitored): {NETWORK_CONTEXT['home_net']}
- WireGuard tunnel: {NETWORK_CONTEXT['wireguard_net']}
- Known hosts: {json.dumps(NETWORK_CONTEXT['known_hosts'], indent=2)}
- Port 22: Cowrie honeypot on Pi 3B+ (any login here is suspicious by definition)
- Port 2222: Real SSH on Pi 3B+ (brute force here is more serious)

IMPORTANT CONTEXT:
- This is a home lab environment. Some "attacks" are authorized red team exercises from the ThinkPad (10.0.0.3 or guest WiFi).
- Traffic involving 192.168.1.10 as TARGET is expected attack traffic (Metasploitable 2, DVWA).
- Traffic FROM 192.168.1.10 to other hosts is highly suspicious (lateral movement indicator from compromised target).
- All Cowrie honeypot events (port 22 on Pi 3B+) are suspicious by definition.

OUTPUT: Return ONLY valid JSON, no markdown, no preamble, no explanation outside the JSON:
{{
  "severity": "noise|low|medium|critical",
  "summary": "2-3 sentence plain-English explanation of what happened, what triggered it, and why it matters",
  "mitre_technique": "TXXXX or null",
  "mitre_technique_name": "Technique name or null",
  "recommended_action": "ignore|monitor|investigate|respond_immediately",
  "confidence": 0.0-1.0,
  "reasoning": "1-2 sentences explaining your classification decision"
}}"""

# ── Main ────────────────────────────────────────────────────────────────────────

def load_alert(source):
    """Load alert JSON from file path or stdin."""
    if source == "-" or source is None:
        raw = sys.stdin.read()
    else:
        with open(source, "r") as f:
            raw = f.read()
    return json.loads(raw)


def classify_alert(alert_json: dict) -> dict:
    """Send alert to Claude API and return structured classification."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    client = anthropic.Anthropic(api_key=api_key)

    # Add timestamp context to help Claude assess time-of-day anomalies
    alert_with_context = {
        "alert": alert_json,
        "analysis_time": datetime.utcnow().isoformat() + "Z",
        "day_of_week": datetime.utcnow().strftime("%A"),
        "hour_utc": datetime.utcnow().hour,
    }

    message = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Analyze this Wazuh alert:\n\n{json.dumps(alert_with_context, indent=2)}"
            }
        ]
    )

    response_text = message.content[0].text.strip()

    # Strip markdown code blocks if Claude wraps the JSON
    response_text = re.sub(r'^```json\s*', '', response_text)
    response_text = re.sub(r'\s*```$', '', response_text)

    return json.loads(response_text)


def main():
    source = sys.argv[1] if len(sys.argv) > 1 else "-"

    try:
        alert = load_alert(source)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(json.dumps({"error": f"Failed to load alert: {e}", "severity": "noise"}))
        sys.exit(1)

    try:
        result = classify_alert(alert)
        print(json.dumps(result, indent=2))
    except Exception as e:
        # Fail safe — if Claude is unavailable, log as low and continue
        # The pipeline must not block on AI unavailability
        fallback = {
            "severity": "low",
            "summary": "AI triage unavailable — alert requires manual review.",
            "mitre_technique": None,
            "mitre_technique_name": None,
            "recommended_action": "monitor",
            "confidence": 0.0,
            "reasoning": f"Claude API error: {str(e)}. Alert forwarded for manual triage.",
        }
        print(json.dumps(fallback, indent=2))
        sys.exit(0)  # Don't fail the pipeline — alert still flows


if __name__ == "__main__":
    main()
