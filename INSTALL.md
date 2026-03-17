# VAST SE Toolkit — Installation Guide

## Prerequisites

| Requirement | Windows (WSL2) | macOS |
|---|---|---|
| Docker Desktop | ✅ Required | ✅ Required |
| WSL2 | ✅ Required | — |
| Git | ✅ Required | ✅ Required |
| Chrome / Edge | ✅ Recommended | ✅ Recommended |

---

## Windows (WSL2)

### 1 — Install prerequisites (once only)

Install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/).
During setup, enable **WSL2 backend** when prompted.

Open **WSL** (Ubuntu terminal) and confirm Docker works:
```bash
docker --version
docker compose version
```

### 2 — Clone the repo

```bash
mkdir -p ~/projects
cd ~/projects
git clone https://github.com/YOUR_ORG/vast-se-toolkit.git
cd vast-se-toolkit
```

### 3 — Create the data directory

```bash
mkdir -p data outputs
```

### 4 — Build and start

```bash
docker compose up --build -d
```

First build takes 2–3 minutes. Subsequent starts are instant.

### 5 — Open the app

Navigate to **http://localhost:8501** in your browser.

### 6 — Desktop launcher (optional)

Copy `Start VAST SE Toolkit.ps1` to your Windows Desktop.

To run it: **right-click → Run with PowerShell**.

> On first run Windows may prompt about execution policy. Select **Run anyway** or run once from an elevated PowerShell:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```

---

## macOS

### 1 — Install prerequisites (once only)

Install [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/).

Open Terminal and confirm:
```bash
docker --version
docker compose version
```

### 2 — Clone the repo

```bash
mkdir -p ~/projects
cd ~/projects
git clone https://github.com/YOUR_ORG/vast-se-toolkit.git
cd vast-se-toolkit
```

### 3 — Create the data directory

```bash
mkdir -p data outputs
```

### 4 — Build and start

```bash
docker compose up --build -d
```

### 5 — Open the app

Navigate to **http://localhost:8501** in your browser.

### 6 — Desktop launcher (optional)

Copy `Start VAST SE Toolkit.command` to your Desktop.

**First time only:** right-click → **Open** to grant execution permission.
After that, double-click to launch.

---

## Updating

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

**Syntax error after editing app.py**
```bash
docker compose exec vast-se-toolkit python3 -c "
import ast
with open('/app/app.py') as f: source = f.read()
try:
    ast.parse(source)
    print('Syntax OK')
except SyntaxError as e:
    print(f'SyntaxError at line {e.lineno}: {e.msg}')
"
```

**Mixed tabs/spaces after editing**
```bash
python3 -c "
with open('app.py', 'r') as f: content = f.read()
content = content.expandtabs(4)
with open('app.py', 'w') as f: f.write(content)
print('Done')
"
```
