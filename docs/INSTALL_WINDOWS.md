# VAST SE Toolkit — Windows Install Guide

> **Before you start:** Make sure Kimo has added you to the GitHub repo and you've accepted the invite. See [INSTALL.md](../INSTALL.md).

The toolkit runs inside Docker using **WSL2** (Windows Subsystem for Linux). This gives you a real Linux environment on your Windows machine — it's fast, stable, and required for Docker to work properly.

Total setup time: **15–20 minutes** (mostly waiting for downloads).

---

## Step 1 — Enable WSL2 and install Ubuntu

Open **PowerShell as Administrator**:
- Press `Windows key`, type `PowerShell`, right-click → **Run as administrator**

Run this single command:

```powershell
wsl --install
```

This will:
- Enable WSL2
- Install Ubuntu automatically

**Restart your computer when prompted.**

> If you see `"WSL is already installed"`, run `wsl --install -d Ubuntu` instead, then restart.

After restarting, Ubuntu will open automatically and ask you to create a username and password. Use something simple — this is just your local Linux account.

---

## Step 2 — Install Docker Desktop

1. Go to [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) and click **Download for Windows**
2. Run the installer — accept all defaults
3. When installation finishes, open **Docker Desktop** from the Start Menu
4. Wait until the whale icon appears in your taskbar (bottom-right) and says **"Docker Desktop is running"**

**Verify WSL2 integration is on:**
- Click the gear icon (Settings) → **Resources** → **WSL Integration**
- Make sure **"Enable integration with my default WSL distro"** is toggled on
- Also toggle on **Ubuntu** if it appears in the list
- Click **Apply & Restart**

> Docker must be running every time you use the toolkit.

---

## Step 3 — Open your Ubuntu terminal

All remaining steps happen inside Ubuntu — not PowerShell or CMD.

Open Ubuntu:
- Press `Windows key`, type `Ubuntu`, press Enter

You'll see a prompt like `yourname@LAPTOP:~$` — this is your Linux terminal.

> **Tip:** Pin Ubuntu to your taskbar now — you'll use it regularly.

---

## Step 4 — Set up your SSH key for GitHub

This is a one-time step so Ubuntu can connect to GitHub.

### Check if you already have a key

```bash
ls ~/.ssh/id_ed25519.pub
```

- If a file path is printed — you already have a key, **skip to step 4d**
- If you see *"No such file or directory"* — continue to the next step

### Generate a new key

```bash
ssh-keygen -t ed25519 -C "your-email@vast.com"
```

When prompted:
- *"Enter file in which to save the key"* — press **Enter**
- *"Enter passphrase"* — press **Enter** twice

### Copy your public key

```bash
cat ~/.ssh/id_ed25519.pub
```

This prints a long line starting with `ssh-ed25519 AAAA...` — **select the entire line and copy it**.

### Add the key to GitHub

1. Go to [github.com/settings/ssh/new](https://github.com/settings/ssh/new)
2. **Title:** `My Work PC`
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

---

## Step 5 — Download the toolkit

In your Ubuntu terminal:

```bash
mkdir -p ~/projects
cd ~/projects
git clone git@github.com:kimosabie/vast-se-toolkit.git
cd vast-se-toolkit
```

> If you see *"Repository not found"* — the GitHub invite wasn't accepted yet. Go back to the [main guide](../INSTALL.md).

---

## Step 6 — Run setup

Make sure the Docker whale icon is visible in your taskbar, then in Ubuntu run:

```bash
./setup.sh
```

This will:
1. Verify Docker and Git are working
2. Create the required folders
3. Build the app image — **takes 2–3 minutes the first time**
4. Start the app

When you see `=== Setup complete! ===` you're done.

---

## Step 7 — Open the app

Open your browser and go to:

```
http://localhost:8501
```

---

## Day-to-day use

1. Open **Docker Desktop** (whale icon must be visible in taskbar)
2. Open **Ubuntu** terminal and run:
   ```bash
   cd ~/projects/vast-se-toolkit
   docker compose up -d
   ```
3. Go to **http://localhost:8501**

Or use the Desktop launcher (see below).

---

## Step 8 — Set up the Desktop launcher and pin to taskbar *(optional but recommended)*

This lets you start the toolkit with a single click — no terminal needed.

Windows won't let you pin a `.ps1` script directly to the taskbar, so you create a shortcut that wraps it.

### Create the shortcut

1. Right-click an empty spot on your **Desktop** → **New** → **Shortcut**
2. When asked for the location, paste this exactly — replacing `yourname` with your Ubuntu username:
   ```
   powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File "\\wsl$\Ubuntu\home\yourname\projects\vast-se-toolkit\Start VAST SE Toolkit.ps1"
   ```
3. Click **Next**
4. Name it `VAST SE Toolkit`, click **Finish**

### Give it a better icon *(optional)*

1. Right-click the new shortcut → **Properties**
2. Click **Change Icon...**
3. Browse to `C:\Windows\System32\shell32.dll` and pick any icon you like
4. Click **OK** → **Apply**

### Pin to the taskbar

1. Right-click the shortcut on your Desktop
2. Click **Pin to taskbar**

The icon will appear in your taskbar. Click it anytime to start the toolkit and open your browser automatically.

> **First time only:** Windows may show a security warning. Click **Open** or allow the script to run. This only happens once.

---

## Closing the app

**Just close the browser tab — that's it.** The app keeps running in the background, ready for next time.

**To fully stop the app** (frees memory — optional), in Ubuntu:
```bash
cd ~/projects/vast-se-toolkit
docker compose down
```
Or open **Docker Desktop** → find `vast-se-toolkit` → click Stop.

---

## Updating

When Kimo releases a new version, open Ubuntu and run:

```bash
cd ~/projects/vast-se-toolkit
git pull
docker compose up --build -d
```

Your saved projects are never affected.

---

## Troubleshooting

**Blank page or "This site can't be reached"**
- Check the whale icon is showing in your taskbar
- Wait 30 seconds and refresh the page
- Check logs in Ubuntu: `docker compose logs --tail=50`

**`./setup.sh` says "Docker is not running"**
- Open Docker Desktop from the Start Menu and wait for the whale icon before re-running

**`docker: command not found` in Ubuntu**
- Open Docker Desktop → Settings → Resources → WSL Integration → toggle on Ubuntu → Apply & Restart

**`git clone` says "Permission denied (publickey)"**
- Redo Step 4 — your SSH key may not be saved to GitHub correctly
- Make sure you ran the SSH commands inside Ubuntu, not PowerShell

**WSL2 install failed or `wsl --install` did nothing**
- Your Windows may need updating: Settings → Windows Update → Check for updates
- After updating, try `wsl --install` again in an Administrator PowerShell

---

[Back to main guide](../INSTALL.md)
