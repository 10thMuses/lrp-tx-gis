# Windows preflight for LRP GIS Claude Code setup.
# Run this once from PowerShell (Admin) on Windows. After it completes,
# all further work happens inside WSL2 / Ubuntu via the bash scripts.
#
# Usage:
#   1. Open PowerShell as Administrator (right-click PowerShell -> Run as administrator)
#   2. Allow script execution for this session:
#        Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
#   3. Run:
#        .\bootstrap-windows.ps1

$ErrorActionPreference = "Stop"

function Log($msg) {
    Write-Host "[bootstrap] $msg" -ForegroundColor Cyan
}

# 1. Check for WSL ---------------------------------------------------------
Log "Checking WSL2 status..."
$wslStatus = wsl --status 2>&1
if ($LASTEXITCODE -ne 0) {
    Log "WSL not installed. Installing now (will require a reboot)..."
    wsl --install -d Ubuntu
    Log "WSL install initiated. REBOOT YOUR MACHINE, then re-run this script."
    Log "After reboot, Ubuntu will finish setup and prompt for a username + password."
    Log "Once Ubuntu is set up, re-run: .\bootstrap-windows.ps1"
    exit 0
}
Log "WSL2 is installed."

# 2. Confirm Ubuntu distribution exists -----------------------------------
$distros = wsl --list --quiet
if ($distros -notmatch "Ubuntu") {
    Log "Ubuntu not found in WSL. Installing..."
    wsl --install -d Ubuntu
    Log "Ubuntu install initiated. Open the Ubuntu app from Start Menu to finish setup."
    Log "Then re-run this script."
    exit 0
}
Log "Ubuntu distro found."

# 3. Locate the repo directory --------------------------------------------
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoDir = Join-Path $scriptDir "lrp-tx-gis"
$envSrc  = Join-Path $scriptDir ".env"
$envDst  = Join-Path $repoDir ".env"

if (-not (Test-Path $repoDir)) {
    Log "ERROR: lrp-tx-gis/ folder not found next to this script."
    Log "       Make sure you unzipped lrp-handoff.zip and ran this from inside lrp-handoff/."
    exit 1
}
Log "Repo folder found at: $repoDir"

# 4. Move .env into the repo if it's still in the handoff root ------------
if ((Test-Path $envSrc) -and -not (Test-Path $envDst)) {
    Move-Item $envSrc $envDst
    Log ".env moved into repo. (gitignored — will not be committed)"
} elseif (Test-Path $envDst) {
    Log ".env already present in repo."
} else {
    Log "WARN: no .env found at $envSrc or $envDst"
}

# 5. Convert the Windows path to a WSL path -------------------------------
# C:\Users\you\Code\lrp-handoff\lrp-tx-gis  ->  /mnt/c/Users/you/Code/lrp-handoff/lrp-tx-gis
$wslRepoPath = $repoDir -replace '^([A-Z]):\\', { "/mnt/" + $_.Groups[1].Value.ToLower() + "/" } -replace '\\', '/'
Log "WSL path to repo: $wslRepoPath"

# 6. Run the bash bootstrap inside WSL ------------------------------------
Log "Handing off to WSL Ubuntu for the bash bootstrap..."
Log "(You may be prompted for your Ubuntu sudo password to install tippecanoe.)"
Log ""

wsl -d Ubuntu -- bash -c "cd '$wslRepoPath' && bash scripts/bootstrap-claude-code.sh"

if ($LASTEXITCODE -ne 0) {
    Log "ERROR: bash bootstrap exited with code $LASTEXITCODE"
    exit $LASTEXITCODE
}

Log ""
Log "=== Windows preflight complete ==="
Log ""
Log "Next steps:"
Log "  1. Open .env in a text editor (e.g. notepad.exe $envDst) and"
Log "     paste your NETLIFY_PAT after 'NETLIFY_PAT='"
Log "  2. Open Ubuntu (Start Menu -> Ubuntu) and:"
Log "       cd $wslRepoPath"
Log "       python3 build.py    # verify built=26 errored=0"
Log "       claude              # launch Claude Code"
Log ""
Log "Or skip the manual step and run from PowerShell:"
Log "  wsl -d Ubuntu -- bash -c 'cd $wslRepoPath && python3 build.py'"
