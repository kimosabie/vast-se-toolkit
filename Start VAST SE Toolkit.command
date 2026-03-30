#!/usr/bin/env bash
# =============================================================
# VAST SE Toolkit — macOS Launcher
# Double-click to start the app. Copy to Desktop for easy use.
# First time only: right-click → Open to allow execution.
# =============================================================

# Always run from the directory this script lives in (the repo)
cd "$(dirname "$0")"

# ── Start Docker Desktop if not running ──────────────────────
if ! docker info &>/dev/null; then
    echo "Docker Desktop is not running — starting it..."
    open -a Docker

    # Wait up to 60 seconds for Docker to become ready
    READY=false
    for i in {1..30}; do
        sleep 2
        if docker info &>/dev/null; then
            READY=true
            break
        fi
        echo "Waiting for Docker Desktop to start... ($((i * 2))s)"
    done

    if ! $READY; then
        osascript -e 'display dialog "Docker Desktop did not start in time.\n\nPlease open Docker Desktop manually and try again." buttons {"OK"} default button "OK" with icon stop with title "VAST SE Toolkit"'
        exit 1
    fi

    echo "Docker Desktop is ready."
fi

# ── Check for updates ─────────────────────────────────────────
echo "Checking for updates..."
if git fetch origin main 2>/dev/null; then
    LOCAL=$(git rev-parse HEAD 2>/dev/null)
    REMOTE=$(git rev-parse origin/main 2>/dev/null)

    if [ "$LOCAL" != "$REMOTE" ]; then
        RESPONSE=$(osascript -e '
            display dialog "An update is available for VAST SE Toolkit.\n\nUpdate now? This takes about 1–2 minutes." buttons {"Skip for now", "Update"} default button "Update" with title "VAST SE Toolkit Update" with icon note
        ')
        if [[ "$RESPONSE" == *"Update"* ]]; then
            echo "Pulling latest changes..."
            git pull origin main
            echo "Rebuilding image..."
            docker compose up --build -d
            echo "Update complete."
        else
            docker compose up -d
        fi
    else
        echo "Already up to date."
        docker compose up -d
    fi
else
    # git fetch failed (offline or no SSH) — just start
    echo "Could not reach GitHub (offline?). Starting existing version."
    docker compose up -d
fi

# ── Wait for app and open browser ────────────────────────────
echo "Starting VAST SE Toolkit..."
for i in {1..20}; do
    if curl -s http://localhost:8501/_stcore/health &>/dev/null; then
        break
    fi
    sleep 2
done

open http://localhost:8501
