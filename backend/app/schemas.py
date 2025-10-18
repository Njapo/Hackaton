"""
schemas.py - Pydantic Schemas for Request/Response Validation

This file defines Pydantic models for data validation and serialization.
These schemas ensure type safety and automatic API documentation.
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List


# ============= User Schemas =============

class UserBase(BaseModel):
    """Base schema for User with common attributes."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)


class UserInDB(UserBase):
    """Schema for User as stored in database."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class User(UserInDB):
    """Schema for User in API responses."""
    pass


# ============= Animal Schemas =============

class AnimalBase(BaseModel):
    """Base schema for Animal with common attributes."""
    name: str = Field(..., min_length=1, max_length=100)
    species: str = Field(..., min_length=1, max_length=50)
    breed: Optional[str] = Field(None, max_length=50)
    age: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None
    image_url: Optional[str] = None


class AnimalCreate(AnimalBase):
    """Schema for creating a new animal."""
    pass


class AnimalUpdate(BaseModel):
    """Schema for updating animal information."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    species: Optional[str] = Field(None, min_length=1, max_length=50)
    breed: Optional[str] = Field(None, max_length=50)
    age: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None
    image_url: Optional[str] = None


class AnimalInDB(AnimalBase):
    """Schema for Animal as stored in database."""
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Animal(AnimalInDB):
    """Schema for Animal in API responses."""
    pass


# ============= AI Request Schemas =============

class AIRequestBase(BaseModel):
    """Base schema for AI Request."""
    prompt: str = Field(..., min_length=1)
    animal_id: Optional[int] = None


class AIRequestCreate(AIRequestBase):
    """Schema for creating a new AI request."""
    pass


class AIRequestInDB(AIRequestBase):
    """Schema for AI Request as stored in database."""
    id: int
    user_id: int
    response: str
    model: str
    tokens_used: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AIRequest(AIRequestInDB):
    """Schema for AI Request in API responses."""
    pass


class AIResponse(BaseModel):
    """Schema for AI API response."""
    response: str
    model: str
    tokens_used: Optional[int] = None


# ============= Authentication Schemas =============

class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token payload data."""
    username: Optional[str] = None


class LoginRequest(BaseModel):
    """Schema for login request."""
    username: str
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
