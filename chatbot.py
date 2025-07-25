"""
Chatbot module for the text-based game quest.

This module defines the Chatbot class and related adapters, which allow AI to assume
control over characters in the game. The Chatbot class provides an interface for
generating responses based on character attributes and conversation context.
"""

import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from character import Character
import openai


class AIAdapter(ABC):
    """Abstract base class for AI adapters.
    
    This class defines the interface that all AI adapters must implement.
    Different AI services (like OpenAI, etc.) can be supported by implementing
    this interface.
    """
    
    @abstractmethod
    def generate_response(self, character: Character, context: List[Dict[str, Any]], 
                         prompt: Optional[str] = None) -> str:
        """Generate a response for a character based on context.
        
        Args:
            character: The character for whom to generate a response
            context: List of previous messages/events in the conversation
            prompt: Optional additional instructions for the AI
            
        Returns:
            str: The generated response text
        """
        pass


class OpenAIAdapter(AIAdapter):
    """Adapter for OpenAI's API.
    
    This adapter uses OpenAI's API to generate responses for characters.
    It requires an API key to be set in the OPENAI_API_KEY environment variable.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the OpenAI adapter.
        
        Args:
            api_key: Optional API key for OpenAI. If not provided, will try to get from
                    OPENAI_API_KEY environment variable.
        """
        # Track the source of the API key for logging purposes
        self.api_key_source = "passed directly" if api_key else "environment variable"
        
        self.api_key = api_key
        if not self.api_key:
            self.api_key = os.environ.get("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError("OpenAI API key not provided. Please set OPENAI_API_KEY environment variable.")

        # Log the API key source to log only, not to the chat window
        logging.info(f"OpenAI API key source: {self.api_key_source}")
        
        openai.api_key = self.api_key
        self.client = openai.OpenAI(api_key=self.api_key)
    
    def generate_response(self, character: Character, context: List[Dict[str, Any]], 
                         prompt: Optional[str] = None) -> str:
        """Generate a response using OpenAI's API.
        
        Args:
            character: The character for whom to generate a response
            context: List of previous messages/events in the conversation
            prompt: Optional additional instructions for the AI
            
        Returns:
            str: The generated response text
        """
        # Create a system message that describes the character
        system_message = f"""You are roleplaying as {character.name}, a character with the following attributes:
- Leadership: {character.leadership}/100
- Intelligence: {character.intelligence}/100
- Resilience: {character.resilience}/100

Your current emotion is: {character.current_emotion.name}

You have {len(character.friends)} friends and {len(character.enemies)} enemies.
Friends: {', '.join([friend.name for friend in character.friends]) if character.friends else 'None'}
Enemies: {', '.join([enemy.name for enemy in character.enemies]) if character.enemies else 'None'}

Respond as this character would, maintaining their personality and current emotional state.
Keep responses concise and in-character.
"""
        
        if prompt:
            system_message += f"\n\nAdditional instructions: {prompt}"
        
        # Convert context to the format expected by OpenAI
        messages = [{"role": "system", "content": system_message}]
        
        for item in context:
            if item.get("type") == "dialogue":
                speaker = item.get("speaker", "")
                text = item.get("text", "")
                if speaker == character.name:
                    messages.append({"role": "assistant", "content": text})
                else:
                    messages.append({"role": "user", "content": f"{speaker}: {text}"})
        
        # Generate response
        try:
            response = self.client.chat.completions.create(
                model="o4-mini",
                messages=messages,
                max_tokens=150,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            # Log the error to logs only, not to the chat window
            import logging
            logging.error(f"Error generating response from OpenAI: {e}")
            return f"I'm not sure how to respond to that."


class Chatbot:
    """Chatbot for controlling characters in the game.
    
    This class provides functionality for AI to assume control over characters
    and generate responses based on the character's attributes and conversation context.
    """
    
    def __init__(self, character: Character, adapter: Optional[AIAdapter] = None):
        """Initialize a new Chatbot instance.
        
        Args:
            character: The character to be controlled by this chatbot
            adapter: The AI adapter to use for generating responses. If None, uses OpenAIAdapter.
        """
        self.character = character
        self.adapter = adapter or self._create_default_adapter()
        self.conversation_history = []
        self.is_active = False
    
    def _create_default_adapter(self) -> AIAdapter:
        """Create the default AI adapter.
        
        Returns:
            AIAdapter: The default AI adapter (OpenAIAdapter)
        """
        try:
            return OpenAIAdapter()
        except (ImportError, ValueError) as e:
            print(f"Warning: Could not create default OpenAI adapter: {e}")
            # Return a simple adapter that just returns a fixed message
            class SimpleAdapter(AIAdapter):
                def generate_response(self, character, context, prompt=None):
                    return f"[{character.name} would respond here, but AI is not configured]"
            return SimpleAdapter()
    
    def activate(self):
        """Activate the chatbot to take control of the character."""
        self.is_active = True
        # Log the activation of the chatbot (to logs only, not to chat window)
        import logging
        api_key_source = getattr(self.adapter, 'api_key_source', 'unknown source') if hasattr(self.adapter, 'api_key_source') else 'unknown source'
        logging.info(f"AI assuming control of character: {self.character.name} (API key from {api_key_source})")
    
    def deactivate(self):
        """Deactivate the chatbot, returning control to the game."""
        self.is_active = False
    
    def add_to_history(self, entry: Dict[str, Any]):
        """Add an entry to the conversation history.
        
        Args:
            entry: Dictionary containing information about the dialogue or event
        """
        self.conversation_history.append(entry)
        # Keep history to a reasonable size to avoid token limits
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
    
    def generate_response(self, prompt: Optional[str] = None) -> str:
        """Generate a response for the character.
        
        Args:
            prompt: Optional additional instructions for the AI
            
        Returns:
            str: The generated response text
        """
        if not self.is_active:
            return ""
        
        return self.adapter.generate_response(
            self.character, 
            self.conversation_history,
            prompt
        )