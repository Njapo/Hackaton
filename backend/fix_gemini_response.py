#!/usr/bin/env python3
"""
Fix gemini_response column to allow NULL values
This allows saving history entries without generating Gemini response immediately
"""

import sqlite3

# Connect to database
conn = sqlite3.connect('/home/v-nikolozij/hackaton/skinai.db')
cursor = conn.cursor()

print("Fixing gemini_response column to allow NULL...")

try:
    # SQLite doesn't support ALTER COLUMN directly
    # We need to recreate the table with correct schema
    
    # 1. Create new table with correct schema
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            section_id VARCHAR(36),
            image_path VARCHAR(500) NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            disease_predictions JSON NOT NULL,
            dino_embedding JSON,
            gemini_response TEXT,  -- NOW NULLABLE!
            healing_score FLOAT,
            is_baseline BOOLEAN DEFAULT 0,
            user_notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (section_id) REFERENCES lesion_sections(section_id)
        )
    """)
    
    # 2. Copy data from old table
    cursor.execute("""
        INSERT INTO history_new 
        SELECT id, user_id, section_id, image_path, timestamp, 
               disease_predictions, dino_embedding, gemini_response, 
               healing_score, is_baseline, user_notes
        FROM history
    """)
    
    # 3. Drop old table
    cursor.execute("DROP TABLE history")
    
    # 4. Rename new table
    cursor.execute("ALTER TABLE history_new RENAME TO history")
    
    # 5. Recreate indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_user_id ON history(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_section_id ON history(section_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_timestamp ON history(timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_is_baseline ON history(is_baseline)")
    
    conn.commit()
    print("✅ Successfully fixed gemini_response column!")
    print("   gemini_response is now NULLABLE")
    
except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()

finally:
    conn.close()

print("\n🎉 Database fixed! You can now save history entries without gemini_response.")
