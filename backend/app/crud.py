"""
crud.py - CRUD (Create, Read, Update, Delete) Operations

This file contains database operations for all models.
These functions abstract database queries and provide a clean interface for routes.
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from . import models, schemas
from .auth import get_password_hash


# ============= User CRUD Operations =============

def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """Get a user by ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """Get a user by username."""
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Get a user by email."""
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    """Get a list of users with pagination."""
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create a new user with hashed password."""
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate) -> Optional[models.User]:
    """Update user information."""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    
    # Hash password if it's being updated
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """Delete a user."""
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    return True


# ============= Animal CRUD Operations =============

def get_animal(db: Session, animal_id: int) -> Optional[models.Animal]:
    """Get an animal by ID."""
    return db.query(models.Animal).filter(models.Animal.id == animal_id).first()


def get_animals(db: Session, skip: int = 0, limit: int = 100) -> List[models.Animal]:
    """Get a list of all animals with pagination."""
    return db.query(models.Animal).offset(skip).limit(limit).all()


def get_animals_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 100) -> List[models.Animal]:
    """Get all animals owned by a specific user."""
    return db.query(models.Animal).filter(
        models.Animal.owner_id == owner_id
    ).offset(skip).limit(limit).all()


def get_animals_by_species(db: Session, species: str, skip: int = 0, limit: int = 100) -> List[models.Animal]:
    """Get animals by species."""
    return db.query(models.Animal).filter(
        models.Animal.species.ilike(f"%{species}%")
    ).offset(skip).limit(limit).all()


def create_animal(db: Session, animal: schemas.AnimalCreate, owner_id: int) -> models.Animal:
    """Create a new animal."""
    db_animal = models.Animal(**animal.model_dump(), owner_id=owner_id)
    db.add(db_animal)
    db.commit()
    db.refresh(db_animal)
    return db_animal


def update_animal(db: Session, animal_id: int, animal_update: schemas.AnimalUpdate) -> Optional[models.Animal]:
    """Update animal information."""
    db_animal = get_animal(db, animal_id)
    if not db_animal:
        return None
    
    update_data = animal_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_animal, field, value)
    
    db.commit()
    db.refresh(db_animal)
    return db_animal


def delete_animal(db: Session, animal_id: int) -> bool:
    """Delete an animal."""
    db_animal = get_animal(db, animal_id)
    if not db_animal:
        return False
    
    db.delete(db_animal)
    db.commit()
    return True


# ============= AI Request CRUD Operations =============

def get_ai_request(db: Session, request_id: int) -> Optional[models.AIRequest]:
    """Get an AI request by ID."""
    return db.query(models.AIRequest).filter(models.AIRequest.id == request_id).first()


def get_ai_requests_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[models.AIRequest]:
    """Get all AI requests made by a specific user."""
    return db.query(models.AIRequest).filter(
        models.AIRequest.user_id == user_id
    ).order_by(desc(models.AIRequest.created_at)).offset(skip).limit(limit).all()


def get_ai_requests_by_animal(db: Session, animal_id: int, skip: int = 0, limit: int = 100) -> List[models.AIRequest]:
    """Get all AI requests related to a specific animal."""
    return db.query(models.AIRequest).filter(
        models.AIRequest.animal_id == animal_id
    ).order_by(desc(models.AIRequest.created_at)).offset(skip).limit(limit).all()


def create_ai_request(
    db: Session, 
    user_id: int, 
    prompt: str, 
    response: str, 
    model: str,
    animal_id: Optional[int] = None,
    tokens_used: Optional[int] = None
) -> models.AIRequest:
    """Create a new AI request record."""
    db_request = models.AIRequest(
        user_id=user_id,
        animal_id=animal_id,
        prompt=prompt,
        response=response,
        model=model,
        tokens_used=tokens_used
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request
