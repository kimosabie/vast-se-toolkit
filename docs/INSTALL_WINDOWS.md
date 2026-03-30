# VAST SE Toolkit — Windows Install Guide

> **Before you start:** Make sure Kimo has added you to the GitHub repo and you've accepted the invite. See [INSTALL.md](../INSTALL.md).

> **Important:** All terminal commands in this guide must be run in **Git Bash** — not PowerShell or Command Prompt.

---

## Step 1 — Install Docker Desktop

1. Go to [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) and click **Download for Windows**
2. Run the installer — accept all defaults
3. Restart your computer if prompted
4. Open **Docker Desktop** from the Start Menu
5. Wait until the whale icon appears in your taskbar (bottom-right) and says **"Docker Desktop is running"**

> Docker must be running every time you use the toolkit.

---

## Step 2 — Install Git (and Git Bash)

1. Go to [git-scm.com/downloads](https://git-scm.com/downloads) and click **Download for Windows**
2. Run the installer — accept all defaults
3. After install, open **Git Bash** from the Start Menu to confirm it worked

> Git Bash is a small terminal that comes with Git. You'll use it for all commands in this guide — never use PowerShell or CMD for these steps.

---

## Step 3 — Set up your SSH key for GitHub

This is a one-time step so your PC can securely connect to GitHub.

Open **Git Bash** and follow the steps below.

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

> If you see *"Permission denied"* — check that you pasted the full key and saved it on GitHub.

---

## Step 4 — Download the toolkit

In **Git Bash**, run:

```bash
mkdir -p ~/projects
cd ~/projects
git clone git@github.com:kimosabie/vast-se-toolkit.git
cd vast-se-toolkit
```

This creates the toolkit in `C:\Users\YourName\projects\vast-se-toolkit\`.

> If you see *"Repository not found"* — the GitHub invite wasn't accepted yet. Go back to the [main guide](../INSTALL.md).

---

## Step 5 — Run setup

Make sure the Docker whale icon is visible in your taskbar, then in **Git Bash** run:

```bash
bash setup.sh
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

## Step 7 — Set up the Desktop launcher *(optional)*

This lets you start the toolkit with a double-click.

1. Open **File Explorer** → navigate to `C:\Users\YourName\projects\vast-se-toolkit\`
2. Copy **`Start VAST SE Toolkit.ps1`** to your Desktop
3. Right-click it → **Run with PowerShell**

> If Windows blocks the script, open PowerShell as Administrator and run:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```
> Then try the launcher again.

---

## Closing the app

**Just close the browser tab — that's it.** The app keeps running in the background, ready for next time.

The Desktop launcher handles everything when you double-click it again:
- If Docker Desktop isn't running, it starts it automatically
- If the container stopped, it restarts it
- Your data is always safe regardless

**To fully stop the app** (frees memory — optional), in Git Bash:
```bash
cd ~/projects/vast-se-toolkit
docker compose down
```
Or open **Docker Desktop** → find `vast-se-toolkit` → click Stop.

---

## Troubleshooting

**Blank page or "This site can't be reached"**
- Check the whale icon is showing in your taskbar
- Wait 30 seconds and refresh the page
- Check logs in Git Bash: `docker compose logs --tail=50`

**`bash setup.sh` says "Docker is not running"**
- Open Docker Desktop from the Start Menu and wait for the whale icon before re-running

**`git clone` says "Permission denied (publickey)"**
- Redo Step 3 — your SSH key may not be saved to GitHub correctly
- Confirm you accepted the GitHub invite
- Make sure you're running the command in **Git Bash**, not PowerShell or CMD

**Git commands don't work in PowerShell or CMD**
- Always use **Git Bash** for all commands in this guide

---

[Back to main guide](../INSTALL.md)
