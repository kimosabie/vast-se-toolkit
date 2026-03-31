# =============================================================
# VAST SE Toolkit - Windows Launcher
# Right-click -> Run with PowerShell to start the app.
# Copy to Desktop for easy use.
# =============================================================

Add-Type -AssemblyName System.Windows.Forms

# -- Start Docker Desktop if not running ----------------------
$dockerOK = $false
try {
    docker info 2>$null | Out-Null
    $dockerOK = $true
} catch {}

if (-not $dockerOK) {
    Write-Host "Docker Desktop is not running - starting it..."

    $dockerExe = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    if (Test-Path $dockerExe) {
        Start-Process $dockerExe
    } else {
        Start-Process "Docker Desktop"
    }

    # Wait up to 90 seconds for Docker to become ready
    $waited = 0
    while ($waited -lt 90) {
        Start-Sleep -Seconds 3
        $waited += 3
        try {
            docker info 2>$null | Out-Null
            $dockerOK = $true
            break
        } catch {}
        Write-Host "Waiting for Docker Desktop... ($waited s)"
    }

    if (-not $dockerOK) {
        [System.Windows.Forms.MessageBox]::Show(
            "Docker Desktop did not start in time.`n`nPlease open Docker Desktop manually and try again.",
            "VAST SE Toolkit",
            [System.Windows.Forms.MessageBoxButtons]::OK,
            [System.Windows.Forms.MessageBoxIcon]::Error
        ) | Out-Null
        exit 1
    }

    Write-Host "Docker Desktop is ready."
}

# -- All repo operations run inside WSL2 ----------------------
# Git SSH keys and docker compose live in the Ubuntu environment.

$repoPath = "~/projects/vast-se-toolkit"

# Check for updates
Write-Host "Checking for updates..."
$fetchResult = wsl -d Ubuntu -- bash -c "cd $repoPath && git fetch origin main 2>&1 && echo OK"
if ($fetchResult -match "OK") {
    $status = wsl -d Ubuntu -- bash -c "cd $repoPath && git rev-parse HEAD && git rev-parse origin/main"
    $lines = $status -split "`n" | Where-Object { $_ -match '\S' }
    if ($lines.Count -ge 2 -and $lines[0].Trim() -ne $lines[1].Trim()) {
        $result = [System.Windows.Forms.MessageBox]::Show(
            "An update is available for VAST SE Toolkit.`n`nUpdate now? This takes about 1-2 minutes.",
            "VAST SE Toolkit Update",
            [System.Windows.Forms.MessageBoxButtons]::YesNo,
            [System.Windows.Forms.MessageBoxIcon]::Information
        )
        if ($result -eq [System.Windows.Forms.DialogResult]::Yes) {
            Write-Host "Pulling latest changes..."
            wsl -d Ubuntu -- bash -c "cd $repoPath && git pull origin main"
            Write-Host "Rebuilding image..."
            wsl -d Ubuntu -- bash -c "cd $repoPath && docker compose up --build -d"
            Write-Host "Update complete."
        } else {
            wsl -d Ubuntu -- bash -c "cd $repoPath && docker compose up -d"
        }
    } else {
        Write-Host "Already up to date."
        wsl -d Ubuntu -- bash -c "cd $repoPath && docker compose up -d"
    }
} else {
    Write-Host "Could not reach GitHub (offline?). Starting existing version."
    wsl -d Ubuntu -- bash -c "cd $repoPath && docker compose up -d"
}

# -- Wait for app and open browser ----------------------------
Write-Host "Starting VAST SE Toolkit..."
$ready = $false
for ($i = 0; $i -lt 20; $i++) {
    try {
        Invoke-WebRequest -Uri "http://localhost:8501/_stcore/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop | Out-Null
        $ready = $true
        break
    } catch {}
    Start-Sleep -Seconds 2
}

Start-Process "http://localhost:8501"

if (-not $ready) {
    Write-Host "App may still be starting - opening browser anyway."
}
