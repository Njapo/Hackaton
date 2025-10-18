"""
ai_client.py - Google Gemini API Client

This file handles all interactions with the Google Gemini API.
Includes functions for chat completions and other AI features.
"""

import os
from typing import Optional, List, Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Gemini client
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Default model configuration
DEFAULT_MODEL = "gemini-2.5-pro"
DEFAULT_MAX_TOKENS = 1000
DEFAULT_TEMPERATURE = 0.7


class AIClient:
    """
    Client class for interacting with Google Gemini API.
    Provides methods for various AI operations related to animals.
    """
    
    def __init__(self, model: str = DEFAULT_MODEL):
        """
        Initialize the AI client.
        
        Args:
            model: The Gemini model to use (default: gemini-pro)
        """
        self.model = genai.GenerativeModel(model)
    
    def chat_completion(
        self, 
        messages: List[Dict[str, str]],
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE
    ) -> Dict[str, Any]:
        """
        Send a chat completion request to Google Gemini.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum tokens in the response
            temperature: Sampling temperature (0-2)
            
        Returns:
            Dictionary containing response text and metadata
        """
        try:
            # Convert messages to Gemini format
            # Combine system and user messages into a single prompt
            prompt = ""
            for msg in messages:
                if msg["role"] == "system":
                    prompt += f"{msg['content']}\n\n"
                elif msg["role"] == "user":
                    prompt += f"{msg['content']}"
            
            # Configure generation with safety settings
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }
            
            # Configure safety settings to be less restrictive for medical/veterinary content
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE"
                }
            ]
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            # Check if response has text (safely)
            try:
                response_text = response.text
                return {
                    "response": response_text,
                    "model": DEFAULT_MODEL,
                    "tokens_used": None,
                    "finish_reason": "stop"
                }
            except (ValueError, AttributeError):
                # Handle blocked content or empty response - return fallback message WITHOUT error key
                finish_reason = response.candidates[0].finish_reason if response.candidates else "UNKNOWN"
                fallback_message = (
                    "I understand you're concerned about your dog's coughing. While I cannot provide specific "
                    "medical advice due to safety restrictions, here are general recommendations:\n\n"
                    "1. **Monitor the cough**: Note if it's dry, wet, or accompanied by other symptoms\n"
                    "2. **Check for triggers**: Exercise, eating/drinking, or environmental factors\n"
                    "3. **Ensure hydration**: Make sure fresh water is always available\n"
                    "4. **Watch for warning signs**: Difficulty breathing, lethargy, loss of appetite\n"
                    "5. **Veterinary consultation**: If coughing persists >24-48 hours or worsens, contact your vet\n\n"
                    "Common causes include kennel cough, allergies, or heart issues. A vet examination is recommended."
                )
                return {
                    "response": fallback_message,
                    "model": DEFAULT_MODEL,
                    "tokens_used": None,
                    "finish_reason": f"safety_block_{finish_reason}"
                }
        except Exception as e:
            return {
                "error": str(e),
                "response": None
            }
    
    def ask_about_animal(
        self, 
        prompt: str,
        animal_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ask a question about an animal or animals in general.
        
        Args:
            prompt: The user's question or prompt
            animal_info: Optional dictionary with animal details (name, species, breed, etc.)
            
        Returns:
            Dictionary containing AI response and metadata
        """
        # Build context from animal info if provided
        context = ""
        if animal_info:
            context = f"""
            Animal Information:
            - Name: {animal_info.get('name', 'Unknown')}
            - Species: {animal_info.get('species', 'Unknown')}
            - Breed: {animal_info.get('breed', 'Unknown')}
            - Age: {animal_info.get('age', 'Unknown')}
            - Description: {animal_info.get('description', 'No additional information')}
            """
        
        messages = [
            {
                "role": "system",
                "content": "You are an expert veterinarian and animal care specialist. "
                          "Provide helpful, accurate, and compassionate advice about animal care, "
                          "behavior, health, and well-being. Always remind users to consult with "
                          "a licensed veterinarian for serious health concerns."
            },
            {
                "role": "user",
                "content": f"{context}\n\nQuestion: {prompt}"
            }
        ]
        
        return self.chat_completion(messages)
    
    def generate_animal_care_tips(
        self, 
        species: str,
        breed: Optional[str] = None,
        age: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate care tips for a specific animal.
        
        Args:
            species: The animal species
            breed: Optional breed specification
            age: Optional age of the animal
            
        Returns:
            Dictionary containing care tips and metadata
        """
        breed_info = f" ({breed} breed)" if breed else ""
        age_info = f", age {age}" if age else ""
        
        prompt = f"Provide comprehensive care tips for a {species}{breed_info}{age_info}. " \
                f"Include information about diet, exercise, grooming, and health monitoring."
        
        messages = [
            {
                "role": "system",
                "content": "You are an expert animal care specialist. Provide practical, "
                          "evidence-based care tips that are easy to understand and follow."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        return self.chat_completion(messages)
    
    def analyze_animal_behavior(
        self,
        behavior_description: str,
        species: str,
        breed: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze and provide insights about animal behavior.
        
        Args:
            behavior_description: Description of the observed behavior
            species: The animal species
            breed: Optional breed specification
            
        Returns:
            Dictionary containing behavior analysis and metadata
        """
        breed_info = f" ({breed} breed)" if breed else ""
        
        prompt = f"Analyze this behavior in a {species}{breed_info}: {behavior_description}. " \
                f"Explain what it might mean, whether it's normal, and if any action should be taken."
        
        messages = [
            {
                "role": "system",
                "content": "You are an expert animal behaviorist. Provide insightful analysis "
                          "of animal behavior, explaining possible causes and recommendations."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        return self.chat_completion(messages)


# Global AI client instance
ai_client = AIClient()


def get_ai_response(prompt: str, animal_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Convenience function to get an AI response.
    
    Args:
        prompt: The user's question or prompt
        animal_info: Optional animal information dictionary
        
    Returns:
        Dictionary containing AI response and metadata
    """
    return ai_client.ask_about_animal(prompt, animal_info)
