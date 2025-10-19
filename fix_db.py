from app.database import engine
from app.models import Base

print("🗑️  Dropping all tables...")
Base.metadata.drop_all(bind=engine)

print("📝 Creating all tables from models...")
Base.metadata.create_all(bind=engine)

print("✅ Database recreated successfully!")

# Verify
import sqlite3
conn = sqlite3.connect('skinai.db')
cursor = conn.cursor()
schema = cursor.execute('PRAGMA table_info(history)').fetchall()

print("\n=== HISTORY TABLE SCHEMA ===")
for col in schema:
    col_id, name, type_, notnull, default, pk = col
    null_str = "NOT NULL" if notnull else "NULL OK"
    print(f"{name:20} {type_:15} {null_str}")

gemini_col = [c for c in schema if c[1] == 'gemini_response']
if gemini_col:
    if gemini_col[0][3] == 0:
        print(f"\n✅ gemini_response is NULLABLE!")
    else:
        print(f"\n❌ gemini_response is still NOT NULL")
        
conn.close()
