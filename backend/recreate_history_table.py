#!/usr/bin/env python3
"""
Recreate history table with correct schema (gemini_response nullable)
"""

import sqlite3
import sys

# Connect to database
conn = sqlite3.connect('/home/v-nikolozij/hackaton/skinai.db')
cursor = conn.cursor()

print("🔧 Fixing history table...")

try:
    # Check current schema
    cursor.execute("PRAGMA table_info(history)")
    columns = cursor.fetchall()
    
    print("\n📋 Current columns:")
    for col in columns:
        print(f"  - {col[1]}: {col[2]} (NOT NULL: {bool(col[3])})")
    
    # Backup existing data
    cursor.execute("SELECT COUNT(*) FROM history")
    count = cursor.fetchone()[0]
    print(f"\n📊 Found {count} existing records")
    
    if count > 0:
        print("⚠️  Backing up data...")
        cursor.execute("CREATE TABLE history_backup AS SELECT * FROM history")
    
    # Drop and recreate table
    print("🗑️  Dropping old table...")
    cursor.execute("DROP TABLE history")
    
    # Create new table with correct schema
    print("✨ Creating new table...")
    cursor.execute("""
        CREATE TABLE history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            section_id VARCHAR(36),
            image_path VARCHAR(500) NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            disease_predictions JSON NOT NULL,
            dino_embedding JSON,
            gemini_response TEXT,
            healing_score FLOAT,
            is_baseline BOOLEAN DEFAULT 0,
            user_notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (section_id) REFERENCES lesion_sections(section_id)
        )
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX idx_history_user_id ON history(user_id)")
    cursor.execute("CREATE INDEX idx_history_section_id ON history(section_id)")
    cursor.execute("CREATE INDEX idx_history_timestamp ON history(timestamp)")
    cursor.execute("CREATE INDEX idx_history_is_baseline ON history(is_baseline)")
    
    # Restore data if any
    if count > 0:
        print("📥 Restoring data...")
        cursor.execute("""
            INSERT INTO history 
            SELECT * FROM history_backup
        """)
        cursor.execute("DROP TABLE history_backup")
        print(f"✅ Restored {count} records")
    
    conn.commit()
    
    # Verify new schema
    print("\n✅ New schema:")
    cursor.execute("PRAGMA table_info(history)")
    for col in cursor.fetchall():
        if col[1] == 'gemini_response':
            print(f"  ✅ gemini_response: {col[2]} (NOT NULL: {bool(col[3])}) ← Should be False!")
    
    print("\n🎉 History table fixed successfully!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    conn.rollback()
    sys.exit(1)

finally:
    conn.close()
