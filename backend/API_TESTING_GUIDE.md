# 🧪 API Testing Guide - New Progress Tracking Endpoints

## 🎉 ALL NEW ENDPOINTS ARE NOW LIVE IN SWAGGER!

Visit: **http://localhost:8000/docs**

You should now see **3 new endpoint groups** in Swagger:

1. **Lesion Sections** (6 endpoints) - Create and manage lesion sections
2. **Progress Tracking** (2 endpoints) - Generate progress reviews and view history
3. **AI** (Enhanced) - Updated analyze endpoint with auto-save

---

## 📋 Swagger Documentation Overview

### 🟢 Lesion Sections Tag

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/sections/create` | Create new lesion section |
| GET | `/api/sections` | Get all user's sections |
| GET | `/api/sections/{section_id}` | Get specific section |
| PUT | `/api/sections/{section_id}` | Update section |
| DELETE | `/api/sections/{section_id}` | Delete section |

### 🟡 Progress Tracking Tag

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/history/progress-review` | Generate AI progress report |
| GET | `/api/sections/{section_id}/history` | Get all entries for section |

### 🔵 AI Tag (Updated)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ai/analyze` | **NEW!** Analyze + auto-save with embeddings |
| POST | `/api/ai/skin-analysis` | Original Gemini analysis |
| POST | `/api/ai/analyze-image` | Image-only analysis |

---

## 🚀 Step-by-Step Testing Workflow

### Step 1: Login and Get Token

```bash
# Use Swagger UI at http://localhost:8000/docs
# Or curl:
curl -X POST "http://localhost:8000/api/auth/login/json" \
  -H "Content-Type: application/json" \
  -d '{"email": "your@email.com", "password": "yourpassword"}'
```

**Copy the `access_token` from response!**

### Step 2: Create a Lesion Section

In Swagger:
1. Click **🟢 Lesion Sections** → **POST /api/sections/create**
2. Click **"Try it out"**
3. Enter:
```json
{
  "section_name": "Facial Acne Treatment",
  "description": "Tracking acne on forehead area"
}
```
4. Click **Execute**

**Copy the `section_id` (UUID) from response!**

### Step 3: Upload Baseline Image

1. Click **🔵 AI** → **POST /api/ai/analyze**
2. Click **"Try it out"**
3. Fill in:
   - **image**: Upload a skin image
   - **section_id**: Paste your section UUID
   - **is_baseline**: `true`
   - **user_notes**: "Day 1 - baseline before treatment"
4. Click **Execute**

**Response will include:**
```json
{
  "success": true,
  "history_id": 1,
  "predictions": [
    {
      "disease": "Acne",
      "confidence": 0.89
    }
  ],
  "embedding_extracted": true,
  "embedding_dimensions": 768,
  "message": "Analysis completed and saved to history successfully"
}
```

### Step 4: Upload Follow-up Images

Wait a few days, then upload another image:

1. Same endpoint: **POST /api/ai/analyze**
2. Use same section_id
3. Set `is_baseline`: `false`
4. Add notes: "Day 7 - after applying treatment"

**Copy the `history_id` from response!**

### Step 5: Request Progress Review

1. Click **🟡 Progress Tracking** → **POST /api/history/progress-review**
2. Click **"Try it out"**
3. Enter:
```json
{
  "section_id": "your-section-uuid",
  "current_history_id": 2,
  "include_last_n_entries": 3
}
```
4. Click **Execute**

**You'll get a doctor-style report!**

```json
{
  "section_name": "Facial Acne Treatment",
  "average_healing_score": 78.5,
  "trend": "improving",
  "doctor_summary": "**Progress Assessment**\n\nBased on image analysis...",
  "comparisons": [
    {
      "previous_entry_id": 1,
      "similarity_score": 0.785,
      "healing_percentage": 78.5,
      "days_difference": 7
    }
  ]
}
```

### Step 6: View Section History

1. Click **🟡 Progress Tracking** → **GET /api/sections/{section_id}/history**
2. Paste your section_id
3. Click **Execute**

