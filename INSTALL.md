# VAST SE Toolkit — Install Guide

This guide will get the VAST SE Toolkit running on your laptop in about 10 minutes.
No prior experience with Docker or command lines needed — just follow each step in order.

---

## What you'll need

| Tool | What it does | Download |
|------|-------------|----------|
| **Docker Desktop** | Runs the app in a container | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) |
| **Git** | Downloads the code from GitHub | [git-scm.com/downloads](https://git-scm.com/downloads) |
| **GitHub account** | Needed to access the private repo | Ask Kimo to add you |

> **Windows users:** When installing Git, accept all the defaults. This installs **Git Bash** — a small terminal you'll use in the steps below.

---

## Step 1 — Install Docker Desktop

1. Go to [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) and download the installer for your OS.
2. Run the installer and follow the prompts.
3. Once installed, open **Docker Desktop** from your Applications / Start Menu.
4. Wait until the whale icon in your taskbar/menu bar shows **"Docker Desktop is running"**.

> Docker needs to be running every time you use the toolkit. If the whale icon is not there, open Docker Desktop first.

---

## Step 2 — Install Git

**macOS:**
Open Terminal (search "Terminal" in Spotlight) and run:
```bash
git --version
```
If Git is already installed you'll see a version number — skip to Step 3.
If not, macOS will prompt you to install Xcode Command Line Tools — click Install.

**Windows:**
Download and run the installer from [git-scm.com/downloads](https://git-scm.com/downloads).
Accept all defaults. After install, open **Git Bash** from your Start Menu to confirm it worked.

---

## Step 3 — Set up your SSH key for GitHub

This is a one-time step that lets your laptop talk to GitHub securely.

### 3a — Check if you already have a key

**macOS:** Open Terminal
**Windows:** Open Git Bash

Run:
```bash
ls ~/.ssh/id_ed25519.pub
```

- If you see a file path printed back — you already have a key. **Skip to step 3c.**
- If you see "No such file or directory" — continue to 3b.

### 3b — Generate a new SSH key

```bash
ssh-keygen -t ed25519 -C "your-email@vast.com"
```

- When asked "Enter file in which to save the key" — just press **Enter**
- When asked for a passphrase — just press **Enter** (twice)

### 3c — Copy your public key

```bash
cat ~/.ssh/id_ed25519.pub
```

This prints a long string starting with `ssh-ed25519 AAAA...` — **select all of it and copy it**.

### 3d — Add the key to GitHub

1. Go to [github.com/settings/ssh/new](https://github.com/settings/ssh/new) (you must be logged in)
2. **Title:** type something like `My Work Laptop`
3. **Key:** paste the string you copied
4. Click **Add SSH key**

### 3e — Verify it works

```bash
ssh -T git@github.com
```

You should see:
```
Hi yourname! You've successfully authenticated...
```

> If you see a "Permission denied" error, double-check that you pasted the full key and saved it on GitHub.

---

## Step 4 — Request access to the repo

The toolkit is in a private GitHub repository. You need to be added as a collaborator before you can download it.

1. **Find your GitHub username** — log in at [github.com](https://github.com) and it's shown in the top-right corner (e.g. `@johndoe`)
2. **Send Kimo a Slack message** with the following:

   > Hi Kimo, can you add me to the VAST SE Toolkit repo on GitHub? My username is: `your-github-username`

3. Kimo will add you and GitHub will send you an **email invitation** — open it and click **Accept invitation**
4. Once accepted, continue to Step 5

> Do not proceed to Step 5 until you have accepted the invite — the clone will fail with "Repository not found".

---

## Step 5 — Clone (download) the code

**macOS:** In Terminal
**Windows:** In Git Bash

```bash
mkdir -p ~/projects
cd ~/projects
git clone git@github.com:kimosabie/vast-se-toolkit.git
cd vast-se-toolkit
```

This creates a `vast-se-toolkit` folder inside `~/projects/`.

> If you see "Repository not found" — either the invite wasn't accepted yet, or the SSH key isn't set up correctly. Go back to Step 3.

---

## Step 6 — Run the setup script

Make sure **Docker Desktop is running** first (whale icon visible).

Then run:

```bash
./setup.sh
```

The script will:
1. Check your Git and Docker setup
2. Create the required folders
3. Build the Docker image — **this takes 2–3 minutes on the first run**
4. Start the app
5. Open your browser automatically (macOS)

When you see `=== Setup complete! ===` you're done.

> **Windows:** If you get "Permission denied" running `./setup.sh`, run `bash setup.sh` instead.

---

## Step 7 — Open the app

Open your browser and go to:

```
http://localhost:8501
```

You should see the VAST SE Toolkit home screen.

---

## Step 8 — Set up the Desktop launcher (optional but recommended)

This lets you start the toolkit with a double-click instead of using the terminal.

**macOS:**
1. Open Finder → navigate to `~/projects/vast-se-toolkit/`
2. Copy the file **`Start VAST SE Toolkit.command`** to your Desktop
3. The first time: **right-click it → Open** (macOS security requires this once)
4. After that, just double-click it to launch

**Windows:**
1. Open File Explorer → navigate to `C:\Users\YourName\projects\vast-se-toolkit\`
2. Copy **`Start VAST SE Toolkit.ps1`** to your Desktop
3. Right-click → **Run with PowerShell**

> If Windows blocks the script, open PowerShell as Administrator and run:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```
> Then try the launcher again.

---

## Day-to-day use

Once set up, just double-click the Desktop launcher. It will:
- Check for updates from GitHub
- Start the app
- Open `http://localhost:8501` in your browser

---

## Updating the app

When a new version is released:

```bash
cd ~/projects/vast-se-toolkit
git pull
docker compose up --build -d
```

Your saved projects and generated configs are **never affected by updates**.

---

## Stopping the app

```bash
cd ~/projects/vast-se-toolkit
docker compose down
```

Or open **Docker Desktop** → find `vast-se-toolkit` → click Stop.

---

## Troubleshooting

**The browser shows a blank page or "This site can't be reached"**
- Make sure Docker Desktop is running (whale icon in taskbar)
- Wait 30 seconds and refresh — the app takes a moment to start
- Check logs: `docker compose logs --tail=50`

**`./setup.sh` says "Docker is not running"**
- Open Docker Desktop and wait for it to fully start before re-running the script

**`git clone` says "Permission denied (publickey)"**
- Your SSH key isn't set up or wasn't added to GitHub — redo Step 3
- Make sure you accepted the GitHub repo invite (Step 4)

**Port 8501 already in use**
```bash
docker compose down
docker compose up -d
```

**On Windows, Git commands don't work in PowerShell or CMD**
- Always use **Git Bash** (installed with Git for Windows) for all commands in this guide

---

## Need help?

Ping **Kimo** on Slack.
