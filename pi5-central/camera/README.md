# Physical Security Camera Stack — Pi 5 (argus-central)

## Architecture

```
OV5647 NoIR Camera (CSI)
        ↓
MediaMTX (RTSP :8554 / HLS :8888 / WebRTC :8889)
        ↓                    ↓
   Frigate NVR          Grafana Dashboard
 (AI detection)        (HLS feed embedded
        ↓               in SOC panel)
Wazuh Agent (Pi 5)
        ↓
Hetzner Wazuh Manager
        ↓
n8n → Claude API → Telegram notification
```

## Stream URLs

| Protocol | URL | Use Case |
|----------|-----|----------|
| RTSP | `rtsp://192.168.1.10:8554/cam0` | Frigate, VLC, NVR clients |
| HLS | `http://192.168.1.10:8888/cam0/index.m3u8` | Grafana dashboard, browser |
| WebRTC | `http://192.168.1.10:8889/cam0` | Low-latency browser viewing |

## UFW Rules Required on Pi 5

```bash
sudo ufw allow 8554/tcp comment 'MediaMTX RTSP'
sudo ufw allow 8888/tcp comment 'MediaMTX HLS'
sudo ufw allow 8889/tcp comment 'MediaMTX WebRTC'
```

## MediaMTX Systemd Service

```
# /etc/systemd/system/mediamtx.service
[Unit]
Description=MediaMTX RTSP Server
After=network.target

[Service]
ExecStart=/usr/local/bin/mediamtx /etc/mediamtx.yml
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

## Frigate Docker Run

```bash
docker run -d \
  --name frigate \
  --restart=unless-stopped \
  --shm-size=64m \
  -v /home/pi/frigate/config:/config \
  -v /home/pi/frigate/storage:/media/frigate \
  -p 5000:5000 \
  ghcr.io/blakeblackshear/frigate:stable
```

## Status

| Component | Status |
|-----------|--------|
| OV5647 camera detected | ✅ Done |
| MediaMTX installed and running | ✅ Done |
| MediaMTX systemd service | ✅ Done |
| Wazuh Agent on Pi 5 | ⏳ Phase 6 |
| Frigate — AI motion/object detection | ⏳ Phase 6 |
| Frigate events → Wazuh alert | ⏳ Phase 6 |
| Grafana — HLS feed in SOC dashboard | ⏳ Phase 6 |
| n8n → Telegram for motion events | ⏳ Phase 6 |
