#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="/opt/watcherV2"
TARGET_SCRIPT="$TARGET_DIR/watcher2.py"
SERVICE_FILE="/etc/systemd/system/watcher2.service"

if [[ "${EUID}" -ne 0 ]]; then
  echo "Please run as root (use sudo)."
  exit 1
fi

mkdir -p "$TARGET_DIR"
install -m 755 src/watcher2.py "$TARGET_SCRIPT"

cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=WatcherV2 x-ui traffic watcher
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 $TARGET_SCRIPT
Restart=always
RestartSec=2
WorkingDirectory=$TARGET_DIR

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now watcher2.service

echo "WatcherV2 installed and running via systemd service watcher2.service"
