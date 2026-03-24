# VAST SE Toolkit — Installation Guide

## Prerequisites

| Requirement | Windows | macOS |
|---|---|---|
| Docker Desktop | ✅ Required | ✅ Required |
| Git | ✅ Required | ✅ Required |
| SSH key added to GitHub | ✅ Required | ✅ Required |
| Chrome / Edge | ✅ Recommended | ✅ Recommended |

> **Windows note:** Install [Git for Windows](https://git-scm.com/download/win) — this gives you Git Bash and SSH in one package. WSL2 is not required.

---

## Step 1 — Set up your SSH key for GitHub

You only do this once per machine.

**Check if you already have a key:**
```bash
ls ~/.ssh/id_ed25519.pub
```

**If not, generate one:**
```bash
ssh-keygen -t ed25519 -C "your-email@vast.com"
# Press Enter to accept defaults (no passphrase needed)
```

**Copy your public key:**
```bash
cat ~/.ssh/id_ed25519.pub
```

**Add it to GitHub:**
1. Go to [github.com/settings/ssh/new](https://github.com/settings/ssh/new)
2. Title: e.g. `My Work Laptop`
3. Paste your key → **Add SSH key**

**Verify it works:**
```bash
ssh -T git@github.com
# Should say: Hi kimosabie! You've successfully authenticated...
```

> **Windows:** Run these commands in **Git Bash** (installed with Git for Windows).

---

## Step 2 — Clone the repo

```bash
mkdir -p ~/projects
cd ~/projects
git clone git@github.com:kimosabie/vast-se-toolkit.git
cd vast-se-toolkit
```

---

## Step 3 — Run setup

```bash
./setup.sh
```

This script will:
- Verify your SSH and Docker setup
- Create required directories
- Build the Docker image (2–3 minutes on first run)
- Start the app and open your browser

> **Windows:** Run `setup.sh` in **Git Bash**. Make sure Docker Desktop is running first.

---

## Step 4 — Copy the launcher to your Desktop

**macOS:** Copy `Start VAST SE Toolkit.command` to your Desktop.
First time only: right-click → **Open** to grant execution permission.
After that, double-click to launch.

**Windows:** Copy `Start VAST SE Toolkit.ps1` to your Desktop.
Right-click → **Run with PowerShell** to launch.

> If PowerShell blocks execution, run once from an elevated PowerShell:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```

---

## Day-to-day use

Just double-click the launcher. It will:
1. Check if an update is available on GitHub
2. Prompt you to update (or skip)
3. Start the app and open http://localhost:8501

---

## Manual update

```bash
cd ~/projects/vast-se-toolkit
git pull
docker compose up --build -d
```

Your project database (`data/toolkit.db`) and generated configs (`outputs/`) are preserved across updates.

---

## Stopping the app

```bash
cd ~/projects/vast-se-toolkit
docker compose down
```

Or from Docker Desktop → find `vast-se-toolkit` → Stop.

---

## Backup

The app auto-backs up your project database daily to `~/vast-toolkit-backups/`.

You can change the backup location inside the app (Tab 1 → Settings), or manually:
```bash
cp ~/projects/vast-se-toolkit/data/toolkit.db ~/OneDrive/vast-toolkit-backup.db
```

---

## Troubleshooting

**App doesn't start / blank page**
```bash
docker compose logs --tail=50
```

**Port 8501 already in use**
```bash
docker compose down
docker compose up -d
```

**SSH key not working on Windows**

Make sure you're using **Git Bash** (not cmd or PowerShell) when running git commands. The SSH key at `~/.ssh/id_ed25519` in Git Bash maps to `C:\Users\YourName\.ssh\id_ed25519`.

**`git pull` says "Permission denied (publickey)"**

Your SSH key isn't added to GitHub, or you're using HTTPS instead of SSH.
Check the remote URL:
```bash
git remote -v
# Should show: git@github.com:kimosabie/vast-se-toolkit.git
# If it shows https://, fix it:
git remote set-url origin git@github.com:kimosabie/vast-se-toolkit.git
```
