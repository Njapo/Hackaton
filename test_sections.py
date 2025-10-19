import subprocess
import sys

print("Testing the sections endpoint...")
print("=" * 60)

# Run the server in debug mode to see errors
cmd = 'wsl bash -c "cd ~/hackaton && source venv/bin/activate && python -c \\"from app.database import SessionLocal; from app.models import User; from app import crud; db = SessionLocal(); user = db.query(User).first(); print(f\'User ID: {user.id}\'); sections = crud.get_user_sections(db, user.id); print(f\'Sections: {sections}\'); db.close()\\""'

result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode)
