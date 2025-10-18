"""
models.py - SQLAlchemy ORM Database Models

This file defines the database schema using SQLAlchemy ORM models.
Each class represents a table in the database.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    """
    User model for authentication and user management.
    
    Stores user credentials and profile information.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    animals = relationship("Animal", back_populates="owner")
    ai_requests = relationship("AIRequest", back_populates="user")


class Animal(Base):
    """
    Animal model for storing animal information.
    
    Stores details about animals that users add to the system.
    """
    __tablename__ = "animals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    species = Column(String(50), nullable=False)
    breed = Column(String(50), nullable=True)
    age = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    image_url = Column(String(255), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="animals")
    ai_requests = relationship("AIRequest", back_populates="animal")


class AIRequest(Base):
    """
    AIRequest model for tracking OpenAI API requests and responses.
    
    Stores the history of AI interactions for auditing and analysis.
    """
    __tablename__ = "ai_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    animal_id = Column(Integer, ForeignKey("animals.id"), nullable=True)
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    model = Column(String(50), default="gpt-3.5-turbo")
    tokens_used = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="ai_requests")
    animal = relationship("Animal", back_populates="ai_requests")
