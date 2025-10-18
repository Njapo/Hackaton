"""
schemas.py - Pydantic Schemas for Request/Response Validation

This file defines Pydantic models for data validation and serialization.
These schemas ensure type safety and automatic API documentation.

Schemas for:
- User: Authentication and user profile
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


# ============= Chat Message Schemas =============

class ChatMessageBase(BaseModel):
    """Base schema for ChatMessage."""
    message: str = Field(..., description="User's message or query")


class ChatMessageCreate(ChatMessageBase):
    """Schema for creating a new chat message."""
    response: str = Field(..., description="AI's generated response")


class ChatMessageInDB(ChatMessageBase):
    """Schema for ChatMessage as stored in database."""
    id: int
    owner_id: int
    response: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatMessage(ChatMessageInDB):
    """Schema for ChatMessage in API responses."""
    pass


# ============= Token Schemas =============

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
    message: str = Field(..., min_length=1, description="User's message to AI")


class AIChatResponse(BaseModel):
    """Schema for AI chat response."""
    message: str = Field(..., description="AI's response")
    severity: Literal['low', 'moderate', 'urgent'] = Field(default='low')
    medicine_suggestion: Optional[str] = None
    chat_message_id: int = Field(..., description="ID of the saved chat message")
