# 🔧 HOW TO FIX THE ERROR - MANUAL STEPS

## ⚠️ Current Problem
The server is running OLD code. The database was fixed but the Python code needs to be updated.

---

## ✅ SOLUTION - Run This Script

### Option 1: Use PowerShell Script (EASIEST)

1. **Open NEW PowerShell window** (close the stuck one)

2. **Navigate to backend folder:**
   ```powershell
   cd C:\Users\v-nikolozij\Desktop\Hackaton\backend
   ```

3. **Run the fix script:**
   ```powershell
   .\complete_fix.ps1
   ```

4. **Wait for server to start** (you'll see "✅ Database initialized")

5. **Test in Swagger:** http://localhost:8000/docs

---

### Option 2: Manual Steps (if script doesn't work)

#### Step 1: Copy Updated Code
```powershell
wsl cp /mnt/c/Users/v-nikolozij/Desktop/Hackaton/backend/app/main.py ~/hackaton/app/main.py
```

#### Step 2: Recreate Database
```powershell
wsl bash -c "cd ~/hackaton && source venv/bin/activate && python create_tables.py"
```

#### Step 3: Start Server
```powershell
wsl bash -c "cd ~/hackaton && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0"
```

---

## 🎯 What This Fixes

### 1. Updates main.py with:
- ✅ **Auto-baseline detection** (no need to pass `is_baseline`)
- ✅ **Removes `is_baseline` parameter** from endpoint
- ✅ **First upload** → automatically marked as baseline
- ✅ **Subsequent uploads** → automatically marked as follow-up

### 2. Database Schema:
- ✅ `gemini_response` column is **NULLABLE**
- ✅ Can save history without Gemini response
- ✅ Response added later during progress review

---

## 📊 After Running the Fix

### Test Upload (No more error!):
```bash
curl -X 'POST' \
  'http://localhost:8000/api/ai/analyze' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: multipart/form-data' \
  -F 'image=@your-image.jpeg' \
  -F 'section_id=9ec6b1a6-0ce8-4979-a21f-c48887661b5e' \
  -F 'user_notes=Red itches on my face'
```

**Note:** NO `is_baseline` parameter! ✨

### Expected Response:
```json
{
  "success": true,
  "history_id": 1,
  "predictions": [
    {"disease": "Herpes Simplex", "confidence": 0.318},
    ...
  ],
  "embedding_extracted": true,
  "embedding_dimensions": 768,
  "section_id": "9ec6b1a6-...",
  "is_baseline": true,  ← Automatically detected!
  "message": "Analysis completed and saved to history successfully"
}
```

---

## 🐛 If Still Getting Error

### Check 1: Verify Code Updated
```powershell
wsl grep -c "AUTOMATIC BASELINE" ~/hackaton/app/main.py
```
Should return a number > 0

### Check 2: Verify Database
```powershell
wsl bash -c "cd ~/hackaton && sqlite3 skinai.db 'PRAGMA table_info(history);' | grep gemini"
```
Should show gemini_response with NOT NULL = 0

### Check 3: Server Logs
Look for:
```
✅ Database initialized
🚀 SkinAI API is running!
```

---

## 💡 Quick Reference

| Issue | Command |
|-------|---------|
| Copy new code | `wsl cp /mnt/c/.../main.py ~/hackaton/app/main.py` |
| Recreate DB | `wsl bash -c "cd ~/hackaton && source venv/bin/activate && python create_tables.py"` |
| Start server | `wsl bash -c "cd ~/hackaton && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0"` |
| Check logs | Look for "✅ Database initialized" message |
| Test endpoint | http://localhost:8000/docs → POST /api/ai/analyze |

---

## ✅ Success Indicators

1. ✅ Server starts without errors
2. ✅ Upload works (no 500 error)
3. ✅ Response includes `"is_baseline": true/false`
4. ✅ No NOT NULL constraint error

---

## 🎉 After Success

You'll be able to:
- ✅ Upload images without errors
- ✅ Automatic baseline detection
- ✅ No need to manually set `is_baseline`
- ✅ Generate progress reports
- ✅ Track healing scores

**Just run the PowerShell script and it should all work!** 🚀
