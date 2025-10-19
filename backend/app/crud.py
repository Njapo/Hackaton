"""
crud.py - CRUD (Create, Read, Update, Delete) Operations

This file contains database operations for all models.
These functions abstract database queries and provide a clean interface for routes.

CRUD operations for:
- User: Authentication and profile management
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
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False


# ============= Project CRUD Operations =============

def create_project(db: Session, project: schemas.ProjectCreate, user_id: int) -> models.Project:
    """
    Create a new project for a user.
    
    Args:
        db: Database session
        project: ProjectCreate schema with project data
        user_id: The ID of the user who owns this project
        
    Returns:
        Created Project object
    """
    db_project = models.Project(
        title=project.title,
        description=project.description,
        owner_id=user_id
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def get_user_projects(db: Session, user_id: int) -> List[models.Project]:
    """
    Get all projects for a specific user, ordered by most recent.
    
    Args:
        db: Database session
        user_id: The ID of the user
        
    Returns:
        List of Project objects
    """
    return db.query(models.Project)\
             .filter(models.Project.owner_id == user_id)\
             .order_by(desc(models.Project.created_at))\
             .all()


def get_project(db: Session, project_id: int, user_id: int) -> Optional[models.Project]:
    """
    Get a specific project by ID for a user.
    
    Args:
        db: Database session
        project_id: The ID of the project
        user_id: The ID of the user
        
    Returns:
        Project object or None if not found
    """
    return db.query(models.Project)\
             .filter(models.Project.id == project_id)\
             .filter(models.Project.owner_id == user_id)\
             .first()


def get_project_chat_messages(db: Session, project_id: int, user_id: int) -> List[models.ChatMessage]:
    """
    Get all chat messages for a specific project.
    
    Args:
        db: Database session
        project_id: The ID of the project
        user_id: The ID of the user
        
    Returns:
        List of ChatMessage objects
    """
    return db.query(models.ChatMessage)\
             .filter(models.ChatMessage.project_id == project_id)\
             .filter(models.ChatMessage.owner_id == user_id)\
             .order_by(models.ChatMessage.created_at)\
             .all()


# ============= Chat Message CRUD Operations =============

def create_chat_message(db: Session, message: schemas.ChatMessageCreate, user_id: int) -> models.ChatMessage:
    """
    Create a new chat message for a user.
    
    Args:
        db: Database session
        message: ChatMessageCreate schema with message data
        user_id: The ID of the user who owns this message
        
    Returns:
        Created ChatMessage object
    """
    db_message = models.ChatMessage(
        message=message.message,
        response=message.response,
        owner_id=user_id,
        project_id=message.project_id
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def get_user_chat_messages(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[models.ChatMessage]:
    """
    Get all chat messages for a specific user, ordered by most recent.
    
    Args:
        db: Database session
        user_id: The ID of the user
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of ChatMessage objects
    """
    return db.query(models.ChatMessage)\
             .filter(models.ChatMessage.owner_id == user_id)\
             .order_by(desc(models.ChatMessage.created_at))\
             .offset(skip)\
             .limit(limit)\
             .all()
