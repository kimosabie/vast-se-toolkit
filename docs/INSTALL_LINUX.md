# VAST SE Toolkit — Linux Install Guide

> **Before you start:** Make sure Kimo has added you to the GitHub repo and you've accepted the invite. See [INSTALL.md](../INSTALL.md).

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

## Step 3 — Set up your SSH key for GitHub

This is a one-time step so your machine can securely connect to GitHub.

### Check if you already have a key

```bash
ls ~/.ssh/id_ed25519.pub
```

- If a file path is printed — you already have a key, **skip to step 3d**
- If you see *"No such file or directory"* — continue to the next step

### Generate a new key

```bash
ssh-keygen -t ed25519 -C "your-email@vast.com"
```

When prompted:
- *"Enter file in which to save the key"* — press **Enter**
- *"Enter passphrase"* — press **Enter**
- *"Enter same passphrase again"* — press **Enter**

### Copy your public key

```bash
cat ~/.ssh/id_ed25519.pub
```

This prints a long line starting with `ssh-ed25519 AAAA...` — **select the entire line and copy it**.

### Add the key to GitHub

1. Go to [github.com/settings/ssh/new](https://github.com/settings/ssh/new)
2. **Title:** `My Linux Machine`
3. **Key:** paste what you copied
4. Click **Add SSH key**

### Verify it works

```bash
ssh -T git@github.com
```

You should see:
```
Hi yourname! You've successfully authenticated...
```

> If you see *"Permission denied"* — check that you pasted the full key and saved it on GitHub.

---

## Step 4 — Download the toolkit

```bash
mkdir -p ~/projects
cd ~/projects
git clone git@github.com:kimosabie/vast-se-toolkit.git
cd vast-se-toolkit
```

> If you see *"Repository not found"* — the GitHub invite wasn't accepted yet. Go back to the [main guide](../INSTALL.md).

---

## Step 5 — Run setup

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

## Step 6 — Open the app

Open your browser and go to:

```
http://localhost:8501
```

---

## Step 7 — Set up a Desktop launcher and pin to taskbar *(optional but recommended)*

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

**`git clone` says "Permission denied (publickey)"**
- Redo Step 3 — your SSH key may not be saved to GitHub correctly
- Confirm you accepted the GitHub invite

**`docker compose` not found**
- Make sure you installed `docker-compose-plugin` (Step 1)
- Try `docker-compose` (with hyphen) as a fallback

---

[Back to main guide](../INSTALL.md)
