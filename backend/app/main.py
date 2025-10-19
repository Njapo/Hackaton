"""
main.py - FastAPI Application Entry Point

This is the main application file that initializes FastAPI and configures all routes.
Run this file to start the API server.
"""

from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List, Optional
import os
from dotenv import load_dotenv

from . import models, schemas, crud, auth
from .database import engine, get_db, init_db
from .ai_client import get_ai_response
from .skin_analyzer import analyze_skin_image, analyze_skin_image_with_confidence, analyze_and_extract

# Load environment variables
load_dotenv()

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=os.getenv("APP_NAME", "SkinAI"),
    version=os.getenv("APP_VERSION", "1.0.0"),
    description="AI-powered skin health analysis API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============= Startup Event =============

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
    print("✅ Database initialized")
    print("🚀 SkinAI API is running!")
    print(f"📚 API Documentation: http://localhost:8000/docs")


# ============= Root Endpoint =============

@app.get("/", tags=["Root"])
def read_root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to SkinAI API",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["Root"])
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "API is running smoothly"
    }


# ============= Authentication Endpoints =============

@app.post("/api/auth/register", response_model=schemas.User, tags=["Authentication"])
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if email already exists
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    return crud.create_user(db=db, user=user)


@app.post("/api/auth/login", response_model=schemas.Token, tags=["Authentication"])
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login and get access token (OAuth2 compatible - use email in username field)."""
    # The form_data.username field should contain the email
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/api/auth/login/json", response_model=schemas.Token, tags=["Authentication"])
def login_json(
    login_request: schemas.LoginRequest,
    db: Session = Depends(get_db)
):
    """Login with JSON body (alternative to OAuth2 form)."""
    user = auth.authenticate_user(db, login_request.email, login_request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/auth/me", response_model=schemas.User, tags=["Authentication"])
async def get_current_user_info(
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get current user information."""
    return current_user


# ============= AI Analysis Endpoint =============

