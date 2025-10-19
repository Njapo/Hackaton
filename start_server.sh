#!/bin/bash

echo "🔧 COMPLETE FIX SCRIPT"
echo "====================="

cd ~/hackaton

echo ""
echo "1️⃣  Copying fixed database.py..."
cp /mnt/c/Users/v-nikolozij/Desktop/Hackaton/backend/app/database.py ~/hackaton/app/database.py
echo "✅ database.py copied (now uses skinai.db)"

echo ""
echo "2️⃣  Activating venv..."
source venv/bin/activate

echo ""
echo "3️⃣  Testing database connection..."
python -c "
from app.database import SessionLocal
from app.models import User

db = SessionLocal()
users = db.query(User).all()
print(f'Found {len(users)} users in skinai.db:')
for u in users:
    print(f'  - {u.email}')
db.close()
"

echo ""
echo "4️⃣  Starting server..."
uvicorn app.main:app --reload --host 0.0.0.0
