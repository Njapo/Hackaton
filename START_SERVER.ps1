# PowerShell script to start the server
Write-Host "Starting SkinAI Server..." -ForegroundColor Green

# Copy the fixed database.py to WSL
Write-Host "Copying fixed database.py..." -ForegroundColor Yellow
wsl cp /mnt/c/Users/v-nikolozij/Desktop/Hackaton/backend/app/database.py ~/hackaton/app/database.py

# Start the server
Write-Host "Starting FastAPI server..." -ForegroundColor Yellow
wsl bash -c "cd ~/hackaton && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0"
