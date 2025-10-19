"""
models.py - SQLAlchemy ORM Database Models

This file defines the database schema using SQLAlchemy ORM models.
Each class represents a table in the database.

Models:
- User: Stores user authentication and profile information
- ChatMessage: Stores chat history for skin analysis
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


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
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")


class Project(Base):
    """
    Project model for storing disease/condition tracking.
    
    Fields:
    - id: Primary key
    - owner_id: Foreign key to the user who created the project
    - title: Project/disease name
    - description: Project description
    - created_at: Timestamp when project was created
    
    Relationships:
    - owner: Many-to-one relationship with User model
    - chat_messages: One-to-many relationship with ChatMessage model
    """
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="projects")
    chat_messages = relationship("ChatMessage", back_populates="project", cascade="all, delete-orphan")


class ChatMessage(Base):
    """
    ChatMessage model for storing conversation history.
    
    Fields:
    - id: Primary key
    - owner_id: Foreign key to the user who initiated the chat
    - project_id: Foreign key to the project (optional)
    - message: The user's original query/symptoms
    - response: The AI's generated response
    - created_at: Timestamp of the interaction
    
    Relationships:
    - owner: Many-to-one relationship with User model
    - project: Many-to-one relationship with Project model
    """
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="chat_messages")
    project = relationship("Project", back_populates="chat_messages")
