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


# ============= History CRUD Operations =============

def save_history_entry(
    db: Session,
    user_id: int,
    image_path: str,
    predictions: List[dict],
    embedding: Optional[List[float]],
    gemini_response: str,
    healing_score: Optional[float] = None
) -> models.History:
    """
    Save a complete skin disease analysis to history.
    
    This function stores:
    - Image metadata
    - Disease predictions from DinoV2
    - Image embeddings for similarity search
    - AI-generated response
    - Optional healing score
    
    Args:
        db: Database session
        user_id: ID of the user who submitted the analysis
        image_path: Path or URL where the image is stored
        predictions: List of prediction dicts with 'disease' and 'confidence' keys
        embedding: Vector embedding from DinoV2 (list of floats)
        gemini_response: Full text response from Gemini AI
        healing_score: Optional healing score (0-100)
        
    Returns:
        Created History object
        
    Example:
        save_history_entry(
            db=db,
            user_id=1,
            image_path="/uploads/skin_123.jpg",
            predictions=[{"disease": "Eczema", "confidence": 0.95}],
            embedding=[0.1, 0.2, ...],  # 768-dim vector
            gemini_response="This appears to be eczema...",
            healing_score=75.0
        )
    """
    db_history = models.History(
        user_id=user_id,
        image_path=image_path,
        disease_predictions=predictions,
        dino_embedding=embedding,
        gemini_response=gemini_response,
        healing_score=healing_score
    )
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history


def get_user_history(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 50
) -> List[models.History]:
    """
    Get all history entries for a specific user, ordered by most recent.
    
    Args:
        db: Database session
        user_id: ID of the user
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        
    Returns:
        List of History objects
    """
    return db.query(models.History)\
             .filter(models.History.user_id == user_id)\
             .order_by(desc(models.History.timestamp))\
             .offset(skip)\
             .limit(limit)\
             .all()


def get_history_entry(db: Session, history_id: int) -> Optional[models.History]:
    """
    Get a specific history entry by ID.
    
    Args:
        db: Database session
        history_id: ID of the history entry
        
    Returns:
        History object or None if not found
    """
    return db.query(models.History).filter(models.History.id == history_id).first()


def update_healing_score(
    db: Session,
    history_id: int,
    healing_score: float
) -> Optional[models.History]:
    """
    Update the healing score for a history entry.
    
    Useful for tracking progress after initial diagnosis.
    
    Args:
        db: Database session
        history_id: ID of the history entry
        healing_score: New healing score (0-100)
        
    Returns:
        Updated History object or None if not found
    """
    db_history = get_history_entry(db, history_id)
    if not db_history:
        return None
    
    db_history.healing_score = healing_score
    db.commit()
    db.refresh(db_history)
    return db_history


def get_similar_cases(
    db: Session,
    user_id: int,
    current_embedding: List[float],
    limit: int = 5
) -> List[models.History]:
    """
    Find similar historical cases for a user based on embedding similarity.
    
    For PostgreSQL with pgvector, this can use cosine similarity.
    For SQLite, we'll return recent cases for the same user.
    
    Args:
        db: Database session
        user_id: ID of the user
        current_embedding: Embedding vector to compare against
        limit: Maximum number of similar cases to return
        
    Returns:
        List of similar History objects
        
    Note:
        For full pgvector support, you would use:
        .order_by(History.dino_embedding.cosine_distance(current_embedding))
    """
    # Simple fallback: return recent history for the same user
    # TODO: Implement pgvector cosine similarity when PostgreSQL is configured
    return db.query(models.History)\
             .filter(models.History.user_id == user_id)\
             .filter(models.History.dino_embedding.isnot(None))\
             .order_by(desc(models.History.timestamp))\
             .limit(limit)\
             .all()


# ============= Lesion Section CRUD Operations =============

def create_lesion_section(
    db: Session,
    user_id: int,
    section_name: str,
    description: Optional[str] = None
) -> models.LesionSection:
    """
    Create a new lesion section for organizing different lesions/conditions.
    
    Args:
        db: Database session
        user_id: ID of the user creating the section
        section_name: Name of the section (e.g., "Left arm rash")
        description: Optional detailed description
        
    Returns:
        Created LesionSection object
    """
    db_section = models.LesionSection(
        user_id=user_id,
        section_name=section_name,
        description=description
    )
    db.add(db_section)
    db.commit()
    db.refresh(db_section)
    return db_section


def get_user_sections(
    db: Session,
    user_id: int
) -> List[models.LesionSection]:
    """
    Get all lesion sections for a user.
    
    Args:
        db: Database session
        user_id: ID of the user
        
    Returns:
        List of LesionSection objects
    """
    return db.query(models.LesionSection)\
             .filter(models.LesionSection.user_id == user_id)\
             .order_by(desc(models.LesionSection.created_at))\
             .all()


