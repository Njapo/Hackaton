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


# ============= Project Schemas =============

class ProjectBase(BaseModel):
    """Base schema for Project."""
    title: str = Field(..., min_length=1, max_length=200, description="Project/disease title")
    description: str = Field(..., min_length=1, description="Project description")


class ProjectCreate(ProjectBase):
    """Schema for creating a new project."""
    pass


class ProjectInDB(ProjectBase):
    """Schema for Project as stored in database."""
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class Project(ProjectInDB):
    """Schema for Project in API responses."""
    pass


# ============= Chat Message Schemas =============

class ChatMessageBase(BaseModel):
    """Base schema for ChatMessage."""
    message: str = Field(..., description="User's message or query")


class ChatMessageCreate(ChatMessageBase):
    """Schema for creating a new chat message."""
    response: str = Field(..., description="AI's generated response")
    project_id: Optional[int] = Field(None, description="Associated project ID")


class ChatMessageInDB(ChatMessageBase):
    """Schema for ChatMessage as stored in database."""
    id: int
    owner_id: int
    project_id: Optional[int]
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


class SummarizeRequest(BaseModel):
    """Schema for progress summary request."""
    project_id: int = Field(..., description="Project ID to summarize")
    project_title: str = Field(..., description="Project title")
    project_description: str = Field(..., description="Project description")


class SummarizeResponse(BaseModel):
    """Schema for progress summary response."""
    summary: str = Field(..., description="Generated progress summary")


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


# ============= History Schemas =============

class PredictionItem(BaseModel):
    """Schema for a single disease prediction."""
    disease: str = Field(..., description="Name of the predicted disease")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")


class HistoryBase(BaseModel):
    """Base schema for History entry."""
    image_path: str = Field(..., description="Path or URL to the uploaded image")
    disease_predictions: List[PredictionItem] = Field(..., description="List of disease predictions with confidence scores")
    gemini_response: str = Field(..., description="Full AI-generated response")
    healing_score: Optional[float] = Field(None, ge=0.0, le=100.0, description="Healing score (0-100)")


class HistoryCreate(HistoryBase):
    """Schema for creating a new history entry."""
    dino_embedding: Optional[List[float]] = Field(None, description="768-dim embedding vector from DinoV2")


class HistoryInDB(HistoryBase):
    """Schema for History as stored in database."""
    id: int
    user_id: int
    timestamp: datetime
    dino_embedding: Optional[List[float]] = None

    class Config:
        from_attributes = True


class History(HistoryInDB):
    """Schema for History in API responses."""
    pass


class HistorySummary(BaseModel):
    """Simplified schema for history list view (without full response text)."""
    id: int
    timestamp: datetime
    top_prediction: str = Field(..., description="Top predicted disease")
    top_confidence: float = Field(..., description="Confidence of top prediction")
    healing_score: Optional[float] = None
    image_path: str

    class Config:
        from_attributes = True


class HealingScoreUpdate(BaseModel):
    """Schema for updating healing score."""
    healing_score: float = Field(..., ge=0.0, le=100.0, description="New healing score (0-100)")


# ============= Lesion Section Schemas =============

class LesionSectionCreate(BaseModel):
    """Schema for creating a new lesion section."""
    section_name: str = Field(..., min_length=1, max_length=200, description="Name of the lesion section")
    description: Optional[str] = Field(None, description="Optional detailed description")


class LesionSectionResponse(BaseModel):
    """Schema for lesion section in API responses."""
    section_id: str = Field(..., description="Unique section identifier (UUID)")
    user_id: int
    section_name: str
    description: Optional[str] = None
    is_baseline: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class LesionSectionUpdate(BaseModel):
    """Schema for updating a lesion section."""
    section_name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None


# ============= Enhanced History Schemas for Progress Tracking =============

class HistoryCreateEnhanced(BaseModel):
    """Enhanced schema for creating history entry with section support."""
    section_id: Optional[str] = Field(None, description="Section ID to associate this entry with")
    image_path: str = Field(..., description="Path or URL to the uploaded image")
    disease_predictions: List[PredictionItem] = Field(..., description="List of disease predictions")
    dino_embedding: Optional[List[float]] = Field(None, description="768-dim embedding vector")
    gemini_response: Optional[str] = Field(None, description="AI response (may be generated later)")
    healing_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    is_baseline: bool = Field(False, description="Whether this is a baseline entry")
    user_notes: Optional[str] = Field(None, description="User's optional text description")


class HistoryResponseEnhanced(BaseModel):
    """Enhanced history response with section info."""
    id: int
    user_id: int
    section_id: Optional[str] = None
    section_name: Optional[str] = None  # Populated from relationship
    image_path: str
    timestamp: datetime
    disease_predictions: List[PredictionItem]
    gemini_response: Optional[str] = None
    healing_score: Optional[float] = None
    is_baseline: bool
    user_notes: Optional[str] = None

    class Config:
        from_attributes = True


# ============= Progress Review Schemas =============

class ProgressReviewRequest(BaseModel):
    """Schema for requesting a progress review."""
    section_id: str = Field(..., description="Section ID to review progress for")
    current_history_id: int = Field(..., description="ID of the current/latest history entry")
    include_last_n_entries: int = Field(3, ge=1, le=10, description="Number of previous entries to compare")


class ProgressComparison(BaseModel):
    """Schema for comparing two history entries."""
    previous_entry_id: int
    previous_timestamp: datetime
    previous_top_disease: str
    current_similarity: float = Field(..., description="Cosine similarity (0-1)")
    healing_percentage: float = Field(..., description="Computed healing score (0-100)")


class ProgressReviewResponse(BaseModel):
    """Schema for progress review response."""
    current_entry_id: int
    section_name: str
    baseline_entry_id: Optional[int] = None
    comparisons: List[ProgressComparison]
    average_healing_score: float = Field(..., description="Average healing score across comparisons")
    doctor_summary: str = Field(..., description="AI-generated doctor-style assessment")
    trend: Literal['improving', 'stable', 'worsening'] = Field(..., description="Overall trend")
