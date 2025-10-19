wsl bash -c "sed -i 's/animalai.db/skinai.db/g' ~/hackaton/.env && cd ~/hackaton && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0"
