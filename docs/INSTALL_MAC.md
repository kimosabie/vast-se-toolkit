# VAST SE Toolkit — macOS Install Guide

> **Before you start:** Make sure Kimo has added you to the GitHub repo and you've accepted the invite. See [INSTALL.md](../INSTALL.md).

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

## Step 3 — Set up your SSH key for GitHub

This is a one-time step so your Mac can securely connect to GitHub.

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
2. **Title:** `My Mac`
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

## Step 6 — Open the app

Your browser should open automatically. If it doesn't, go to:

```
http://localhost:8501
```

---

## Step 7 — Set up the Desktop launcher and pin to Dock *(optional but recommended)*

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

## Troubleshooting

**Blank page or "This site can't be reached"**
- Check the whale icon is showing in your menu bar
- Wait 30 seconds and refresh the page
- Check logs: `docker compose logs --tail=50`

**`./setup.sh` says "Docker is not running"**
- Open Docker Desktop from Applications and wait for the whale icon before re-running

**`git clone` says "Permission denied (publickey)"**
- Redo Step 3 — your SSH key may not be saved to GitHub correctly
- Confirm you accepted the GitHub invite

---

[Back to main guide](../INSTALL.md)
