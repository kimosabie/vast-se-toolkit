# VAST SE Toolkit — Linux Install Guide

> **Before you start:** You'll need Docker Engine and Git. See [INSTALL.md](../INSTALL.md).

---

## Step 1 — Install Docker Engine

Docker Desktop is available for Linux but most users prefer Docker Engine (CLI only). Choose one:

### Option A — Docker Desktop for Linux *(GUI, similar to Mac/Windows)*
Follow the official guide for your distro: [docs.docker.com/desktop/install/linux-install](https://docs.docker.com/desktop/install/linux-install/)

### Option B — Docker Engine *(CLI, recommended)*

**Ubuntu / Debian:**
```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

**Add your user to the docker group** (so you don't need `sudo` every time):
```bash
sudo usermod -aG docker $USER
newgrp docker
```

**Verify Docker is running:**
```bash
docker --version
docker compose version
```

---

## Step 2 — Install Git

```bash
sudo apt-get install -y git    # Ubuntu/Debian
sudo dnf install -y git        # Fedora/RHEL
```

Verify:
```bash
git --version
```

---

## Step 3 — Download the toolkit

```bash
mkdir -p ~/projects
cd ~/projects
git clone https://github.com/kimosabie/vast-se-toolkit.git
cd vast-se-toolkit
```

---

## Step 4 — Run setup

```bash
./setup.sh
```

This will:
1. Verify Docker and Git are working
2. Create the required folders
3. Build the app image — **takes 2–3 minutes the first time**
4. Start the app

When you see `=== Setup complete! ===` you're done.

> If you get *"Permission denied"* running `./setup.sh`, run `bash setup.sh` instead.

---

## Step 5 — Open the app

Open your browser and go to:

```
http://localhost:8501
```

---

## Step 6 — Set up a Desktop launcher and pin to taskbar *(optional but recommended)*

### Create the launcher file

```bash
cat > ~/Desktop/vast-se-toolkit.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=VAST SE Toolkit
Comment=VAST SE Installation Toolkit
Exec=bash -c "cd ~/projects/vast-se-toolkit && docker compose up -d && xdg-open http://localhost:8501"
Icon=$HOME/projects/vast-se-toolkit/images/vast_logo_icon.png
Terminal=false
Categories=Development;
EOF
chmod +x ~/Desktop/vast-se-toolkit.desktop
```

### Allow it to run (Ubuntu/GNOME)

1. Double-click the file on your Desktop
2. A dialog appears — click **"Trust and Launch"**

After this, double-clicking it will start the app and open your browser.

### Pin to taskbar (GNOME)

1. Open the **Activities** overview (press the `Super` key or click Activities top-left)
2. Search for `VAST SE Toolkit`
3. Right-click the result → **Add to Favorites**

It will now appear in the left-side dock permanently.

### Pin to taskbar (other desktops)

- **KDE Plasma:** right-click the desktop icon → **Add to Panel**
- **XFCE:** right-click the desktop icon → **Add to Panel**
- **Other:** drag the `.desktop` file to your panel/taskbar

---

## Closing the app

**Just close the browser tab — that's it.** The app keeps running in the background, ready for next time.

**To fully stop the app** (frees memory — optional):
```bash
cd ~/projects/vast-se-toolkit
docker compose down
```

---

## Updating

```bash
cd ~/projects/vast-se-toolkit
git pull
docker compose pull
docker compose up -d
```

---

## Troubleshooting

**Blank page or "This site can't be reached"**
- Check Docker is running: `docker ps`
- Wait 30 seconds and refresh
- Check logs: `docker compose logs --tail=50`

**`./setup.sh` says "Docker is not running"**
- Start Docker: `sudo systemctl start docker`
- If using Docker Desktop, open it from your app launcher

**`git clone` fails**
- Check your internet connection and try again

**`docker compose` not found**
- Make sure you installed `docker-compose-plugin` (Step 1)
- Try `docker-compose` (with hyphen) as a fallback

---

[Back to main guide](../INSTALL.md)
