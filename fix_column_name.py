import sqlite3

conn = sqlite3.connect('skinai.db')
cursor = conn.cursor()

print("Renaming column section_description to description...")

# SQLite doesn't support RENAME COLUMN directly, need to recreate table
try:
    # Create new table with correct schema
    cursor.execute("""
        CREATE TABLE lesion_sections_new (
            section_id VARCHAR(36) PRIMARY KEY,
            user_id INTEGER NOT NULL,
            section_name VARCHAR(200) NOT NULL,
            description TEXT,
            is_baseline BOOLEAN DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Copy data
    cursor.execute("""
        INSERT INTO lesion_sections_new (section_id, user_id, section_name, description, created_at)
        SELECT section_id, user_id, section_name, section_description, created_at
        FROM lesion_sections
    """)
    
    # Drop old table
    cursor.execute("DROP TABLE lesion_sections")
    
    # Rename new table
    cursor.execute("ALTER TABLE lesion_sections_new RENAME TO lesion_sections")
    
    conn.commit()
    print("✅ Column renamed successfully!")
    
    # Verify
    schema = cursor.execute('PRAGMA table_info(lesion_sections)').fetchall()
    print("\n=== NEW SCHEMA ===")
    for col in schema:
        print(f"  - {col[1]} ({col[2]})")
        
except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()

conn.close()