**See all entries with healing scores!**

---

## 🧪 Quick Test Scenarios

### Scenario 1: Track Multiple Conditions

```json
// Create sections for different areas
Section 1: "Left Arm Eczema"
Section 2: "Face Acne"
Section 3: "Scalp Psoriasis"

// Each section can have independent history and progress tracking!
```

### Scenario 2: Compare Progress Over Time

```
Day 1: Upload baseline (is_baseline=true)
Day 7: Upload follow-up
Day 14: Upload follow-up
Day 21: Upload follow-up → Request progress review

✅ Get healing scores comparing all entries
✅ See trend: improving/stable/worsening
✅ Get AI doctor-style assessment
```

### Scenario 3: Get All Sections

```bash
GET /api/sections

# Returns all your lesion sections with metadata
```

---

## 📊 Understanding Healing Scores

**How it works:**
- Compares 768-dimensional DinoV2 embeddings
- Uses cosine similarity (0-1 scale)
- Converted to percentage (0-100%)

**Interpretation:**
- **90-100%**: Very similar images (minimal change)
- **70-89%**: Similar with minor differences
- **50-69%**: Moderate changes detected
- **Below 50%**: Significant visual changes

**Trend Detection:**
- **Improving**: Scores increasing over time (condition improving)
- **Stable**: Consistent scores (no major changes)
- **Worsening**: Scores decreasing (condition deteriorating)

---

## 🔧 Troubleshooting

### Issue: "Section not found"
- Make sure you're using the correct `section_id` (UUID format)
- Verify the section belongs to your user

### Issue: "No previous entries found"
- You need at least 2 entries to generate progress review
- Upload a baseline image first

### Issue: "Failed to analyze image"
- Check image format (JPG, PNG)
- Image should be clear and properly lit
- Try a different image

### Issue: Endpoint not showing in Swagger
- Refresh the page: http://localhost:8000/docs
- Check server logs for errors
- Verify server is running: `http://localhost:8000/health`

---

## 🎯 API Response Examples

### Create Section Response
```json
{
  "section_id": "550e8400-e29b-41d4-a716-446655440000",
  "section_name": "Facial Acne Treatment",
  "description": "Tracking acne on forehead area",
  "created_at": "2025-10-19T10:30:00",
  "user_id": 1
}
```

### Analyze Response
```json
{
  "success": true,
  "history_id": 5,
  "predictions": [
    {"disease": "Acne", "confidence": 0.89},
    {"disease": "Rosacea", "confidence": 0.06},
    {"disease": "Dermatitis", "confidence": 0.03}
  ],
  "embedding_extracted": true,
  "embedding_dimensions": 768,
  "section_id": "550e8400-e29b-41d4-a716-446655440000",
  "is_baseline": false,
  "timestamp": "2025-10-19T10:35:00"
}
```

### Progress Review Response
```json
{
  "current_entry_id": 5,
  "section_name": "Facial Acne Treatment",
  "baseline_entry_id": 1,
  "comparisons": [
    {
      "previous_entry_id": 4,
      "previous_timestamp": "2025-10-12T10:00:00",
      "similarity_score": 0.82,
      "healing_percentage": 82.0,
      "days_difference": 7,
      "is_baseline": false
    },
    {
      "previous_entry_id": 1,
      "previous_timestamp": "2025-10-05T10:00:00",
      "similarity_score": 0.65,
      "healing_percentage": 65.0,
      "days_difference": 14,
      "is_baseline": true
    }
  ],
  "average_healing_score": 73.5,
  "doctor_summary": "**Progress Assessment for Facial Acne Treatment**\n\n...",
  "trend": "improving"
}
```

---

## ✅ All Features Now Live!

- ✅ Create/manage lesion sections
- ✅ Auto-save every analysis
- ✅ Extract 768-dim embeddings
- ✅ Compute healing scores
- ✅ Generate progress reviews
- ✅ Doctor-style AI assessments
- ✅ Trend analysis
- ✅ All visible in Swagger UI!

**🎉 Start testing at: http://localhost:8000/docs**
