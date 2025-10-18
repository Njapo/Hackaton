@echo off
wsl -d Ubuntu -e bash -c "cd ~/hackaton && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0"
