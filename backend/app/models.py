"""
models.py - SQLAlchemy ORM Database Models

This file defines the database schema using SQLAlchemy ORM models.
Each class represents a table in the database.

Models:
- User: Stores user authentication and profile information
- Animal: Stores animal/pet information owned by users
- ChatMessage: Stores chat history between owner and AI for each animal
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
    - animals: One-to-many relationship with Animal model
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    animals = relationship("Animal", back_populates="owner", cascade="all, delete-orphan")




class Animal(Base):
    """
    Animal model for storing pet/animal information.
    
    Fields:
    - id: Primary key, auto-incrementing integer
    - owner_id: Foreign key to User.id (who owns this animal)
    - name: Animal's name (e.g., "Fluffy", "Rex")
    - species: Type of animal (e.g., "Dog", "Cat", "Bird")
    - breed: Specific breed (e.g., "Golden Retriever", "Persian")
    - age: Age in years
    - weight: Weight in kilograms (float for precision)
    - icon_emoji: Emoji icon for the animal (e.g., "🐕", "🐱", "🐦")
    
    Relationships:
    - owner: Many-to-one relationship with User model
    - chat_messages: One-to-many relationship with ChatMessage model
    """
    __tablename__ = "animals"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    species = Column(String(50), nullable=False)
    breed = Column(String(100), nullable=True)
    age = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)
    icon_emoji = Column(String(10), nullable=True, default="🐾")

    # Relationships
    owner = relationship("User", back_populates="animals")
    chat_messages = relationship("ChatMessage", back_populates="animal", cascade="all, delete-orphan")


class ChatMessage(Base):
    """
    ChatMessage model for storing conversation history between owner and AI.
    
    Each message is associated with a specific animal and tracks:
    - Who sent it (Owner or AI)
    - The message content
    - Health severity level (if applicable)
    - Any medicine suggestions from AI
    
    Fields:
    - id: Primary key, auto-incrementing integer
    - animal_id: Foreign key to Animal.id (which animal this chat is about)
    - sender: Who sent the message - either 'Owner' or 'AI'
    - text: The actual message content
    - severity: Health severity level - 'low', 'moderate', or 'urgent'
    - timestamp: When the message was sent
    - medicine_suggestion: JSON string or text with medicine recommendations
    
    Relationships:
    - animal: Many-to-one relationship with Animal model
    """
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    animal_id = Column(Integer, ForeignKey("animals.id", ondelete="CASCADE"), nullable=False)
    sender = Column(String(10), nullable=False)  # 'Owner' or 'AI'
    text = Column(Text, nullable=False)
    severity = Column(String(20), nullable=True, default="low")  # 'low', 'moderate', 'urgent'
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    medicine_suggestion = Column(Text, nullable=True)  # JSON string or plain text

    # Relationships
    animal = relationship("Animal", back_populates="chat_messages")
