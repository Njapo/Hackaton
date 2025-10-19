from app.database import engine, Base
from app import models

# Create all tables
Base.metadata.create_all(bind=engine)
print("✅ All tables created successfully!")
