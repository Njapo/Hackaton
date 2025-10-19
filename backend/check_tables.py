from sqlalchemy import inspect
from app.database import engine

inspector = inspect(engine)
tables = inspector.get_table_names()

print("✅ Database Tables:")
for table in tables:
    print(f"  - {table}")
    columns = inspector.get_columns(table)
    for col in columns:
        print(f"      {col['name']}: {col['type']}")
