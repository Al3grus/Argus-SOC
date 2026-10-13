#!/usr/bin/env python3
"""OPSEC guardrail: block commits that would publish lab addresses, hostnames or secrets.

Usage:
  opsec_scan.py --staged            scan files staged for commit (pre-commit hook)
  opsec_scan.py --message FILE      scan a commit message (commit-msg hook)
  opsec_scan.py --all               scan every tracked file
  opsec_scan.py --history           scan every blob, commit message and author in all history
  opsec_scan.py FILE [FILE ...]     scan files on disk

Generic rules live here. Real values (public IP, hostnames, names, provider) go in the
untracked file `.opsec-denylist` at the repo root, or in the OPSEC_DENYLIST environment
variable (newline-separated, e.g. from a CI secret). One entry per line:
  plain text      matched case-insensitively as a substring
  re:<pattern>    Python regex, case-sensitive unless it starts with (?i)
  # comment
Add `opsec:allow` on a line to suppress findings on that line (use sparingly).
"""
import ipaddress
import os
import re
import struct
import subprocess
import sys
import urllib.parse
import zlib
import base64

ALLOW_MARK = 'opsec:allow'

# Public addresses that are fine to mention (documentation ranges, loopback, public resolvers).
ALLOWED_NETS = [ipaddress.ip_network(n) for n in (
    '0.0.0.0/32', '127.0.0.0/8', '255.255.255.255/32',
    '192.0.2.0/24', '198.51.100.0/24', '203.0.113.0/24',  # RFC 5737 documentation
    '1.1.1.1/32', '1.0.0.1/32', '8.8.8.8/32', '8.8.4.4/32', '9.9.9.9/32',
)]
PRIVATE_NETS = [ipaddress.ip_network(n) for n in (
    '10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16', '100.64.0.0/10', '169.254.0.0/16',  # opsec:allow (range definitions)
)]

IPV4 = re.compile(r'(?<![\d.])((?:\d{1,3}\.){3}\d{1,3})(?:/\d{1,2})?(?![\d]|\.\d)')
PLACEHOLDER = re.compile(r'^(<[^>]*>|\$\{?[A-Za-z_][A-Za-z0-9_]*\}?|x+|\*+|changeme|example\w*|your[_-]?\w*|redacted\w*|placeholder\w*|none|null|true|false|from)$', re.I)

