# 🚀 Progress Tracking & Lesion Sections - Complete Implementation Guide

## Overview

This implementation adds comprehensive progress tracking to SkinAI with:
- ✅ **Automatic history saving** for all analyses
- ✅ **Lesion sections** for organizing multiple conditions
- ✅ **Healing score computation** using embedding similarity
- ✅ **Doctor-style progress assessments** via Gemini AI
- ✅ **Trend analysis** (improving/stable/worsening)

---

## 📋 New Database Models

### 1. LesionSection

Allows users to create separate tracking sections for different lesions:

```python
{
  "section_id": "uuid-string",
  "user_id": 123,
  "section_name": "Left arm rash",
  "description": "Appeared after contact with...",
  "is_baseline": false,
  "created_at": "2025-10-19T..."
}
```

### 2. Enhanced History

Now includes:
- `section_id` - Links to lesion section
- `is_baseline` - Marks first entry for comparison
- `user_notes` - User's text description
- `gemini_response` - Can be NULL initially (generated during progress review)

---

## 🔄 Complete Workflow

### Workflow 1: First-Time Analysis (Baseline)

```
User uploads image + notes
       ↓
Frontend calls: POST /api/sections/create
   → Creates new section
       ↓
Frontend calls: POST /api/ai/analyze
   → Saves to History with is_baseline=True
   → Returns predictions + embedding
       ↓
Display results (no progress review yet)
```

### Workflow 2: Follow-Up Analysis (Progress Tracking)

```
User uploads new image for existing section
       ↓
Frontend calls: POST /api/ai/analyze
   → Saves to History automatically
   → Returns predictions + embedding
       ↓
Frontend calls: POST /api/history/progress-review
   → Retrieves previous entries from same section
   → Computes healing scores (embedding similarity)
   → Generates Gemini doctor-style assessment
   → Updates gemini_response in database
       ↓
Display progress report with:
   - Healing score
   - Trend (improving/stable/worsening)
   - Doctor-style summary
   - Before/after comparison
```

---

## 🎯 API Endpoints (To Be Added to main.py)

### 1. Create Lesion Section

```python
POST /api/sections/create

Request:
{
  "section_name": "Facial acne",
  "description": "Ongoing since June 2025"
}

Response:
{
  "section_id": "uuid",
  "section_name": "Facial acne",
  "description": "Ongoing since June 2025",
  "created_at": "2025-10-19T..."
}
```

### 2. Get User's Sections

```python
GET /api/sections

Response:
[
  {
    "section_id": "uuid-1",
    "section_name": "Facial acne",
    "created_at": "...",
    "entry_count": 5
  },
  {
    "section_id": "uuid-2",
    "section_name": "Left arm rash",
    "created_at": "...",
    "entry_count": 3
  }
]
```

### 3. Enhanced Skin Analysis (Auto-Save)

```python
POST /api/ai/analyze

Request (multipart/form-data):
{
  "image": <file>,
  "section_id": "uuid" (optional),
  "user_notes": "Redness has decreased",
  "is_baseline": false
}

Response:
{
  "history_id": 123,
  "predictions": [
    {"disease": "Eczema", "confidence": 0.95},
    ...
  ],
  "embedding_extracted": true,
  "section_id": "uuid",
  "message": "Analysis saved successfully"
}
```

### 4. Progress Review

```python
POST /api/history/progress-review

Request:
{
  "section_id": "uuid",
  "current_history_id": 123,
  "include_last_n_entries": 3
}

Response:
{
  "current_entry_id": 123,
  "section_name": "Facial acne",
  "baseline_entry_id": 100,
  "comparisons": [
    {
      "previous_entry_id": 120,
      "previous_timestamp": "2025-10-15T...",
      "previous_top_disease": "Acne Vulgaris",
      "current_similarity": 0.82,
      "healing_percentage": 18.0
    },
    ...
  ],
  "average_healing_score": 22.5,
  "trend": "improving",
  "doctor_summary": "**PROGRESS ASSESSMENT - FACIAL ACNE**\n\n**Current Condition:**\n..."
}
```

### 5. Get Section History

```python
GET /api/sections/{section_id}/history

Response:
[
  {
    "id": 123,
    "timestamp": "2025-10-19T...",
    "top_prediction": "Eczema",
    "healing_score": 22.5,
    "is_baseline": false,
    "image_path": "/uploads/img123.jpg"
  },
  ...
]
```

---

## 💻 Implementation Steps

### Step 1: Copy Files to WSL

```bash
# Copy all updated files
wsl -d Ubuntu bash -c "cp /mnt/c/Users/v-nikolozij/Desktop/Hackaton/backend/app/models.py ~/hackaton/app/"
wsl -d Ubuntu bash -c "cp /mnt/c/Users/v-nikolozij/Desktop/Hackaton/backend/app/crud.py ~/hackaton/app/"
wsl -d Ubuntu bash -c "cp /mnt/c/Users/v-nikolozij/Desktop/Hackaton/backend/app/schemas.py ~/hackaton/app/"
wsl -d Ubuntu bash -c "cp /mnt/c/Users/v-nikolozij/Desktop/Hackaton/backend/app/skin_analyzer.py ~/hackaton/app/"
wsl -d Ubuntu bash -c "cp /mnt/c/Users/v-nikolozij/Desktop/Hackaton/backend/app/progress_analyzer.py ~/hackaton/app/"
wsl -d Ubuntu bash -c "cp -r /mnt/c/Users/v-nikolozij/Desktop/Hackaton/backend/alembic ~/hackaton/"
```

