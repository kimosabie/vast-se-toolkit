#!/usr/bin/env bash
# =============================================================
# VAST SE Toolkit — One-time setup script
# Run this once after cloning the repo.
# =============================================================
set -e

BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
RESET="\033[0m"

echo ""
echo -e "${BOLD}=== VAST SE Toolkit — Setup ===${RESET}"
echo ""

# ── 1. Git ────────────────────────────────────────────────────
if ! command -v git &>/dev/null; then
    echo -e "${RED}ERROR: git is not installed.${RESET}"
    echo "Install Git and re-run this script."
    exit 1
fi
echo -e "${GREEN}✓${RESET} git found"

# ── 2. SSH access to GitHub ───────────────────────────────────
echo "  Checking GitHub SSH access..."
SSH_TEST=$(ssh -o ConnectTimeout=8 -T git@github.com 2>&1 || true)
if echo "$SSH_TEST" | grep -q "successfully authenticated"; then
    echo -e "${GREEN}✓${RESET} GitHub SSH access OK"
else
    echo ""
    echo -e "${RED}ERROR: SSH authentication to GitHub failed.${RESET}"
    echo ""
    echo "Your SSH key is either missing or not added to your GitHub account."
    echo ""
    echo "Fix steps:"
    echo "  1. Generate a key (skip if you already have one):"
    echo "       ssh-keygen -t ed25519 -C \"your-email@vast.com\""
    echo "  2. Copy your public key:"
    echo "       cat ~/.ssh/id_ed25519.pub"
    echo "  3. Add it to GitHub:"
    echo "       https://github.com/settings/ssh/new"
    echo "  4. Re-run this script."
    exit 1
fi

# ── 3. Docker ─────────────────────────────────────────────────
if ! docker info &>/dev/null; then
    echo ""
    echo -e "${RED}ERROR: Docker is not running.${RESET}"
    echo "Start Docker Desktop and re-run this script."
    exit 1
fi
echo -e "${GREEN}✓${RESET} Docker is running"

# ── 4. Required directories & files ───────────────────────────
mkdir -p data outputs
echo -e "${GREEN}✓${RESET} data/ and outputs/ directories ready"

if [ ! -f .env ]; then
    touch .env
    echo -e "${GREEN}✓${RESET} .env created"
fi

# ── 5. Build and start ────────────────────────────────────────
echo ""
echo -e "${BOLD}Building VAST SE Toolkit image...${RESET}"
echo "(First build takes 2–3 minutes)"
echo ""
docker compose up --build -d

# ── 6. Wait for app to become ready ───────────────────────────
echo ""
echo "Waiting for app to start..."
READY=false
for i in {1..30}; do
    if curl -s http://localhost:8501/_stcore/health &>/dev/null; then
        READY=true
        break
    fi
    sleep 2
done

echo ""
echo -e "${BOLD}${GREEN}=== Setup complete! ===${RESET}"
echo ""
if $READY; then
    echo -e "VAST SE Toolkit is running at: ${BOLD}http://localhost:8501${RESET}"
else
    echo -e "${YELLOW}App may still be starting. Open http://localhost:8501 in a moment.${RESET}"
fi
echo ""
echo "Next steps:"

# Detect OS for platform-specific hint
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "  • Copy 'Start VAST SE Toolkit.command' to your Desktop for easy launching"
    echo "  • First time: right-click → Open to allow execution"
    # Try to open browser automatically
    open http://localhost:8501 2>/dev/null || true
else
    echo "  • On Windows: copy 'Start VAST SE Toolkit.ps1' to your Desktop"
    echo "  • Right-click → Run with PowerShell to launch"
fi
echo ""
echo "To update later:  git pull && docker compose up --build -d"
echo "To stop:          docker compose down"
echo ""
