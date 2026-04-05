# VAST SE Toolkit — Windows Install Guide

> **Before you start:** You'll need Docker Desktop and Git. See [INSTALL.md](../INSTALL.md).

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

## Step 4 — Download the toolkit

In your Ubuntu terminal:

```bash
mkdir -p ~/projects
cd ~/projects
git clone https://github.com/kimosabie/vast-se-toolkit.git
cd vast-se-toolkit
```

---

## Step 5 — Run setup

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

## Step 6 — Open the app

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

## Step 7 — Set up the Desktop launcher and pin to taskbar *(optional but recommended)*

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

## Step 8 — Enable Google Drive backup *(optional but recommended)*

The toolkit can automatically back up your project database to Google Drive so your work is safe across machines.

**Requirement:** Google Drive Desktop must be installed and set to **Mirror files** mode (not Stream files). Mirror mode keeps a real copy of your files on disk so WSL2 can reach them.

### Switch Google Drive Desktop to Mirror mode

1. Click the Google Drive icon in your system tray (bottom-right)
2. Click the gear icon → **Preferences**
3. On the left, click **Google Drive**
4. Switch from **Stream files** to **Mirror files**
5. Note the folder path shown (usually `C:\Users\yourname\My Drive`) — click **Save**

### Find your path in WSL2

Open your Ubuntu terminal and run (replace `yourname` with your Windows username):

```bash
ls "/mnt/c/Users/yourname/My Drive/"
```

If you see your Drive contents listed, the path is correct.

### Configure the .env file

In Ubuntu, open the `.env` file in the project folder:

```bash
nano ~/projects/vast-se-toolkit/.env
```

Uncomment and set `CLOUD_SYNC_DIR` to your path:

```
CLOUD_SYNC_DIR=/mnt/c/Users/yourname/My Drive/VAST Backups
```

Save with `Ctrl+O`, then `Ctrl+X` to exit. Then restart the app:

```bash
cd ~/projects/vast-se-toolkit
docker compose restart
```

The **Session** tab will now show a **☁️ Cloud Backup** section. The `VAST Backups` folder will be created automatically on first backup.

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
docker compose pull
docker compose up -d
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

**`git clone` fails**
- Make sure you're running the command inside Ubuntu, not PowerShell
- Check your internet connection and try again

**WSL2 install failed or `wsl --install` did nothing**
- Your Windows may need updating: Settings → Windows Update → Check for updates
- After updating, try `wsl --install` again in an Administrator PowerShell

---

[Back to main guide](../INSTALL.md)
