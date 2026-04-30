# SentiFlow Backend Test Runner

Write-Host "--- Initializing SentiFlow Test Suite ---" -ForegroundColor Cyan

if (Test-Path "venv") {
    Write-Host "Activating virtual environment..." -ForegroundColor Gray
    .\venv\Scripts\Activate.ps1
} else {
    Write-Host "Warning: venv not found. Running with global python." -ForegroundColor Yellow
}

Write-Host "Executing Pytest..." -ForegroundColor Cyan
python -m pytest tests/ -v

Write-Host "--- Test Sequence Complete ---" -ForegroundColor Cyan
