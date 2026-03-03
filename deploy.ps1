# Deploy HP Prime app to target directories
$ErrorActionPreference = "Stop"

# Find the .hpappdir directory in the script's folder
$appDir = Get-ChildItem -Path $PSScriptRoot -Directory -Filter "*.hpappdir" | Select-Object -First 1
if (-not $appDir) {
    Write-Error "No .hpappdir directory found in $PSScriptRoot"
    exit 1
}
$appName = $appDir.Name

$source = Join-Path $PSScriptRoot $appName

$targets = @(
    "$env:USERPROFILE\Documents\HP Connectivity Kit\Calculators\HP Prime\$appName",
    "$env:USERPROFILE\Documents\HP Connectivity Kit\Content\$appName",
    "$env:USERPROFILE\Documents\HP Prime\Calculators\Prime\$appName"
)

$apps = @(
    "C:\Program Files\HP\HP Prime Virtual Calculator\HPPrime.exe",
    "C:\Program Files\HP\HP Connectivity Kit\ConnectivityKit.exe"
)

if (-not (Test-Path $source)) {
    Write-Error "Source not found: $source"
    exit 1
}

# Stop HP processes
foreach ($app in $apps) {
    $procName = [System.IO.Path]::GetFileNameWithoutExtension($app)
    $proc = Get-Process -Name $procName -ErrorAction SilentlyContinue
    if ($proc) {
        Write-Host "Stopping $procName" -ForegroundColor Yellow
        $proc | Stop-Process -Force
        $proc | Wait-Process -ErrorAction SilentlyContinue
    }
}

foreach ($target in $targets) {
    if (Test-Path $target) {
        Write-Host "Removing $target" -ForegroundColor Yellow
        Remove-Item -Path $target -Recurse -Force
    }

    $parentDir = Split-Path $target -Parent
    if (-not (Test-Path $parentDir)) {
        Write-Host "Creating parent directory: $parentDir" -ForegroundColor Cyan
        New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
    }

    Write-Host "Copying to $target" -ForegroundColor Green
    Copy-Item -Path $source -Destination $target -Recurse -Force

    # Remove __pycache__ directories from the target
    Get-ChildItem -Path $target -Directory -Filter "__pycache__" -Recurse | Remove-Item -Recurse -Force
}

# Restart HP processes
foreach ($app in $apps) {
    if (Test-Path $app) {
        Write-Host "Starting $app" -ForegroundColor Cyan
        Start-Process -FilePath $app
    }
}

# Bring HP Prime Virtual Calculator to foreground
# Alt-key trick: simulating Alt press allows SetForegroundWindow to work
if (-not ('FgWindow' -as [type])) {
    Add-Type @"
using System;
using System.Runtime.InteropServices;
public class FgWindow {
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, int dwExtraInfo);
    public static void Activate(IntPtr hwnd) {
        keybd_event(0xA4, 0, 0, 0);           // Alt down
        keybd_event(0xA4, 0, 2, 0);           // Alt up
        SetForegroundWindow(hwnd);
    }
}
"@
}
for ($i = 0; $i -lt 10; $i++) {
    Start-Sleep -Milliseconds 500
    $emulator = Get-Process -Name "HPPrime" -ErrorAction SilentlyContinue
    if ($emulator -and $emulator.MainWindowHandle -ne [IntPtr]::Zero) {
        [FgWindow]::Activate($emulator.MainWindowHandle)
        Write-Host "Brought HP Prime to foreground." -ForegroundColor Cyan
        break
    }
}

Write-Host "`nDeployment complete." -ForegroundColor Green
