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
from typing import List
import os
from dotenv import load_dotenv

from . import models, schemas, crud, auth
from .database import engine, get_db, init_db
from .ai_client import get_ai_response
from .skin_analyzer import analyze_skin_image, analyze_skin_image_with_confidence

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


# ============= Run Application =============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
