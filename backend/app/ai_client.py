"""
ai_client.py - OpenAI API Client

This file handles all interactions with the OpenAI API.
Includes functions for chat completions, embeddings, and other AI features.
"""

import os
from typing import Optional, List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Default model configuration
DEFAULT_MODEL = "gpt-3.5-turbo"
DEFAULT_MAX_TOKENS = 1000
DEFAULT_TEMPERATURE = 0.7


class AIClient:
    """
    Client class for interacting with OpenAI API.
    Provides methods for various AI operations related to animals.
    """
    
    def __init__(self, model: str = DEFAULT_MODEL):
        """
        Initialize the AI client.
        
        Args:
            model: The OpenAI model to use (default: gpt-3.5-turbo)
        """
        self.model = model
        self.client = client
    
    def chat_completion(
        self, 
        messages: List[Dict[str, str]],
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE
    ) -> Dict[str, Any]:
        """
        Send a chat completion request to OpenAI.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum tokens in the response
            temperature: Sampling temperature (0-2)
            
        Returns:
            Dictionary containing response text and metadata
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return {
                "response": response.choices[0].message.content,
                "model": response.model,
                "tokens_used": response.usage.total_tokens if response.usage else None,
                "finish_reason": response.choices[0].finish_reason
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
