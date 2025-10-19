#!/bin/bash
# Complete fix script - run this in WSL

echo "🔧 Complete Fix Script for SkinAI"
echo "=================================="

cd ~/hackaton

echo ""
echo "1️⃣ Copying updated main.py..."
cp /mnt/c/Users/v-nikolozij/Desktop/Hackaton/backend/app/main.py ~/hackaton/app/main.py
echo "✅ main.py updated ($(wc -l < ~/hackaton/app/main.py) lines)"

echo ""
echo "2️⃣ Checking for auto-baseline code..."
if grep -q "AUTOMATIC BASELINE" ~/hackaton/app/main.py; then
    echo "✅ Auto-baseline detection code found!"
else
    echo "❌ Auto-baseline code NOT found - file may not be updated"
fi

echo ""
echo "3️⃣ Recreating database tables..."
source venv/bin/activate
python create_tables.py

echo ""
echo "4️⃣ Verifying database schema..."
python3 << 'PYTHON'
import sqlite3
conn = sqlite3.connect('skinai.db')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(history)")
for col in cursor.fetchall():
    if col[1] == 'gemini_response':
        is_nullable = not bool(col[3])
        status = "✅ NULLABLE" if is_nullable else "❌ NOT NULL"
        print(f"  gemini_response: {status}")
conn.close()
PYTHON

echo ""
echo "5️⃣ Starting server..."
echo "Server will start in 3 seconds..."
sleep 3
uvicorn app.main:app --reload --host 0.0.0.0

echo ""
echo "🎉 Done! Server should be running on http://localhost:8000"
