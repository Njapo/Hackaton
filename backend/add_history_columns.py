from sqlalchemy import text
from app.database import engine

with engine.connect() as conn:
    # Add new columns to history table
    try:
        conn.execute(text("ALTER TABLE history ADD COLUMN section_id VARCHAR(36)"))
        print("✅ Added section_id column")
    except Exception as e:
        print(f"⚠️  section_id column already exists or error: {e}")
    
    try:
        conn.execute(text("ALTER TABLE history ADD COLUMN is_baseline BOOLEAN DEFAULT 0"))
        print("✅ Added is_baseline column")
    except Exception as e:
        print(f"⚠️  is_baseline column already exists or error: {e}")
    
    try:
        conn.execute(text("ALTER TABLE history ADD COLUMN user_notes TEXT"))
        print("✅ Added user_notes column")
    except Exception as e:
        print(f"⚠️  user_notes column already exists or error: {e}")
    
    conn.commit()
    print("✅ All columns added successfully!")
