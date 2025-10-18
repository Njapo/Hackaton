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
from .skin_analyzer import analyze_skin_image

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
    1. The image is analyzed by a fine-tuned image model for disease prediction.
    2. The prediction and user symptoms are sent to a generative AI for a detailed response.
    """
    # 1. Analyze the image with the skin disease model
    predicted_disease = analyze_skin_image(image)
    
    if "Could not analyze image" in predicted_disease:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze the provided image."
        )

    # 2. Create a prompt for the generative AI
    prompt = (
        f"A user is asking about a skin condition. "
        f"A machine learning model analyzed a photo they provided and predicted the following condition: '{predicted_disease}'. "
        f"The user also described their symptoms as: '{symptoms}'.\n\n"
        f"Based on the model's prediction and the user's symptoms, provide a helpful, "
        f"informative, and safe response. IMPORTANT: Start the response with a clear disclaimer that you are an AI, "
        f"not a medical professional, and that this is not a diagnosis. Advise the user to consult a doctor. "
        f"Then, you can provide some general information about the predicted condition."
    )

    # 3. Get the response from the generative AI
    ai_response_dict = get_ai_response(prompt)
    
    # Extract the text from the response
    ai_response_text = ai_response_dict.get("response", "Unable to generate response")
    
    # Check if it's a safety block and generate a custom response
    finish_reason = ai_response_dict.get("finish_reason", "")
    if "safety_block" in finish_reason or "Unable to generate response" in ai_response_text:
        # Generate a custom response based on the prediction
        ai_response_text = (
            f"⚠️ **IMPORTANT MEDICAL DISCLAIMER**: I am an AI assistant, not a medical professional. "
            f"This is NOT a medical diagnosis. Please consult a licensed dermatologist or doctor for proper diagnosis and treatment.\n\n"
            f"**Image Analysis Result**: The AI model has identified your condition as potentially related to **{predicted_disease}**.\n\n"
            f"**Your Symptoms**: {symptoms}\n\n"
            f"**General Recommendations**:\n"
            f"1. 🩺 **Consult a dermatologist immediately** - They can provide a proper diagnosis and treatment plan\n"
            f"2. 🧼 **Keep the affected area clean** - Gently wash with mild, fragrance-free soap\n"
            f"3. 🚫 **Avoid scratching or picking** - This can lead to infection or scarring\n"
            f"4. 📸 **Document your symptoms** - Take daily photos to track changes\n"
            f"5. 💊 **Do NOT self-medicate** - Wait for professional medical advice before using any treatments\n\n"
            f"**Next Steps**: Schedule an appointment with a dermatologist as soon as possible. "
            f"Bring your symptom documentation and mention that an AI analysis suggested {predicted_disease}. "
            f"A medical professional can confirm the diagnosis and recommend appropriate treatment."
        )

    # 4. Save the interaction to the database
    chat_message_data = schemas.ChatMessageCreate(
        message=f"Symptoms: {symptoms} | Image Prediction: {predicted_disease}",
        response=ai_response_text
    )
    db_message = crud.create_chat_message(db, chat_message_data, user_id=current_user.id)

    return db_message


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