### Step 2: Install Dependencies

```bash
wsl -d Ubuntu bash -c "cd ~/hackaton && source venv/bin/activate && pip install numpy"
```

### Step 3: Run Migration

```bash
wsl -d Ubuntu bash -c "cd ~/hackaton && source venv/bin/activate && alembic upgrade head"
```

### Step 4: Verify Tables

```bash
wsl -d Ubuntu bash -c "cd ~/hackaton && source venv/bin/activate && python check_tables.py"
```

Expected output:
```
✅ Database Tables:
  - lesion_sections
  - history (with new columns: section_id, is_baseline, user_notes)
  ...
```

---

## 🔧 Key Functions

### Embedding Extraction

```python
from app.skin_analyzer import get_image_embedding

embedding = get_image_embedding(image_file, normalize=True)
# Returns: [0.1, 0.2, ..., 0.8]  # 768 dimensions
```

### Healing Score Computation

```python
from app.progress_analyzer import compute_healing_score, cosine_similarity

similarity = cosine_similarity(current_embedding, baseline_embedding)
healing_score = compute_healing_score(current_embedding, baseline_embedding)
# Returns: 0-100 (higher = more healing/improvement)
```

### Progress Analysis

```python
from app.progress_analyzer import compute_comparisons, analyze_trend

comparisons, avg_score = compute_comparisons(current_entry, previous_entries)
trend = analyze_trend([entry.healing_score for entry in entries])
# Returns: 'improving', 'stable', or 'worsening'
```

---

## 🎨 Frontend Integration

### Create Section

```javascript
async function createSection(sectionName, description) {
  const response = await fetch('/api/sections/create', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ section_name: sectionName, description })
  });
  return await response.json();
}
```

### Upload Image for Analysis

```javascript
async function analyzeImage(imageFile, sectionId, notes, isBaseline = false) {
  const formData = new FormData();
  formData.append('image', imageFile);
  if (sectionId) formData.append('section_id', sectionId);
  if (notes) formData.append('user_notes', notes);
  formData.append('is_baseline', isBaseline);
  
  const response = await fetch('/api/ai/analyze', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
    body: formData
  });
  return await response.json();
}
```

### Request Progress Review

```javascript
async function getProgressReview(sectionId, currentHistoryId) {
  const response = await fetch('/api/history/progress-review', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      section_id: sectionId,
      current_history_id: currentHistoryId,
      include_last_n_entries: 3
    })
  });
  return await response.json();
}
```

---

## 🧪 Testing

### Test 1: Create Section

```python
from app import crud
from app.database import SessionLocal

db = SessionLocal()
section = crud.create_lesion_section(db, user_id=1, section_name="Test Rash")
print(f"✅ Created section: {section.section_id}")
```

### Test 2: Save History with Embedding

```python
from app.skin_analyzer import analyze_and_extract

# Analyze image
predictions, embedding = analyze_and_extract(image_file)

# Save to history
entry = crud.save_history_entry_enhanced(
    db=db,
    user_id=1,
    section_id=section.section_id,
    image_path="/test/img.jpg",
    predictions=predictions,
    embedding=embedding,
    is_baseline=True,
    user_notes="Initial entry"
)
print(f"✅ Saved entry: {entry.id}")
```

### Test 3: Compute Healing Score

```python
from app.progress_analyzer import compute_comparisons

# Get previous entries
previous = crud.get_recent_section_entries(db, section.section_id, limit=3)

# Compute comparisons
comparisons, avg_score = compute_comparisons(current_entry, previous)
print(f"✅ Average healing score: {avg_score:.1f}%")
```

---

## 📊 Database Schema Summary

```
users
  ├── lesion_sections (1:many)
  │     └── history (1:many)
  └── history (1:many)

lesion_sections
  - section_id (PK, UUID)
  - user_id (FK)
  - section_name
  - description
  - is_baseline
  - created_at

history
  - id (PK)
  - user_id (FK)
  - section_id (FK, nullable)
  - image_path
  - timestamp
  - disease_predictions (JSON)
  - dino_embedding (JSON/Vector)
  - gemini_response (nullable)
  - healing_score
  - is_baseline
  - user_notes
```

---

## ✅ Status

| Component | Status | Location |
|-----------|--------|----------|
| LesionSection Model | ✅ Done | `app/models.py` |
| Enhanced History Model | ✅ Done | `app/models.py` |
| CRUD Operations | ✅ Done | `app/crud.py` |
| Schemas | ✅ Done | `app/schemas.py` |
| Embedding Extraction | ✅ Done | `app/skin_analyzer.py` |
| Progress Analyzer | ✅ Done | `app/progress_analyzer.py` |
| Migration | ✅ Created | `alembic/versions/002_*.py` |
| API Endpoints | ⚠️ TODO | Need to add to `main.py` |

---

## 🚦 Next Steps

1. Run migration: `alembic upgrade head`
2. Add API endpoints to `main.py`
3. Update `.env` with `APP_NAME=SkinAI`
4. Test with real images
5. Integrate frontend UI

**Goal**: Fully automated history tracking with intelligent progress assessment for patient-like monitoring!
