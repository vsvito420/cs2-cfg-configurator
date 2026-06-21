#Requires -Version 5.1
<#
.SYNOPSIS
    Builds vsvito's CounterStrike2 CFG Configurator as a single Windows .exe with PyInstaller.

.DESCRIPTION
    - Checks for PyInstaller (installs via pip if missing).
    - Converts app/assets/icon.png -> icon.ico if ICO is missing.
    - Cleans previous build / dist / spec output.
    - Runs PyInstaller in --onefile --windowed mode.
    - Reports final EXE size and path.

.EXAMPLE
    .\build.ps1
    .\build.ps1 -OneDir
    .\build.ps1 -SkipIcon
#>

[CmdletBinding()]
param(
    [switch]$OneDir,
    [switch]$SkipIcon,
    [switch]$Clean
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $ProjectRoot

Write-Host ""
Write-Host "=== vsvito's CounterStrike2 CFG Configurator - Build Script ===" -ForegroundColor Cyan
Write-Host "Projektordner: $ProjectRoot" -ForegroundColor DarkGray
Write-Host ""

# --- 1. PyInstaller vorhanden? ------------------------------------------------
function Test-PyInstaller {
    try {
        $null = python -m PyInstaller --version 2>$null
        return $true
    }
    catch {
        return $false
    }
}

if (-not (Test-PyInstaller)) {
    Write-Host "[1/4] PyInstaller nicht gefunden -> installiere..." -ForegroundColor Yellow
    python -m pip install --upgrade pyinstaller | Out-Host
    if (-not (Test-PyInstaller)) {
        throw "PyInstaller konnte nicht installiert werden."
    }
}
else {
    $ver = python -m PyInstaller --version 2>$null
    Write-Host "[1/4] PyInstaller gefunden: $ver" -ForegroundColor Green
}

# --- 2. ICO erzeugen ----------------------------------------------------------
$IcoPath = Join-Path $ProjectRoot "app\assets\icon.ico"
$PngPath = Join-Path $ProjectRoot "app\assets\icon.png"

if (-not $SkipIcon) {
    if (Test-Path -LiteralPath $IcoPath) {
        Write-Host "[2/4] icon.ico vorhanden -> ueberspringe" -ForegroundColor DarkGray
    }
    elseif (Test-Path -LiteralPath $PngPath) {
        Write-Host "[2/4] Konvertiere icon.png -> icon.ico ..." -ForegroundColor Yellow
        python -c "from PIL import Image; Image.open(r'$PngPath').save(r'$IcoPath')"
        if (-not (Test-Path -LiteralPath $IcoPath)) {
            throw "ICO-Konvertierung fehlgeschlagen."
        }
    }
    else {
        Write-Host "[2/4] WARN: weder icon.png noch icon.ico gefunden -> Build ohne Icon" -ForegroundColor DarkYellow
        $script:IconArg = @()
    }
}
else {
    Write-Host "[2/4] Icon-Schritt uebersprungen (-SkipIcon)" -ForegroundColor DarkGray
}

if (-not $IconArg) {
    if (Test-Path -LiteralPath $IcoPath) {
        $script:IconArg = @("--icon", $IcoPath)
    }
    else {
        $script:IconArg = @()
    }
}

# --- 3. Vorherige Artefakte aufraeumen (optional) ----------------------------
if ($Clean) {
    Write-Host "[3/4] Raeume alte Build-Artefakte auf..." -ForegroundColor Yellow
    foreach ($d in @("build", "dist")) {
        $p = Join-Path $ProjectRoot $d
        if (Test-Path -LiteralPath $p) { Remove-Item -LiteralPath $p -Recurse -Force }
    }
    Get-ChildItem -Path $ProjectRoot -Filter "*.spec" -File -ErrorAction SilentlyContinue |
    Remove-Item -Force -ErrorAction SilentlyContinue
}
else {
    Write-Host "[3/4] Cleanup uebersprungen (ohne -Clean)" -ForegroundColor DarkGray
}

# --- 4. PyInstaller ausfuehren -----------------------------------------------
$mode = if ($OneDir) { "--onedir" } else { "--onefile" }
Write-Host "[4/4] Baue EXE ($mode) ..." -ForegroundColor Yellow

$pyiArgs = @(
    $mode,
    "--windowed",
    "--name", "CS2-CFG-Configurator",
    "--add-data", "app\assets;app\assets",
    "--add-data", "data;data",
    "--add-data", "configs;configs",
    "main.py"
) + $IconArg

python -m PyInstaller @pyiArgs
if ($LASTEXITCODE -ne 0) { throw "PyInstaller Build fehlgeschlagen." }

# --- Ergebnis -----------------------------------------------------------------
$ExePath = if ($OneDir) {
    Join-Path $ProjectRoot "dist\CS2-CFG-Configurator\CS2-CFG-Configurator.exe"
}
else {
    Join-Path $ProjectRoot "dist\CS2-CFG-Configurator.exe"
}

if (Test-Path -LiteralPath $ExePath) {
    $sizeMB = [math]::Round((Get-Item -LiteralPath $ExePath).Length / 1MB, 2)
    Write-Host ""
    Write-Host "=== Build erfolgreich ===" -ForegroundColor Green
    Write-Host ("EXE : {0}" -f $ExePath) -ForegroundColor Green
    Write-Host ("Size: {0} MB" -f $sizeMB) -ForegroundColor Green
}
else {
    throw "Build beendet, aber EXE wurde nicht gefunden: $ExePath"
}