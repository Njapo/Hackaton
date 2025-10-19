# Complete Fix Script for Windows
# Run this in PowerShell

Write-Host "🔧 Complete Fix Script for SkinAI" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

Write-Host "`n1️⃣ Copying updated main.py to WSL..." -ForegroundColor Yellow
wsl cp /mnt/c/Users/v-nikolozij/Desktop/Hackaton/backend/app/main.py ~/hackaton/app/main.py

$lineCount = wsl wc -l ~/hackaton/app/main.py
Write-Host "✅ main.py updated: $lineCount" -ForegroundColor Green

Write-Host "`n2️⃣ Checking for auto-baseline code..." -ForegroundColor Yellow
$hasAutoBaseline = wsl grep -c "AUTOMATIC BASELINE" ~/hackaton/app/main.py
if ($hasAutoBaseline -gt 0) {
    Write-Host "✅ Auto-baseline detection code found!" -ForegroundColor Green
} else {
    Write-Host "❌ Auto-baseline code NOT found" -ForegroundColor Red
}

Write-Host "`n3️⃣ Recreating database tables..." -ForegroundColor Yellow
wsl bash -c "cd ~/hackaton && source venv/bin/activate && python create_tables.py"

Write-Host "`n4️⃣ Database is ready!" -ForegroundColor Green

Write-Host "`n5️⃣ Starting server..." -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server when done testing`n" -ForegroundColor Cyan

wsl bash -c "cd ~/hackaton && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0"
