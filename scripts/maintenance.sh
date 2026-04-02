#!/bin/bash
# Daily maintenance — runs at 2am via root crontab
# Pulls system updates, refreshes toolkit image, then reboots.
# Container restarts automatically after reboot (restart: unless-stopped).

set -euo pipefail

LOGFILE="/var/log/vast-maintenance.log"
TOOLKIT_DIR="/home/kimo/projects/vast-se-toolkit"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOGFILE"
}

log "=== Maintenance started ==="

# ── System updates ────────────────────────────────────────────
log "Running apt update..."
apt-get update -qq
log "Running apt upgrade..."
DEBIAN_FRONTEND=noninteractive apt-get upgrade -y -qq
log "System updates done."

# ── Toolkit git pull ──────────────────────────────────────────
log "Pulling latest toolkit from git..."
cd "$TOOLKIT_DIR"
sudo -u kimo git pull --ff-only >> "$LOGFILE" 2>&1 || log "WARNING: git pull failed — skipping"

# ── Docker image refresh ──────────────────────────────────────
log "Pulling latest Docker image from GHCR..."
sudo -u kimo docker compose pull >> "$LOGFILE" 2>&1 || log "WARNING: docker compose pull failed — skipping"

# ── Reboot ────────────────────────────────────────────────────
log "=== Maintenance complete — rebooting now ==="
/sbin/reboot
