"""
main.py - FastAPI Application Entry Point

This is the main application file that initializes FastAPI and configures all routes.
Run this file to start the API server.
"""

from fastapi import FastAPI, Depends, HTTPException, status
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
    # Check if username already exists
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
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
    """Login and get access token."""
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
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


# ============= AI Endpoints =============

@app.post("/api/ai/ask", response_model=schemas.AIResponse, tags=["AI"])
async def ask_ai(
    request: schemas.AIRequestCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Ask AI a question about animals."""
    animal_info = None
    
    # Get animal info if animal_id is provided
    if request.animal_id:
        animal = crud.get_animal(db, animal_id=request.animal_id)
        if animal:
            animal_info = {
                "name": animal.name,
                "species": animal.species,
                "breed": animal.breed,
                "age": animal.age,
                "description": animal.description
            }
    
    # Get AI response
    ai_result = get_ai_response(request.prompt, animal_info)
    
    if "error" in ai_result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI request failed: {ai_result['error']}"
        )
    
    # Save AI request to database
    crud.create_ai_request(
        db=db,
        user_id=current_user.id,
        animal_id=request.animal_id,
        prompt=request.prompt,
        response=ai_result["response"],
        model=ai_result["model"],
        tokens_used=ai_result.get("tokens_used")
    )
    
    return {
        "response": ai_result["response"],
        "model": ai_result["model"],
        "tokens_used": ai_result.get("tokens_used")
    }


@app.get("/api/ai/history", response_model=List[schemas.AIRequest], tags=["AI"])
def get_ai_history(
    skip: int = 0,
    limit: int = 50,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's AI request history."""
    requests = crud.get_ai_requests_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    return requests


# ============= Run Application =============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