def get_section_by_id(
    db: Session,
    section_id: str
) -> Optional[models.LesionSection]:
    """
    Get a specific lesion section by ID.
    
    Args:
        db: Database session
        section_id: Section UUID
        
    Returns:
        LesionSection object or None
    """
    return db.query(models.LesionSection)\
             .filter(models.LesionSection.section_id == section_id)\
             .first()


def update_lesion_section(
    db: Session,
    section_id: str,
    section_name: Optional[str] = None,
    description: Optional[str] = None
) -> Optional[models.LesionSection]:
    """
    Update a lesion section.
    
    Args:
        db: Database session
        section_id: Section UUID
        section_name: New name (optional)
        description: New description (optional)
        
    Returns:
        Updated LesionSection object or None
    """
    db_section = get_section_by_id(db, section_id)
    if not db_section:
        return None
    
    if section_name is not None:
        db_section.section_name = section_name
    if description is not None:
        db_section.description = description
    
    db.commit()
    db.refresh(db_section)
    return db_section


def delete_lesion_section(
    db: Session,
    section_id: str
) -> bool:
    """
    Delete a lesion section and all associated history entries.
    
    Args:
        db: Database session
        section_id: Section UUID
        
    Returns:
        True if deleted, False if not found
    """
    db_section = get_section_by_id(db, section_id)
    if db_section:
        db.delete(db_section)
        db.commit()
        return True
    return False


# ============= Enhanced History Operations with Section Support =============

def save_history_entry_enhanced(
    db: Session,
    user_id: int,
    image_path: str,
    predictions: List[dict],
    embedding: Optional[List[float]],
    section_id: Optional[str] = None,
    gemini_response: Optional[str] = None,
    healing_score: Optional[float] = None,
    is_baseline: bool = False,
    user_notes: Optional[str] = None
) -> models.History:
    """
    Save an enhanced history entry with section support and optional fields.
    
    This function automatically saves every analysis, even if Gemini response
    is generated later during progress review.
    
    Args:
        db: Database session
        user_id: ID of the user
        image_path: Path to uploaded image
        predictions: List of prediction dicts
        embedding: 768-dim embedding vector
        section_id: Optional section UUID to associate with
        gemini_response: Optional AI response (can be None initially)
        healing_score: Optional healing score
        is_baseline: Whether this is a baseline entry
        user_notes: Optional user description/notes
        
    Returns:
        Created History object
    """
    db_history = models.History(
        user_id=user_id,
        section_id=section_id,
        image_path=image_path,
        disease_predictions=predictions,
        dino_embedding=embedding,
        gemini_response=gemini_response,
        healing_score=healing_score,
        is_baseline=is_baseline,
        user_notes=user_notes
    )
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history


def get_section_history(
    db: Session,
    section_id: str,
    skip: int = 0,
    limit: int = 50
) -> List[models.History]:
    """
    Get all history entries for a specific section.
    
    Args:
        db: Database session
        section_id: Section UUID
        skip: Number of records to skip
        limit: Maximum number of records
        
    Returns:
        List of History objects for this section
    """
    return db.query(models.History)\
             .filter(models.History.section_id == section_id)\
             .order_by(desc(models.History.timestamp))\
             .offset(skip)\
             .limit(limit)\
             .all()


def get_baseline_entry(
    db: Session,
    section_id: str
) -> Optional[models.History]:
    """
    Get the baseline entry for a section.
    
    Args:
        db: Database session
        section_id: Section UUID
        
    Returns:
        Baseline History object or None
    """
    return db.query(models.History)\
             .filter(models.History.section_id == section_id)\
             .filter(models.History.is_baseline == True)\
             .order_by(models.History.timestamp)\
             .first()


def get_recent_section_entries(
    db: Session,
    section_id: str,
    limit: int = 5,
    exclude_id: Optional[int] = None
) -> List[models.History]:
    """
    Get recent history entries for a section (for comparison).
    
    Args:
        db: Database session
        section_id: Section UUID
        limit: Maximum number of entries to return
        exclude_id: Optional history ID to exclude (e.g., current entry)
        
    Returns:
        List of recent History objects
    """
    query = db.query(models.History)\
              .filter(models.History.section_id == section_id)\
              .filter(models.History.dino_embedding.isnot(None))
    
    if exclude_id:
        query = query.filter(models.History.id != exclude_id)
    
    return query.order_by(desc(models.History.timestamp))\
                .limit(limit)\
                .all()


def update_history_gemini_response(
    db: Session,
    history_id: int,
    gemini_response: str,
    healing_score: Optional[float] = None
) -> Optional[models.History]:
    """
    Update Gemini response and healing score for a history entry.
    
    Used when generating progress reviews after initial save.
    
    Args:
        db: Database session
        history_id: ID of the history entry
        gemini_response: AI-generated response
        healing_score: Optional healing score
        
    Returns:
        Updated History object or None
    """
    db_history = get_history_entry(db, history_id)
    if not db_history:
        return None
    
    db_history.gemini_response = gemini_response
    if healing_score is not None:
        db_history.healing_score = healing_score
    
    db.commit()
    db.refresh(db_history)
    return db_history
