# History Feature Setup Guide

## Overview

This guide explains how to set up the new **History** feature for tracking skin disease analyses with embeddings.

## Features

- ✅ Store complete analysis history (image, predictions, AI response)
- ✅ Support for vector embeddings (DinoV2 768-dim)
- ✅ PostgreSQL with pgvector OR SQLite fallback
- ✅ Healing score tracking over time
- ✅ Similarity search for comparing cases
- ✅ Alembic migrations for easy database updates

---

## Database Options

### Option 1: Continue with SQLite (Current Setup)

**Pros:**
- No additional setup needed
- Works immediately
- Good for development/testing

**Cons:**
- No efficient vector similarity search
- Limited scalability

**Setup:**
```bash
# In WSL
cd ~/hackaton
source venv/bin/activate

# Install new dependencies
pip install psycopg2-binary pgvector alembic

# Run migration (creates history table)
alembic upgrade head
```

### Option 2: Migrate to PostgreSQL (Recommended for Production)

**Pros:**
- ✅ Full pgvector support for embeddings
- ✅ Efficient cosine similarity search
- ✅ Better scalability and performance
- ✅ Production-ready

**Setup:**

#### 1. Install PostgreSQL

```bash
# In WSL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL
sudo service postgresql start

# Create database and user
sudo -u postgres psql
```

In PostgreSQL prompt:
```sql
CREATE DATABASE skinai_db;
CREATE USER skinai_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE skinai_db TO skinai_user;
\q
```

#### 2. Install pgvector extension

```bash
# Install pgvector
sudo apt install postgresql-server-dev-all
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install

# Enable extension in your database
sudo -u postgres psql -d skinai_db -c "CREATE EXTENSION vector;"
```

#### 3. Update .env file

```bash
# In WSL
cd ~/hackaton
nano .env
```

Change:
```env
# OLD
DATABASE_URL=sqlite:///./animalai.db

# NEW
DATABASE_URL=postgresql://skinai_user:your_secure_password@localhost/skinai_db
```

Also update:
```env
APP_NAME=SkinAI  # Change from AnimalAI
```

#### 4. Install Python dependencies and run migration

```bash
cd ~/hackaton
source venv/bin/activate

# Install PostgreSQL drivers
pip install psycopg2-binary pgvector alembic

# Run migration
alembic upgrade head
```

#### 5. Migrate existing data (Optional)

If you have existing users/data in SQLite:
```bash
# Export from SQLite
python migrate_data.py  # (create this script if needed)
```

---

## Database Schema

### History Table Structure

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer | Primary key (auto-increment) |
| `user_id` | Integer | Foreign key to users table |
| `image_path` | String(500) | Path/URL to uploaded image |
| `timestamp` | DateTime | When analysis was performed |
| `disease_predictions` | JSON | Array of predictions with confidence |
| `dino_embedding` | Vector(768) or JSON | DinoV2 image embedding |
| `gemini_response` | Text | Full AI-generated response |
| `healing_score` | Float | Optional healing progress score (0-100) |

---

## API Usage

### Save Analysis to History

```python
from app import crud

# After getting predictions and AI response
history_entry = crud.save_history_entry(
    db=db,
    user_id=current_user.id,
    image_path="/uploads/image_123.jpg",
    predictions=[
        {"disease": "Eczema", "confidence": 0.95},
        {"disease": "Dermatitis", "confidence": 0.03}
    ],
    embedding=[0.1, 0.2, ...],  # 768-dim vector from DinoV2
    gemini_response="This appears to be eczema...",
    healing_score=None  # Will be updated later
)
```

### Get User History

```python
# Get all history for a user
history = crud.get_user_history(db, user_id=1, skip=0, limit=50)

# Get specific entry
entry = crud.get_history_entry(db, history_id=123)
```

### Update Healing Score

```python
# Track healing progress
updated = crud.update_healing_score(db, history_id=123, healing_score=75.0)
```

### Find Similar Cases

```python
# Get similar historical cases
similar = crud.get_similar_cases(
    db, 
    user_id=1, 
    current_embedding=[...],
    limit=5
)
```

---

## Extracting Embeddings from DinoV2

You'll need to update `skin_analyzer.py` to extract embeddings:

```python
def get_image_embedding(image_file) -> List[float]:
    """
    Extract the 768-dim embedding vector from DinoV2 model.
    
    Returns:
        List of 768 float values representing the image embedding
    """
    try:
        image = Image.open(image_file.file).convert("RGB")
        inputs = processor(images=image, return_tensors="pt")
        
        with torch.no_grad():
            outputs = model(**inputs)
            # Get the hidden state (embedding) instead of logits
            # For DinoV2, use outputs.hidden_states[-1] or outputs.last_hidden_state
            embedding = outputs.hidden_states[-1].mean(dim=1).squeeze()
            
        return embedding.tolist()  # Convert to list of floats
        
    except Exception as e:
        print(f"Error extracting embedding: {e}")
        return None
```

---

## Alembic Commands

```bash
# Check current migration status
alembic current

# Create a new migration (after model changes)
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

---

## Next Steps

1. ✅ **Install dependencies**: `pip install psycopg2-binary pgvector alembic`
2. ✅ **Run migration**: `alembic upgrade head`
3. ⚠️ **Update main.py**: Integrate `save_history_entry()` into `/api/ai/skin-analysis`
4. ⚠️ **Add endpoint**: Create `/api/history` endpoint to retrieve user history
5. ⚠️ **Extract embeddings**: Update `skin_analyzer.py` to return embeddings
6. 🔄 **(Optional) Migrate to PostgreSQL** for better performance

---

## Testing

```bash
# Check if history table exists
# SQLite
sqlite3 animalai.db ".tables"

# PostgreSQL
psql -d skinai_db -c "\dt"

# Check history entries
# SQLite
sqlite3 animalai.db "SELECT * FROM history LIMIT 5;"

# PostgreSQL
psql -d skinai_db -c "SELECT * FROM history LIMIT 5;"
```

---

## Troubleshooting

### Migration fails with "table already exists"
```bash
# Mark current state without running migrations
alembic stamp head
```

### pgvector not found
```bash
# Install pgvector Python package
pip install pgvector

# Install PostgreSQL extension
sudo apt install postgresql-server-dev-all
git clone https://github.com/pgvector/pgvector.git
cd pgvector && make && sudo make install
```

### Import errors
```bash
# Reinstall requirements
pip install -r requirements.txt
```
