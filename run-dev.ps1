# Dev runner: starts backend (uvicorn) and frontend (vite) in separate PowerShell windows.
# Usage: Right-click -> Run with PowerShell or run from PowerShell: .\run-dev.ps1

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path $root 'backend'
$frontendDir = Join-Path $root 'frontend'

Write-Host "Starting backend in new PowerShell window..."
$backendCmd = "cd `"$backendDir`"; if (Test-Path .\\venv\\Scripts\\Activate) { .\\venv\\Scripts\\Activate }; `".\\venv\\Scripts\\python.exe`" -m uvicorn main:app --reload --reload-dir `"$backendDir`" --host 127.0.0.1 --port 8000 --log-level info"
Start-Process powershell -ArgumentList "-NoExit","-Command","$backendCmd"

Start-Sleep -Seconds 1
Write-Host "Starting frontend in new PowerShell window..."
$frontendCmd = "cd `"$frontendDir`"; npm run dev"
Start-Process powershell -ArgumentList "-NoExit","-Command","$frontendCmd"

Write-Host "Dev servers started. Backend: http://127.0.0.1:8000 | Frontend: see Vite output (usually http://localhost:5173)"
