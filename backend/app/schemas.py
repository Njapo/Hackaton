"""
schemas.py - Pydantic Schemas for Request/Response Validation

This file defines Pydantic models for data validation and serialization.
These schemas ensure type safety and automatic API documentation.

Schemas for:
- User: Authentication and user profile
- Animal: Pet/animal information
- ChatMessage: Conversation history between owner and AI
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional, List, Literal
import json


# ============= User Schemas =============

class UserBase(BaseModel):
    """Base schema for User with common attributes."""
    email: EmailStr = Field(..., description="User's email address")
    name: str = Field(..., min_length=1, max_length=100, description="User's full name")


class UserCreate(UserBase):
    """Schema for creating a new user (registration)."""
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    email: Optional[EmailStr] = Field(None, description="New email address")
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="New name")
    password: Optional[str] = Field(None, min_length=8, description="New password")


class UserInDB(UserBase):
    """Schema for User as stored in database."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # Allows conversion from ORM model


class User(UserInDB):
    """Schema for User in API responses (same as UserInDB)."""
    pass


# ============= Animal Schemas =============

class AnimalBase(BaseModel):
    """Base schema for Animal with common attributes."""
    name: str = Field(..., min_length=1, max_length=100, description="Animal's name")
    species: str = Field(..., min_length=1, max_length=50, description="Animal species (Dog, Cat, etc.)")
    breed: Optional[str] = Field(None, max_length=100, description="Animal breed")
    age: Optional[int] = Field(None, ge=0, le=100, description="Age in years")
    weight: Optional[float] = Field(None, ge=0, le=1000, description="Weight in kg")
    icon_emoji: Optional[str] = Field(default="🐾", max_length=10, description="Emoji icon")


class AnimalCreate(AnimalBase):
    """Schema for creating a new animal."""
    pass


class AnimalUpdate(BaseModel):
    """Schema for updating animal information."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    species: Optional[str] = Field(None, min_length=1, max_length=50)
    breed: Optional[str] = Field(None, max_length=100)
    age: Optional[int] = Field(None, ge=0, le=100)
    weight: Optional[float] = Field(None, ge=0, le=1000)
    icon_emoji: Optional[str] = Field(None, max_length=10)


class AnimalInDB(AnimalBase):
    """Schema for Animal as stored in database."""
    id: int
    owner_id: int

    class Config:
        from_attributes = True


class Animal(AnimalInDB):
    """Schema for Animal in API responses."""
    pass


class AnimalWithMessages(Animal):
    """Schema for Animal with chat messages included."""
    chat_messages: List['ChatMessage'] = []

    class Config:
        from_attributes = True


# ============= ChatMessage Schemas =============

class ChatMessageBase(BaseModel):
    """Base schema for ChatMessage."""
    sender: Literal['Owner', 'AI'] = Field(..., description="Who sent the message: 'Owner' or 'AI'")
    text: str = Field(..., min_length=1, description="Message content")
    severity: Optional[Literal['low', 'moderate', 'urgent']] = Field(
        default='low',
        description="Health severity level"
    )
    medicine_suggestion: Optional[str] = Field(None, description="Medicine suggestions (JSON or text)")

    @field_validator('medicine_suggestion')
    @classmethod
    def validate_medicine_suggestion(cls, v):
        """Validate that medicine_suggestion is valid JSON if provided."""
        if v is not None and v.strip():
            try:
                # Try to parse as JSON to validate format
                json.loads(v)
            except json.JSONDecodeError:
                # If not valid JSON, just return as plain text (that's okay too)
                pass
        return v


class ChatMessageCreate(ChatMessageBase):
    """Schema for creating a new chat message."""
    animal_id: int = Field(..., description="ID of the animal this message is about")


class ChatMessageUpdate(BaseModel):
    """Schema for updating a chat message."""
    text: Optional[str] = Field(None, min_length=1)
    severity: Optional[Literal['low', 'moderate', 'urgent']] = None
    medicine_suggestion: Optional[str] = None


class ChatMessageInDB(ChatMessageBase):
    """Schema for ChatMessage as stored in database."""
    id: int
    animal_id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class ChatMessage(ChatMessageInDB):
    """Schema for ChatMessage in API responses."""
    pass


# ============= Authentication Schemas =============

class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token payload data."""
    email: Optional[str] = None


class LoginRequest(BaseModel):
    """Schema for login request."""
    email: EmailStr
    password: str


# ============= Response Schemas =============

class MessageResponse(BaseModel):
    """Generic message response schema."""
    message: str
    detail: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str
    detail: Optional[str] = None


# ============= AI Chat Schemas =============

class AIChatRequest(BaseModel):
    """Schema for AI chat request."""
    animal_id: int = Field(..., description="ID of the animal")
    message: str = Field(..., min_length=1, description="User's message to AI")


class AIChatResponse(BaseModel):
    """Schema for AI chat response."""
    message: str = Field(..., description="AI's response")
    severity: Literal['low', 'moderate', 'urgent'] = Field(default='low')
    medicine_suggestion: Optional[str] = None
    chat_message_id: int = Field(..., description="ID of the saved chat message")
