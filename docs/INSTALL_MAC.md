# VAST SE Toolkit — macOS Install Guide

> **Before you start:** You'll need Docker Desktop and Git. See [INSTALL.md](../INSTALL.md).

---

## Step 1 — Install Docker Desktop

1. Go to [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) and click **Download for Mac**
2. Open the downloaded `.dmg` file and drag Docker to your Applications folder
3. Open **Docker** from Applications
4. Wait until the whale icon appears in your menu bar and says **"Docker Desktop is running"**

> Docker must be running every time you use the toolkit.

---

## Step 2 — Install Git

Open **Terminal** (press `Cmd + Space`, type `Terminal`, press Enter) and run:

```bash
git --version
```

- If you see a version number (e.g. `git version 2.39.0`) — Git is already installed, **skip to Step 3**
- If a dialog pops up asking to install Xcode Command Line Tools — click **Install** and wait for it to finish

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

Make sure the Docker whale icon is visible in your menu bar, then run:

```bash
./setup.sh
```

This will:
1. Verify Docker and Git are working
2. Create the required folders
3. Build the app image — **takes 2–3 minutes the first time**
4. Start the app and open your browser automatically

When you see `=== Setup complete! ===` you're done.

---

## Step 5 — Open the app

Your browser should open automatically. If it doesn't, go to:

```
http://localhost:8501
```

---

## Step 6 — Set up the Desktop launcher and pin to Dock *(optional but recommended)*

This lets you start the toolkit with a single click — no terminal needed.

### Copy the launcher to your Desktop

1. Open **Finder** → press `Cmd + Shift + G` → type `~/projects/vast-se-toolkit/` → press Enter
2. Copy **`Start VAST SE Toolkit.command`** to your Desktop

### Allow it to run (first time only)

macOS will block the script the first time:

1. Right-click the file on your Desktop → **Open**
2. A security dialog appears — click **Open** again
3. After this, you can double-click it normally forever

### Pin to the Dock

1. Double-click the launcher once so it runs (this registers it with the system)
2. Find the **Terminal** icon that appears in the Dock while it runs
3. Right-click the Terminal icon in the Dock → **Options** → **Keep in Dock**

> **Tip:** After pinning, you can rename or change the icon: right-click the Dock icon → **Options** → **Show in Finder**, then `Cmd + I` to open info and drag a new icon image onto it.

---

## Step 7 — Enable Google Drive backup *(optional but recommended)*

The toolkit can automatically back up your project database to Google Drive so your work is safe across machines.

**Requirement:** Google Drive Desktop must be installed and set to **Mirror files** mode (not Stream files). Mirror mode keeps a real copy of your files on disk so the app can reach them.

### Switch Google Drive Desktop to Mirror mode

1. Click the Google Drive icon in your menu bar
2. Click the gear icon → **Preferences**
3. On the left, click **Google Drive**
4. Switch from **Stream files** to **Mirror files** and click **Save**

Google Drive Desktop mirrors your files to:
```
/Users/yourname/Library/CloudStorage/GoogleDrive-you@company.com/My Drive/
```

### Verify the path

Open Terminal and run (replace with your actual username and Google account email):

```bash
ls ~/Library/CloudStorage/
```

You'll see a folder like `GoogleDrive-you@vast.com` — note the exact name.

### Configure the .env file

Open the `.env` file in the project folder:

```bash
nano ~/projects/vast-se-toolkit/.env
```

Uncomment and set `CLOUD_SYNC_DIR`:

```
CLOUD_SYNC_DIR=/Users/yourname/Library/CloudStorage/GoogleDrive-you@vast.com/My Drive/VAST Backups
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

The Desktop launcher handles everything when you double-click it again:
- If Docker Desktop isn't running, it starts it automatically
- If the container stopped, it restarts it
- Your data is always safe regardless

**To fully stop the app** (frees memory — optional):
```bash
cd ~/projects/vast-se-toolkit
docker compose down
```
Or open **Docker Desktop** → find `vast-se-toolkit` → click Stop.

---

## Updating

When Kimo releases a new version, open Terminal and run:

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
- Check the whale icon is showing in your menu bar
- Wait 30 seconds and refresh the page
- Check logs: `docker compose logs --tail=50`

**`./setup.sh` says "Docker is not running"**
- Open Docker Desktop from Applications and wait for the whale icon before re-running

**`git clone` fails**
- Check your internet connection and try again

---

[Back to main guide](../INSTALL.md)
