"""
models.py - SQLAlchemy ORM Database Models

This file defines the database schema using SQLAlchemy ORM models.
Each class represents a table in the database.

Models:
- User: Stores user authentication and profile information
- ChatMessage: Stores chat history for skin analysis
- LesionSection: Stores user-created sections for organizing different lesions/conditions
- History: Stores detailed skin disease analysis with embeddings and progress tracking
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import uuid

# Try to import pgvector if available (for PostgreSQL)
try:
    from pgvector.sqlalchemy import Vector
    PGVECTOR_AVAILABLE = True
except ImportError:
    PGVECTOR_AVAILABLE = False
    Vector = None


class User(Base):
    """
    User model for authentication and user management.
    
    Fields:
    - id: Primary key, auto-incrementing integer
    - email: Unique email address for login
    - password_hash: Hashed password (never store plain text!)
    - name: User's display name
    - created_at: Timestamp when user account was created
    
    Relationships:
    - chat_messages: One-to-many relationship with ChatMessage model
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    chat_messages = relationship("ChatMessage", back_populates="owner", cascade="all, delete-orphan")


class ChatMessage(Base):
    """
    ChatMessage model for storing conversation history.
    
    Fields:
    - id: Primary key
    - owner_id: Foreign key to the user who initiated the chat
    - message: The user's original query/symptoms
    - response: The AI's generated response
    - created_at: Timestamp of the interaction
    
    Relationships:
    - owner: Many-to-one relationship with User model
    """
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="chat_messages")


class LesionSection(Base):
    """
    LesionSection model for organizing different lesions/skin conditions.
    
    Allows users to create separate sections for tracking different lesions,
    body parts, or conditions. Each section has its own history and progress tracking.
    
    Fields:
    - section_id: Unique identifier (UUID string)
    - user_id: Foreign key to the user who owns this section
    - section_name: User-defined name (e.g., "Left arm rash", "Facial acne")
    - description: Optional detailed description
    - is_baseline: Whether this section's first entry is marked as baseline
    - created_at: When the section was created
    
    Relationships:
    - user: Many-to-one relationship with User model
    - history_entries: One-to-many relationship with History model
    """
    __tablename__ = "lesion_sections"

    section_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    section_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    is_baseline = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", backref="lesion_sections")
    history_entries = relationship("History", back_populates="section", cascade="all, delete-orphan")


class History(Base):
    """
    History model for storing detailed skin disease analysis with embeddings.
    
    This model stores comprehensive analysis data including:
    - Image metadata and storage path
    - Disease predictions from DinoV2 model
    - Image embeddings (for similarity search and healing tracking)
    - AI-generated responses
    - Healing score for tracking progress over time
    - Section association for organizing multiple lesions
    
    Fields:
    - id: Primary key
    - user_id: Foreign key to the user who submitted the analysis
    - section_id: Foreign key to lesion section (optional for backward compatibility)
    - image_path: Path or URL to the uploaded image file
    - timestamp: When the analysis was performed
    - disease_predictions: JSON array of predictions with confidence scores
    - dino_embedding: Vector embedding from DinoV2 (pgvector if PostgreSQL, JSON if SQLite)
    - gemini_response: Full text response from Gemini AI (can be generated later for progress reviews)
    - healing_score: Optional score (0-100) for tracking healing progress
    - is_baseline: Whether this is the first/baseline entry for a section
    - user_notes: Optional text description from user
    
    Relationships:
    - user: Many-to-one relationship with User model
    - section: Many-to-one relationship with LesionSection model
    """
    __tablename__ = "history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    section_id = Column(String(36), ForeignKey("lesion_sections.section_id"), nullable=True, index=True)
    image_path = Column(String(500), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Store predictions as JSON: [{"disease": "name", "confidence": 0.95}, ...]
    disease_predictions = Column(JSON, nullable=False)
    
    # Embedding vector - use pgvector for PostgreSQL, JSON for SQLite
    # Default dimension for DinoV2-base is 768
    if PGVECTOR_AVAILABLE:
        dino_embedding = Column(Vector(768), nullable=True)
    else:
        dino_embedding = Column(JSON, nullable=True)  # Fallback to JSON array
    
    # Full Gemini response (may be empty initially, filled during progress review)
    gemini_response = Column(Text, nullable=True)
    
    # Optional healing score (0-100)
    healing_score = Column(Float, nullable=True)
    
    # Baseline marker
    is_baseline = Column(Boolean, default=False, index=True)
    
    # Optional user notes/description
    user_notes = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", backref="history_entries")
    section = relationship("LesionSection", back_populates="history_entries")