@app.post("/api/ai/skin-analysis", response_model=schemas.ChatMessage, tags=["AI"])
async def skin_analysis(
    image: UploadFile = File(...),
    symptoms: str = Form(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Analyzes a skin image and user-provided symptoms.
    1. The image is analyzed by a fine-tuned Hugging Face model for disease prediction with confidence scores.
    2. The top predictions and user symptoms are sent to Gemini AI for detailed analysis.
    """
    # 1. Analyze the image with the skin disease model (get top 5 predictions with confidence)
    predictions = analyze_skin_image_with_confidence(image, top_k=5)
    
    if predictions[0]["disease"] == "Could not analyze image":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze the provided image."
        )

    # Format predictions for the prompt
    predictions_text = "\n".join([
        f"  - {pred['disease']}: {pred['confidence']:.1%} confidence"
        for pred in predictions
    ])
    
    top_prediction = predictions[0]["disease"]
    top_confidence = predictions[0]["confidence"]

    # 2. Create a detailed prompt for Gemini with system instruction
    prompt = (
        f"SYSTEM INSTRUCTION:\n"
        f"You are SkinAI, an intelligent assistant specialized in skin disease detection and dermatology-related AI analysis.\n\n"
        f"Your role is to help users understand possible skin conditions from images or text descriptions. When analyzing an image or symptom description:\n\n"
        f"1. Provide a **specific, reasoned analysis** of what the condition might be — e.g., 'This pattern appears consistent with alopecia areata' or 'This looks similar to eczema or psoriasis.'\n"
        f"2. You may list **the most probable conditions (1–3 possibilities)** with short reasoning for each (texture, color, shape, or pattern).\n"
        f"3. Avoid vague or generic answers like 'consult a doctor.' Instead, focus on identifying possible conditions first.\n"
        f"4. Use clear and confident but responsible phrasing:\n"
        f"   - ✅ 'This appears consistent with...'\n"
        f"   - ✅ 'This resembles...'\n"
        f"   - ✅ 'This could indicate early signs of...'\n"
        f"5. After your detailed analysis, **end the message with a short disclaimer**, such as:\n"
        f"   > 'Note: This is an AI-based educational analysis. I recommend consulting a certified dermatologist for a precise diagnosis.'\n"
        f"6. Be concise, factual, and descriptive. If uncertain, describe possible differential diagnoses instead of refusing to answer.\n"
        f"7. You are NOT a doctor, but you are trained to recognize dermatological patterns in a research/AI context.\n\n"
        f"Your output should follow this format:\n"
        f"---\n"
        f"**Possible Condition:** [Condition Name]\n"
        f"**Reasoning:** [Why this condition matches the symptoms/image]\n"
        f"**Recommendation:** [Basic care suggestions]\n"
        f"**Note:** This is an AI-based educational analysis. Please consult a dermatologist for a professional diagnosis.\n"
        f"---\n\n"
        f"USER INPUT:\n"
        f"A specialized skin disease detection model analyzed a photo and returned these predictions:\n"
        f"{predictions_text}\n\n"
        f"The top prediction is: {top_prediction} (confidence: {top_confidence:.1%})\n\n"
        f"The user also described their symptoms as: '{symptoms}'\n\n"
        f"Based on the AI model's predictions (especially the top prediction) and the user's symptoms, "
        f"provide your detailed analysis following the format above."
    )

    # 3. Get the response from Gemini AI
    ai_response_dict = get_ai_response(prompt)
    
    # Extract the text from the response
    ai_response_text = ai_response_dict.get("response", "Unable to generate response")
    
    # Check if it's a safety block and generate a custom response
    finish_reason = ai_response_dict.get("finish_reason", "")
    if "safety_block" in finish_reason or "Unable to generate response" in ai_response_text:
        # Generate a custom response based on the predictions
        ai_response_text = (
            f"**Possible Condition:** {top_prediction}\n\n"
            f"**AI Model Analysis:**\n"
            f"The specialized skin disease detection model analyzed your image and provided these predictions:\n"
            f"{predictions_text}\n\n"
            f"**Your Symptoms:** {symptoms}\n\n"
            f"**Reasoning:** The AI model has identified this pattern with {top_confidence:.1%} confidence based on visual features in the image. "
            f"The model was trained on thousands of dermatological images to recognize patterns associated with various skin conditions.\n\n"
            f"**General Recommendations:**\n"
            f"1. 🩺 **Consult a dermatologist** - They can provide a proper clinical diagnosis and treatment plan\n"
            f"2. 🧼 **Keep the affected area clean** - Gently wash with mild, fragrance-free soap\n"
            f"3. 🚫 **Avoid scratching or picking** - This can lead to infection or scarring\n"
            f"4. 📸 **Document your symptoms** - Take daily photos to track changes\n"
            f"5. 💊 **Do NOT self-medicate** - Wait for professional medical advice before using any treatments\n\n"
            f"**Note:** This is an AI-based educational analysis. I recommend consulting a certified dermatologist for a precise diagnosis and treatment plan."
        )

    # 4. Save the interaction to the database
    chat_message_data = schemas.ChatMessageCreate(
        message=f"Symptoms: {symptoms} | Image Prediction: {top_prediction} ({top_confidence:.1%} confidence)",
        response=ai_response_text
    )
    db_message = crud.create_chat_message(db, chat_message_data, user_id=current_user.id)

    return db_message


# ============= Image Analysis ONLY Endpoint (No Gemini) =============

@app.post("/api/ai/analyze-image", tags=["AI"])
async def analyze_image_only(
    image: UploadFile = File(...),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Analyzes ONLY the skin image using the Hugging Face model.
    Does NOT use Gemini - just returns the raw prediction from the image model.
    Returns top 5 predictions with confidence scores.
    Useful for testing if the image analysis model is working correctly.
    """
    # Analyze the image with the skin disease model
    predictions = analyze_skin_image_with_confidence(image, top_k=5)
    
    if predictions[0]["disease"] == "Could not analyze image":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze the provided image."
        )

    return {
        "success": True,
        "predictions": predictions,
        "model_used": "Jayanth2002/dinov2-base-finetuned-SkinDisease",
        "message": "Image analysis complete. These are the top predictions from the Hugging Face model."
    }


# ============= User History Endpoint =============

@app.get("/api/ai/history", response_model=List[schemas.ChatMessage], tags=["AI"])
def get_user_history(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get the current user's chat history."""
    return crud.get_user_chat_messages(db, user_id=current_user.id)


# ============= Lesion Section Endpoints =============

@app.post("/api/sections/create", response_model=schemas.LesionSectionResponse, tags=["Lesion Sections"])
async def create_section(
    section: schemas.LesionSectionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Create a new lesion section for organizing different skin conditions.
    
    Lesion sections allow users to track multiple skin conditions separately.
    For example: "Facial acne", "Left arm rash", "Scalp condition", etc.
    
    Each section gets a unique UUID identifier and can have multiple history entries.
    """
    return crud.create_lesion_section(
        db, current_user.id, section.section_name, section.description
    )


@app.get("/api/sections", response_model=List[schemas.LesionSectionResponse], tags=["Lesion Sections"])
async def get_sections(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Get all lesion sections for the current user.
    
    Returns a list of all sections with their metadata including:
    - section_id (UUID)
    - section_name
    - description
    - created_at timestamp
    """
    return crud.get_user_sections(db, current_user.id)


@app.get("/api/sections/{section_id}", response_model=schemas.LesionSectionResponse, tags=["Lesion Sections"])
async def get_section(
    section_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Get details of a specific lesion section.
    
    Verifies that the section belongs to the current user.
    """
    section = crud.get_section_by_id(db, section_id)
    if not section or section.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Section not found")
    return section


@app.put("/api/sections/{section_id}", response_model=schemas.LesionSectionResponse, tags=["Lesion Sections"])
async def update_section(
    section_id: str,
    section_update: schemas.LesionSectionUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Update a lesion section's name or description.
    
    Only the section owner can update it.
    """
    section = crud.get_section_by_id(db, section_id)
    if not section or section.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Section not found")
    
    return crud.update_lesion_section(db, section_id, section_update)


@app.delete("/api/sections/{section_id}", tags=["Lesion Sections"])
async def delete_section(
    section_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Delete a lesion section and all its history entries.
    
    ⚠️ Warning: This will permanently delete all analysis history associated with this section!
    """
    section = crud.get_section_by_id(db, section_id)
    if not section or section.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Section not found")
    
    success = crud.delete_lesion_section(db, section_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete section")
    
    return {"message": "Section deleted successfully", "section_id": section_id}


# ============= Enhanced Analysis with Auto-Save =============

@app.post("/api/ai/analyze", tags=["AI"])
async def analyze_with_auto_save(
    image: UploadFile = File(..., description="Skin image to analyze"),
    section_id: Optional[str] = Form(None, description="UUID of the lesion section (optional)"),
    user_notes: Optional[str] = Form(None, description="User's notes about this entry"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Analyze image with DinoV2 model and automatically save to history.
    
    This endpoint:
    1. Extracts 768-dimensional embeddings from the image using DinoV2
    2. Predicts the top 5 possible skin conditions with confidence scores
    3. Automatically saves the analysis to the user's history
    4. Links to a lesion section if section_id is provided
    5. **Automatically detects if this is the first upload (baseline)**
    
    **Auto-Baseline Detection:**
    - If this is the FIRST upload for a section → automatically marks as baseline
    - All subsequent uploads → automatically marked as follow-ups
    - No need to manually set is_baseline!
    
    **Auto-Save Features:**
    - Every analysis is saved automatically
    - Embeddings stored for future similarity comparisons
    - Can be linked to a specific lesion section for tracking
    - Automatic baseline marking for first upload
    
    **Returns:** 
    - history_id: ID of the saved history entry
    - predictions: Top 5 disease predictions with confidence scores
    - embedding_extracted: Whether embedding was successfully extracted
    - section_id: The section this entry belongs to (if provided)
    - is_baseline: Whether this was marked as baseline (auto-detected)
    """
    from app.skin_analyzer import analyze_and_extract
    
    # Verify section exists and belongs to user if provided
    if section_id:
        section = crud.get_section_by_id(db, section_id)
        if not section or section.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Section not found")
        
        # AUTOMATIC BASELINE DETECTION
        # Check if this section already has any entries
        existing_entries = crud.get_section_history(db, section_id, skip=0, limit=1)
        is_baseline = len(existing_entries) == 0  # True if first upload, False otherwise
    else:
        # No section provided, not a baseline
        is_baseline = False
    
    # Extract predictions and embedding
    try:
        predictions, embedding = analyze_and_extract(image)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze image: {str(e)}"
        )
    
    if predictions[0]["disease"] == "Could not analyze image":
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze the provided image."
        )
    
    # For now, use a placeholder for image path (in production, implement proper file storage)
    import uuid
    image_filename = f"{uuid.uuid4()}_{image.filename}"
    image_path = f"/uploads/{image_filename}"
    # TODO: Implement actual file saving logic here
    # Example: await save_upload_file(image, image_path)
    
    # Save to history automatically
    try:
        history_entry = crud.save_history_entry_enhanced(
            db=db,
            user_id=current_user.id,
            image_path=image_path,
            predictions=predictions,
            embedding=embedding,
            section_id=section_id,
            gemini_response=None,  # Will be generated during progress review
            is_baseline=is_baseline,
            user_notes=user_notes
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save history entry: {str(e)}"
        )
    
    return {
        "success": True,
        "history_id": history_entry.id,
        "predictions": predictions,
        "embedding_extracted": embedding is not None,
        "embedding_dimensions": len(embedding) if embedding else 0,
        "section_id": section_id,
        "is_baseline": is_baseline,
        "message": "Analysis completed and saved to history successfully",
        "timestamp": history_entry.timestamp.isoformat()
    }


# ============= Progress Review Endpoint =============

@app.post("/api/sections/{section_id}/progress-review", tags=["Progress Tracking"])
async def progress_review(
    section_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    🩺 Generate AI doctor-style progress assessment for a lesion section.
    
    **SIMPLE TO USE:** Just provide section_id - we automatically:
    - Get the LATEST (most recent) entry in this section
    - Compare it with ALL previous entries
    - Calculate healing scores using image embeddings
    - Generate doctor-style AI assessment via Gemini
    
    **How it works:**
    1. **Finds latest entry** - Automatically gets your most recent upload
    2. **Compares with history** - Analyzes ALL previous images in this section
    3. **Calculates healing scores** - Uses AI image embeddings (768-dim DinoV2 vectors)
    4. **Computes trend** - Determines if improving/stable/worsening
    5. **Generates report** - Doctor-style assessment from Gemini AI
    
    **Healing Score Explanation:**
    - 90-100%: Very similar to previous (minimal change)
    - 70-89%: Similar with minor differences
    - 50-69%: Moderate changes visible
    - Below 50%: Significant changes detected
    
    **Trend Detection:**
    - "improving": Healing scores increasing over time
    - "stable": Consistent condition
    - "worsening": Healing scores decreasing
    
    **When to use:**
    - After uploading a new follow-up image
    - To check treatment progress
    - To see how condition changed over time
    
    **Example Response:**
    ```json
    {
      "section_name": "Facial Acne",
      "latest_entry_date": "2025-10-19",
      "baseline_date": "2025-10-01",
      "comparisons": [
        {
          "previous_date": "2025-10-12",
          "healing_percentage": 78.5,
          "days_difference": 7
        }
      ],
      "average_healing_score": 78.5,
      "trend": "improving",
      "doctor_summary": "Based on image analysis, your condition shows improvement..."
    }
    ```
    """
    from app.progress_analyzer import (
        compute_comparisons, analyze_trend, generate_progress_prompt
    )
    
    # Get section and verify ownership
    section = crud.get_section_by_id(db, section_id)
    if not section or section.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Section not found")
    
    # Get ALL entries for this section, ordered by timestamp DESC (latest first)
    all_entries = crud.get_section_history(db, section_id, skip=0, limit=100)
    
    if len(all_entries) < 2:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough history. Section has {len(all_entries)} entry/entries. Need at least 2 to compare progress."
        )
    
    # Latest entry is the first one (most recent)
    current_entry = all_entries[0]
    
    # All previous entries (everything except the latest)
    previous_entries = all_entries[1:]
    
    # Compute comparisons and healing scores
    try:
        comparisons, avg_healing_score = compute_comparisons(current_entry, previous_entries)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compute comparisons: {str(e)}"
        )
    
    # Analyze trend
    healing_scores = [comp['healing_percentage'] for comp in comparisons]
    trend = analyze_trend(healing_scores) if healing_scores else 'stable'
    
    # Generate Gemini prompt
    try:
        prompt = generate_progress_prompt(
            current_entry,
            previous_entries,
            comparisons,
            avg_healing_score,
            trend,
            section.section_name
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate prompt: {str(e)}"
        )
    
    # Get doctor-style assessment from Gemini
    try:
        gemini_response = get_ai_response(prompt)
        doctor_summary = gemini_response.get("response", "Unable to generate assessment")
    except Exception as e:
        # Fallback if Gemini fails
        doctor_summary = (
            f"**Progress Analysis for {section.section_name}**\n\n"
            f"Average healing score: {avg_healing_score:.1f}%\n"
            f"Trend: {trend}\n\n"
            f"Based on image similarity analysis, your condition appears to be {trend}.\n\n"
            f"Note: AI assessment temporarily unavailable. Scores based on image embedding comparison."
        )
    
    # Update the latest history entry with Gemini response and healing score
    try:
        crud.update_history_gemini_response(
            db, current_entry.id, doctor_summary, avg_healing_score
        )
    except Exception as e:
        # Non-fatal error, continue with response
        pass
    
    # Get baseline entry
    baseline = crud.get_baseline_entry(db, section_id)
    
    return {
        "section_id": section_id,
        "section_name": section.section_name,
        "latest_entry_id": current_entry.id,
        "latest_entry_date": current_entry.timestamp.isoformat(),
        "baseline_entry_id": baseline.id if baseline else None,
        "baseline_date": baseline.timestamp.isoformat() if baseline else None,
        "total_entries": len(all_entries),
        "comparisons": comparisons,
        "average_healing_score": avg_healing_score,
        "doctor_summary": doctor_summary,
        "trend": trend
    }


# ============= Section History Endpoint =============

@app.get("/api/sections/{section_id}/history", tags=["Progress Tracking"])
async def get_section_history_endpoint(
    section_id: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Get all history entries for a specific lesion section.
    
    Returns chronological list of all analysis entries for tracking progress over time.
    
    **Each entry includes:**
    - Entry ID and timestamp
    - Top disease prediction with confidence score
    - Healing score (if available from progress review)
    - Image path
    - Whether it's marked as baseline
    
    **Use Cases:**
    - View timeline of condition progress
    - See all analysis results for a specific skin area
    - Track healing scores over time
    - Identify baseline and follow-up entries
    
    **Pagination:**
    - skip: Number of entries to skip (default: 0)
    - limit: Maximum entries to return (default: 50)
    """
    # Verify section belongs to user
    section = crud.get_section_by_id(db, section_id)
    if not section or section.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Section not found")
    
    entries = crud.get_section_history(db, section_id, skip, limit)
    
    # Transform to summary format
    summaries = []
    for entry in entries:
        top_pred = entry.disease_predictions[0] if entry.disease_predictions else {}
        summaries.append({
            "id": entry.id,
            "timestamp": entry.timestamp.isoformat(),
            "top_prediction": top_pred.get("disease", "Unknown"),
            "top_confidence": top_pred.get("confidence", 0),
            "healing_score": entry.healing_score,
            "image_path": entry.image_path,
            "is_baseline": entry.is_baseline,
            "has_gemini_response": entry.gemini_response is not None,
            "user_notes": entry.user_notes
        })
    
    return {
        "section_id": section_id,
        "section_name": section.section_name,
        "total_entries": len(summaries),
        "entries": summaries
    }


# ============= Run Application =============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