SECRET_RULES = [
    ('private-key-block', re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----')),
    ('wireguard-key', re.compile(r'(?i)\b(?:Private|Preshared|Public)Key\s*=\s*[A-Za-z0-9+/]{42,43}=')),
    ('anthropic-key', re.compile(r'\bsk-ant-[A-Za-z0-9_-]{20,}')),
    ('openai-style-key', re.compile(r'\bsk-(?:proj-)?[A-Za-z0-9]{32,}')),
    ('telegram-bot-token', re.compile(r'\b\d{8,10}:[A-Za-z0-9_-]{35}\b')),
    ('telegram-chat-id', re.compile(r'(?i)\bchat[_-]?id\b["\']?\s*[:=]\s*["\']?-?\d{6,}')),
    ('pagerduty-key', re.compile(r'(?i)\b(?:routing|integration|service)[_-]?key\b["\']?\s*[:=]\s*["\']?[A-Za-z0-9]{32}\b')),
    ('aws-access-key', re.compile(r'\b(?:AKIA|ASIA)[0-9A-Z]{16}\b')),
    ('github-token', re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{60,})')),
    ('slack-token', re.compile(r'\bxox[abposr]-[A-Za-z0-9-]{10,}')),
    ('chat-webhook', re.compile(r'(?i)hooks\.slack\.com/services/|discord(?:app)?\.com/api/webhooks/')),
    ('jwt', re.compile(r'\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}')),
    ('credentials-in-url', re.compile(r'(?i)\b[a-z][a-z0-9+.-]*://[^\s/:@<>"\']+:[^\s/@<>"\']+@')),
    ('remote-webhook-url', re.compile(r'(?i)\bhttps?://(?!localhost\b|127\.0\.0\.1\b|<|\$)[^\s/"\'<>]+/webhook(?:-test)?/[A-Za-z0-9_-]+')),
    ('mac-address', re.compile(r'(?i)(?<![\w:-])(?:[0-9a-f]{2}[:-]){5}[0-9a-f]{2}(?![\w:-])')),
]
ASSIGNMENT = re.compile(
    r'(?i)\b(?:pass(?:word|wd)?|secret|token|api[_-]?key|auth[_-]?key|private[_-]?key)\b["\']?\s*[:=]\s*["\']?([^\s"\'<>,;]{8,})')

BLOCKED_PATHS = [
    (re.compile(r'(?:^|/)\.env(?:\.(?!example$)[^/]*)?$'), 'env file'),
    (re.compile(r'\.(?:key|pem|p12|pfx|ovpn)$'), 'key/certificate file'),
    (re.compile(r'(?:^|/)wg[^/]*\.conf$'), 'WireGuard config'),
    (re.compile(r'(?:^|/)[^/]*passwords?\.txt$'), 'password file'),
    (re.compile(r'(?:^|/)(?:ossec\.conf|cowrie\.cfg|mediamtx\.yml)$'), 'real service config'),
]


def load_denylist(root):
    lines = []
    path = os.path.join(root, '.opsec-denylist')
    if os.path.exists(path):
        with open(path, encoding='utf-8') as fh:
            lines += fh.read().splitlines()
    lines += os.environ.get('OPSEC_DENYLIST', '').splitlines()
    rules = []
    for raw in lines:
        entry = raw.strip()
        if not entry or entry.startswith('#'):
            continue
        if entry.startswith('re:'):
            rules.append(re.compile(entry[3:]))
        else:
            rules.append(re.compile(re.escape(entry), re.I))
    return rules


def classify_ip(text):
    try:
        ip = ipaddress.ip_address(text)
    except ValueError:
        return None
    if any(ip in n for n in ALLOWED_NETS):
        return None
    if any(ip in n for n in PRIVATE_NETS):
        return 'private-ip'
    return 'public-ip'


def png_text(data):
    """Text carried in PNG metadata chunks, including draw.io's embedded diagram source."""
    out, i = [], 8
    while i + 8 <= len(data):
        length, ctype = struct.unpack('>I4s', data[i:i + 8])
        body = data[i + 8:i + 8 + length]
        i += 12 + length
        try:
            if ctype == b'tEXt':
                out.append(body.split(b'\0', 1)[-1])
            elif ctype == b'zTXt':
                out.append(zlib.decompress(body.split(b'\0', 1)[1][1:]))
            elif ctype == b'iTXt':
                key, rest = body.split(b'\0', 1)
                flag, rest = rest[0], rest[2:]
                text = rest.split(b'\0', 2)[-1]
                out.append(zlib.decompress(text) if flag else text)
            elif ctype == b'eXIf':
                out.append(body)
        except (ValueError, zlib.error, IndexError):
            continue
    text = '\n'.join(b.decode('utf-8', 'replace') for b in out)
    text = urllib.parse.unquote(text)
    # draw.io may store each page deflated + base64 encoded
    for blob in re.findall(r'<diagram[^>]*>([A-Za-z0-9+/=\s]{40,})</diagram>', text):
        try:
            text += '\n' + urllib.parse.unquote(zlib.decompress(base64.b64decode(blob), -15).decode('utf-8', 'replace'))
        except (ValueError, zlib.error):
            pass
    return text


def to_text(path, data):
    if data.startswith(b'\x89PNG\r\n\x1a\n'):
        return png_text(data)
    if b'\0' in data[:8000]:
        # other binaries: scan printable runs (EXIF, XMP, strings)
        return '\n'.join(m.decode('latin-1') for m in re.findall(rb'[\x20-\x7e]{6,}', data))
    return data.decode('utf-8', 'replace')


def scan_text(label, text, deny):
    findings = []
    for n, line in enumerate(text.splitlines(), 1):
        if ALLOW_MARK in line:
            continue
        for m in IPV4.finditer(line):
            kind = classify_ip(m.group(1))
            if kind:
                findings.append((label, n, kind, m.group(0)))
        for name, rx in SECRET_RULES:
            for m in rx.finditer(line):
                findings.append((label, n, name, mask(m.group(0))))
        for m in ASSIGNMENT.finditer(line):
            if not PLACEHOLDER.match(m.group(1)):
                findings.append((label, n, 'credential-assignment', mask(m.group(0))))
        for rx in deny:
            for m in rx.finditer(line):
                findings.append((label, n, 'denylist', m.group(0)))
    return findings


def scan_blob(path, data, deny):
    findings = [(path, 0, 'blocked-path', why) for rx, why in BLOCKED_PATHS if rx.search(path)]
    return findings + scan_text(path, to_text(path, data), deny)


def mask(s):
    return s if len(s) <= 12 else s[:10] + '...'


def git(*args, data=None):
    return subprocess.run(['git', *args], input=data, capture_output=True, check=True).stdout


def staged_files():
    out = git('diff', '--cached', '--name-only', '--diff-filter=ACMR', '-z')
    return [p for p in out.decode('utf-8').split('\0') if p]


def main(argv):
    root = git('rev-parse', '--show-toplevel').decode().strip()
    os.chdir(root)
    deny = load_denylist(root)
    findings = []
    mode = argv[0] if argv else '--staged'
    if mode == '--staged':
        for p in staged_files():
            findings += scan_blob(p, git('show', f':{p}'), deny)
        for var in ('GIT_AUTHOR_IDENT', 'GIT_COMMITTER_IDENT'):
            findings += scan_text(var, git('var', var).decode('utf-8', 'replace'), deny)
    elif mode == '--all':
        for p in git('ls-files', '-z').decode('utf-8').split('\0'):
            if p:
                findings += scan_blob(p, git('show', f':{p}'), deny)
    elif mode == '--message':
        with open(argv[1], encoding='utf-8', errors='replace') as fh:
            msg = '\n'.join(l for l in fh.read().splitlines() if not l.startswith('#'))
        findings += scan_text('commit message', msg, deny)
    elif mode == '--history':
        seen = set()
        for line in git('rev-list', '--objects', '--all').decode('utf-8').splitlines():
            sha, _, path = line.partition(' ')
            if not path or sha in seen:
                continue
            seen.add(sha)
            if git('cat-file', '-t', sha).strip() != b'blob':
                continue
            findings += [(f'{path}@{sha[:7]}', *f[1:]) for f in scan_blob(path, git('cat-file', 'blob', sha), deny)]
        log = git('log', '--all', '--format=%H%n%an <%ae>%n%cn <%ce>%n%B%n\x1e').decode('utf-8', 'replace')
        for entry in log.split('\x1e'):
            entry = entry.strip()
            if entry:
                sha, _, body = entry.partition('\n')
                findings += scan_text(f'commit {sha[:7]}', body, deny)
    else:
        for p in argv:
            with open(p, 'rb') as fh:
                findings += scan_blob(p.replace(os.sep, '/'), fh.read(), deny)

    if not findings:
        return 0
    print('opsec: blocked - this would publish identifying or secret data:', file=sys.stderr)
    for label, n, rule, hit in findings:
        where = f'{label}:{n}' if n else label
        print(f'  {where}: [{rule}] {hit}', file=sys.stderr)
    print('Replace real values with placeholders (<LAB_SUBNET>, sensor-01, ...) or add '
          f'"{ALLOW_MARK}" to a line that is a deliberate exception.', file=sys.stderr)
    return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
