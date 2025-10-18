"""
crud.py - CRUD (Create, Read, Update, Delete) Operations

This file contains database operations for all models.
These functions abstract database queries and provide a clean interface for routes.

CRUD operations for:
- User: Authentication and profile management
- Animal: Pet/animal management
- ChatMessage: Conversation history management

All functions handle SQLAlchemy sessions properly and return typed objects.
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from . import models, schemas
from .auth import get_password_hash


# ============= User CRUD Operations =============

def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """
    Get a user by ID.
    
    Args:
        db: Database session
        user_id: User's ID
        
    Returns:
        User object or None if not found
    """
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """
    Get a user by email address.
    
    Args:
        db: Database session
        email: User's email
        
    Returns:
        User object or None if not found
    """
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    """
    Get a list of users with pagination.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of User objects
    """
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """
    Create a new user with hashed password.
    
    Args:
        db: Database session
        user: UserCreate schema with user data
        
    Returns:
        Created User object
    """
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        name=user.name,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate) -> Optional[models.User]:
    """
    Update user information.
    
    Args:
        db: Database session
        user_id: User's ID
        user_update: UserUpdate schema with updated fields
        
    Returns:
        Updated User object or None if not found
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    
    # Hash password if it's being updated
    if "password" in update_data:
        update_data["password_hash"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """
    Delete a user.
    
    Args:
        db: Database session
        user_id: User's ID
        
    Returns:
        True if deleted, False if not found
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    return True


# ============= Animal CRUD Operations =============

def get_animal(db: Session, animal_id: int) -> Optional[models.Animal]:
    """
    Get an animal by ID.
    
    Args:
        db: Database session
        animal_id: Animal's ID
        
    Returns:
        Animal object or None if not found
    """
    return db.query(models.Animal).filter(models.Animal.id == animal_id).first()


def get_animals(db: Session, skip: int = 0, limit: int = 100) -> List[models.Animal]:
    """
    Get a list of all animals with pagination.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of Animal objects
    """
    return db.query(models.Animal).offset(skip).limit(limit).all()


def get_animals_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 100) -> List[models.Animal]:
    """
    Get all animals owned by a specific user.
    
    Args:
        db: Database session
        owner_id: Owner's user ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of Animal objects
    """
    return db.query(models.Animal).filter(
        models.Animal.owner_id == owner_id
    ).offset(skip).limit(limit).all()


def get_animals_by_species(db: Session, species: str, skip: int = 0, limit: int = 100) -> List[models.Animal]:
    """
    Get animals by species.
    
    Args:
        db: Database session
        species: Animal species to filter by
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of Animal objects
    """
    return db.query(models.Animal).filter(
        models.Animal.species.ilike(f"%{species}%")
    ).offset(skip).limit(limit).all()


def create_animal(db: Session, animal: schemas.AnimalCreate, owner_id: int) -> models.Animal:
    """
    Create a new animal.
    
    Args:
        db: Database session
        animal: AnimalCreate schema with animal data
        owner_id: ID of the user who owns this animal
        
    Returns:
        Created Animal object
    """
    db_animal = models.Animal(**animal.model_dump(), owner_id=owner_id)
    db.add(db_animal)
    db.commit()
    db.refresh(db_animal)
    return db_animal


def update_animal(db: Session, animal_id: int, animal_update: schemas.AnimalUpdate) -> Optional[models.Animal]:
    """
    Update animal information.
    
    Args:
        db: Database session
        animal_id: Animal's ID
        animal_update: AnimalUpdate schema with updated fields
        
    Returns:
        Updated Animal object or None if not found
    """
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
    """
    Delete an animal.
    
    Args:
        db: Database session
        animal_id: Animal's ID
        
    Returns:
        True if deleted, False if not found
    """
    db_animal = get_animal(db, animal_id)
    if not db_animal:
        return False
    
    db.delete(db_animal)
    db.commit()
    return True


# ============= ChatMessage CRUD Operations =============

def get_chat_message(db: Session, message_id: int) -> Optional[models.ChatMessage]:
    """
    Get a chat message by ID.
    
    Args:
        db: Database session
        message_id: Message ID
        
    Returns:
        ChatMessage object or None if not found
    """
    return db.query(models.ChatMessage).filter(models.ChatMessage.id == message_id).first()


def get_chat_messages_by_animal(
    db: Session, 
    animal_id: int, 
    skip: int = 0, 
    limit: int = 100
) -> List[models.ChatMessage]:
    """
    Get all chat messages for a specific animal, ordered by timestamp (newest first).
    
    Args:
        db: Database session
        animal_id: Animal's ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of ChatMessage objects ordered by timestamp descending
    """
    return db.query(models.ChatMessage).filter(
        models.ChatMessage.animal_id == animal_id
    ).order_by(desc(models.ChatMessage.timestamp)).offset(skip).limit(limit).all()


def get_chat_messages_by_sender(
    db: Session,
    animal_id: int,
    sender: str,
    skip: int = 0,
    limit: int = 100
) -> List[models.ChatMessage]:
    """
    Get chat messages for an animal filtered by sender (Owner or AI).
    
    Args:
        db: Database session
        animal_id: Animal's ID
        sender: Message sender ('Owner' or 'AI')
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of ChatMessage objects
    """
    return db.query(models.ChatMessage).filter(
        models.ChatMessage.animal_id == animal_id,
        models.ChatMessage.sender == sender
    ).order_by(desc(models.ChatMessage.timestamp)).offset(skip).limit(limit).all()


def get_chat_messages_by_severity(
    db: Session,
    animal_id: int,
    severity: str,
    skip: int = 0,
    limit: int = 100
) -> List[models.ChatMessage]:
    """
    Get chat messages filtered by severity level.
    
    Args:
        db: Database session
        animal_id: Animal's ID
        severity: Severity level ('low', 'moderate', 'urgent')
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of ChatMessage objects
    """
    return db.query(models.ChatMessage).filter(
        models.ChatMessage.animal_id == animal_id,
        models.ChatMessage.severity == severity
    ).order_by(desc(models.ChatMessage.timestamp)).offset(skip).limit(limit).all()


def create_chat_message(db: Session, message: schemas.ChatMessageCreate) -> models.ChatMessage:
    """
    Create a new chat message.
    
    Args:
        db: Database session
        message: ChatMessageCreate schema with message data
        
    Returns:
        Created ChatMessage object
    """
    db_message = models.ChatMessage(**message.model_dump())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def update_chat_message(
    db: Session, 
    message_id: int, 
    message_update: schemas.ChatMessageUpdate
) -> Optional[models.ChatMessage]:
    """
    Update a chat message.
    
    Args:
        db: Database session
        message_id: Message ID
        message_update: ChatMessageUpdate schema with updated fields
        
    Returns:
        Updated ChatMessage object or None if not found
    """
    db_message = get_chat_message(db, message_id)
    if not db_message:
        return None
    
    update_data = message_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_message, field, value)
    
    db.commit()
    db.refresh(db_message)
    return db_message


def delete_chat_message(db: Session, message_id: int) -> bool:
    """
    Delete a chat message.
    
    Args:
        db: Database session
        message_id: Message ID
        
    Returns:
        True if deleted, False if not found
    """
    db_message = get_chat_message(db, message_id)
    if not db_message:
        return False
    
    db.delete(db_message)
    db.commit()
    return True


def delete_all_chat_messages_for_animal(db: Session, animal_id: int) -> int:
    """
    Delete all chat messages for a specific animal.
    
    Args:
        db: Database session
        animal_id: Animal's ID
        
    Returns:
        Number of messages deleted
    """
    count = db.query(models.ChatMessage).filter(
        models.ChatMessage.animal_id == animal_id
    ).delete()
    db.commit()
    return count
