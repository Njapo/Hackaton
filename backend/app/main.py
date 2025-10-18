"""
main.py - FastAPI Application Entry Point

This is the main application file that initializes FastAPI and configures all routes.
Run this file to start the API server.
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List
import os
from dotenv import load_dotenv

from . import models, schemas, crud, auth
from .database import engine, get_db, init_db
from .ai_client import get_ai_response

# Load environment variables
load_dotenv()

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=os.getenv("APP_NAME", "AnimalAI"),
    version=os.getenv("APP_VERSION", "1.0.0"),
    description="AI-powered animal care and management API",
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
    print("🚀 AnimalAI API is running!")
    print(f"📚 API Documentation: http://localhost:8000/docs")


# ============= Root Endpoint =============

@app.get("/", tags=["Root"])
def read_root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to AnimalAI API",
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
    login_request: schemas.LoginRequest,
    db: Session = Depends(get_db)
):
    """Login and get access token."""
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


# ============= User Endpoints =============

@app.get("/api/users", response_model=List[schemas.User], tags=["Users"])
def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get list of users (requires authentication)."""
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/api/users/{user_id}", response_model=schemas.User, tags=["Users"])
def get_user(
    user_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user by ID."""
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


# ============= Animal Endpoints =============

@app.get("/api/animals", response_model=List[schemas.Animal], tags=["Animals"])
def get_animals(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get list of all animals."""
    animals = crud.get_animals(db, skip=skip, limit=limit)
    return animals


@app.get("/api/animals/my", response_model=List[schemas.Animal], tags=["Animals"])
def get_my_animals(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's animals."""
    animals = crud.get_animals_by_owner(db, owner_id=current_user.id, skip=skip, limit=limit)
    return animals


@app.get("/api/animals/{animal_id}", response_model=schemas.Animal, tags=["Animals"])
def get_animal(
    animal_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get animal by ID."""
    db_animal = crud.get_animal(db, animal_id=animal_id)
    if db_animal is None:
        raise HTTPException(status_code=404, detail="Animal not found")
    return db_animal


@app.post("/api/animals", response_model=schemas.Animal, tags=["Animals"])
def create_animal(
    animal: schemas.AnimalCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new animal."""
    return crud.create_animal(db=db, animal=animal, owner_id=current_user.id)


@app.put("/api/animals/{animal_id}", response_model=schemas.Animal, tags=["Animals"])
def update_animal(
    animal_id: int,
    animal_update: schemas.AnimalUpdate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an animal."""
    db_animal = crud.get_animal(db, animal_id=animal_id)
    if db_animal is None:
        raise HTTPException(status_code=404, detail="Animal not found")
    
    # Check if user owns the animal
    if db_animal.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this animal")
    
    updated_animal = crud.update_animal(db, animal_id=animal_id, animal_update=animal_update)
    return updated_animal


@app.delete("/api/animals/{animal_id}", tags=["Animals"])
def delete_animal(
    animal_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete an animal."""
    db_animal = crud.get_animal(db, animal_id=animal_id)
    if db_animal is None:
        raise HTTPException(status_code=404, detail="Animal not found")
    
    # Check if user owns the animal
    if db_animal.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this animal")
    
    crud.delete_animal(db, animal_id=animal_id)
    return {"message": "Animal deleted successfully"}


# ============= ChatMessage Endpoints =============

@app.get("/api/chat/{animal_id}", response_model=List[schemas.ChatMessage], tags=["Chat"])
def get_chat_history(
    animal_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get chat history for an animal."""
    # Verify the animal belongs to the current user
    animal = crud.get_animal(db, animal_id=animal_id)
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    
    if animal.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this chat")
    
    messages = crud.get_chat_messages_by_animal(db, animal_id=animal_id, skip=skip, limit=limit)
    return messages


@app.post("/api/chat", response_model=schemas.ChatMessage, tags=["Chat"])
def create_chat_message(
    message: schemas.ChatMessageCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new chat message."""
    # Verify the animal belongs to the current user
    animal = crud.get_animal(db, animal_id=message.animal_id)
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    
    if animal.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to add messages for this animal")
    
    return crud.create_chat_message(db=db, message=message)


@app.get("/api/chat/message/{message_id}", response_model=schemas.ChatMessage, tags=["Chat"])
def get_chat_message(
    message_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific chat message."""
    db_message = crud.get_chat_message(db, message_id=message_id)
    if not db_message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Verify the message's animal belongs to the current user
    animal = crud.get_animal(db, animal_id=db_message.animal_id)
    if animal.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return db_message


@app.delete("/api/chat/{animal_id}", tags=["Chat"])
def delete_chat_history(
    animal_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete all chat messages for an animal."""
    animal = crud.get_animal(db, animal_id=animal_id)
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    
    if animal.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    count = crud.delete_all_chat_messages_for_animal(db, animal_id=animal_id)
    return {"message": f"Deleted {count} messages successfully"}


# ============= AI Chat Endpoints (with OpenAI integration) =============

@app.post("/api/ai/chat", response_model=schemas.AIChatResponse, tags=["AI"])
async def ai_chat(
    request: schemas.AIChatRequest,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Chat with AI about an animal."""
    # Verify the animal belongs to the current user
    animal = crud.get_animal(db, animal_id=request.animal_id)
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    
    if animal.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Save owner's message
    owner_message = schemas.ChatMessageCreate(
        animal_id=request.animal_id,
        sender="Owner",
        text=request.message,
        severity="low"
    )
    crud.create_chat_message(db, owner_message)
    
    # Get AI response
    animal_info = {
        "name": animal.name,
        "species": animal.species,
        "breed": animal.breed,
        "age": animal.age,
        "weight": animal.weight
    }
    
    ai_result = get_ai_response(request.message, animal_info)
    
    if "error" in ai_result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI request failed: {ai_result['error']}"
        )
    
    # Save AI response
    ai_message = schemas.ChatMessageCreate(
        animal_id=request.animal_id,
        sender="AI",
        text=ai_result["response"],
        severity="low",  # You can implement severity detection
        medicine_suggestion=None  # You can implement medicine extraction
    )
    db_ai_message = crud.create_chat_message(db, ai_message)
    
    return {
        "message": ai_result["response"],
        "severity": "low",
        "medicine_suggestion": None,
        "chat_message_id": db_ai_message.id
    }


# ============= AI Endpoints (Legacy, keeping for compatibility) =============

@app.post("/api/ai/ask", response_model=schemas.AIChatResponse, tags=["AI"])
async def ask_ai(
    request: schemas.AIChatRequest,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Ask AI a question about animals (legacy endpoint, redirects to /api/ai/chat)."""
    return await ai_chat(request, current_user, db)


@app.get("/api/ai/history/{animal_id}", response_model=List[schemas.ChatMessage], tags=["AI"])
def get_ai_history(
    animal_id: int,
    skip: int = 0,
    limit: int = 50,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get AI chat history for an animal (legacy endpoint, redirects to /api/chat)."""
    return get_chat_history(animal_id, skip, limit, current_user, db)


# ============= Run Application =============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
