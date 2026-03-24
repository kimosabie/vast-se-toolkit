# =============================================================
# VAST SE Toolkit — Windows Launcher
# Right-click → Run with PowerShell to start the app.
# Copy to Desktop for easy use.
# =============================================================

Add-Type -AssemblyName System.Windows.Forms

# Always run from the directory this script lives in (the repo)
$repoDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoDir

# ── Docker check ─────────────────────────────────────────────
$dockerOK = $false
try {
    docker info 2>$null | Out-Null
    $dockerOK = $true
} catch {}

if (-not $dockerOK) {
    [System.Windows.Forms.MessageBox]::Show(
        "Docker Desktop is not running.`n`nPlease start Docker Desktop and try again.",
        "VAST SE Toolkit",
        [System.Windows.Forms.MessageBoxButtons]::OK,
        [System.Windows.Forms.MessageBoxIcon]::Error
    ) | Out-Null
    exit 1
}

# ── Check for updates ─────────────────────────────────────────
Write-Host "Checking for updates..."
$fetchSuccess = $false
try {
    git fetch origin main 2>$null
    $fetchSuccess = $true
} catch {}

if ($fetchSuccess) {
    $local  = git rev-parse HEAD 2>$null
    $remote = git rev-parse origin/main 2>$null

    if ($local -ne $remote) {
        $result = [System.Windows.Forms.MessageBox]::Show(
            "An update is available for VAST SE Toolkit.`n`nUpdate now? This takes about 1–2 minutes.",
            "VAST SE Toolkit Update",
            [System.Windows.Forms.MessageBoxButtons]::YesNo,
            [System.Windows.Forms.MessageBoxIcon]::Information
        )
        if ($result -eq [System.Windows.Forms.DialogResult]::Yes) {
            Write-Host "Pulling latest changes..."
            git pull origin main
            Write-Host "Rebuilding image..."
            docker compose up --build -d
            Write-Host "Update complete."
        } else {
            docker compose up -d
        }
    } else {
        Write-Host "Already up to date."
        docker compose up -d
    }
} else {
    # Offline or SSH not available — just start existing version
    Write-Host "Could not reach GitHub (offline?). Starting existing version."
    docker compose up -d
}

# ── Wait for app and open browser ────────────────────────────
Write-Host "Starting VAST SE Toolkit..."
$ready = $false
for ($i = 0; $i -lt 20; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8501/_stcore/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        $ready = $true
        break
    } catch {}
    Start-Sleep -Seconds 2
}

Start-Process "http://localhost:8501"
