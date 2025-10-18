"""
utils.py - Utility Functions

This file contains helper functions and utilities used across the application.
Includes data validation, formatting, and common operations.
"""

import re
from typing import Optional, Dict, Any
from datetime import datetime
import secrets


def validate_email(email: str) -> bool:
    """
    Validate email format using regex.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid email format, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_username(username: str) -> bool:
    """
    Validate username format.
    Username should be 3-50 characters, alphanumeric and underscores only.
    
    Args:
        username: Username to validate
        
    Returns:
        True if valid username, False otherwise
    """
    if not username or len(username) < 3 or len(username) > 50:
        return False
    pattern = r'^[a-zA-Z0-9_]+$'
    return re.match(pattern, username) is not None


def validate_password_strength(password: str) -> Dict[str, Any]:
    """
    Check password strength and return validation details.
    
    Args:
        password: Password to validate
        
    Returns:
        Dictionary with 'is_valid' bool and 'errors' list
    """
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one number")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors
    }


def generate_random_string(length: int = 32) -> str:
    """
    Generate a random secure string.
    
    Args:
        length: Length of the string to generate
        
    Returns:
        Random string of specified length
    """
    return secrets.token_urlsafe(length)


def format_datetime(dt: Optional[datetime]) -> Optional[str]:
    """
    Format datetime object to ISO string.
    
    Args:
        dt: Datetime object to format
        
    Returns:
        ISO formatted string or None
    """
    if dt is None:
        return None
    return dt.isoformat()


def calculate_age_in_months(age_years: Optional[int]) -> Optional[int]:
    """
    Convert age in years to months.
    
    Args:
        age_years: Age in years
        
    Returns:
        Age in months or None
    """
    if age_years is None:
        return None
    return age_years * 12


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing or replacing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for filesystem
    """
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')
    # Limit length
    if len(sanitized) > 255:
        name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
        sanitized = name[:250] + (f'.{ext}' if ext else '')
    return sanitized


def parse_species(species_input: str) -> str:
    """
    Parse and normalize species input.
    
    Args:
        species_input: Raw species input
        
    Returns:
        Normalized species name
    """
    return species_input.strip().lower().capitalize()


def create_error_response(error: str, detail: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a standardized error response dictionary.
    
    Args:
        error: Error message
        detail: Optional additional details
        
    Returns:
        Error response dictionary
    """
    response = {"error": error}
    if detail:
        response["detail"] = detail
    return response


def create_success_response(message: str, data: Optional[Any] = None) -> Dict[str, Any]:
    """
    Create a standardized success response dictionary.
    
    Args:
        message: Success message
        data: Optional data to include
        
    Returns:
        Success response dictionary
    """
    response = {"message": message}
    if data is not None:
        response["data"] = data
    return response


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to specified length and add suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length before truncation
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def is_valid_animal_age(age: Optional[int]) -> bool:
    """
    Validate animal age is within reasonable range.
    
    Args:
        age: Age to validate
        
    Returns:
        True if valid age, False otherwise
    """
    if age is None:
        return True  # Age is optional
    return 0 <= age <= 100  # Most animals don't live past 100 years
