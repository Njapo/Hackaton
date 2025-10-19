import subprocess
import os

print("=" * 50)
print("STARTING SKINAI SERVER")
print("=" * 50)

# Fix the .env file
print("\n1. Fixing .env file...")
os.system('wsl sed -i "s/animalai.db/skinai.db/g" ~/hackaton/.env')
print("   ✅ .env fixed")

# Kill any existing server
print("\n2. Killing existing servers...")
os.system('wsl pkill -f uvicorn')
print("   ✅ Killed")

# Start the server
print("\n3. Starting server...")
print("=" * 50)
subprocess.run(['wsl', 'bash', '-c', 'cd ~/hackaton && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0'])
