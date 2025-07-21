"""
User Control module for the text-based game quest.

This module defines the UserControl class, which allows users to assume control over
characters in the game. The UserControl class provides an interface for generating
response options and handling user input.
"""

from typing import Dict, List, Optional, Any
from character import Character
from chatbot import AIAdapter, OpenAIAdapter

class UserControl:
    """UserControl for allowing users to control characters in the game.
    
    This class provides functionality for users to assume control over characters
    and choose from AI-generated response options or provide their own responses.
    """
    
    def __init__(self, character: Character, adapter: Optional[AIAdapter] = None):
        """Initialize a new UserControl instance.
        
        Args:
            character: The character to be controlled by the user
            adapter: The AI adapter to use for generating response options. If None, uses OpenAIAdapter.
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
        """Activate user control for the character."""
        self.is_active = True
        print(f"You are now controlling {self.character.name}.")
    
    def deactivate(self):
        """Deactivate user control, returning control to the game."""
        self.is_active = False
        print(f"You are no longer controlling {self.character.name}.")
    
    def add_to_history(self, entry: Dict[str, Any]):
        """Add an entry to the conversation history.
        
        Args:
            entry: Dictionary containing information about the dialogue or event
        """
        self.conversation_history.append(entry)
        # Keep history to a reasonable size to avoid token limits
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
    
    def generate_response_options(self, num_options: int = 3) -> List[str]:
        """Generate multiple response options for the user to choose from.
        
        Args:
            num_options: Number of response options to generate
            
        Returns:
            List[str]: List of generated response options
        """
        if not self.is_active:
            return []
        
        # Create a prompt that asks for multiple response options
        prompt = f"Generate {num_options} different response options for {self.character.name}. " \
                f"Each option should be a complete response and reflect the character's personality. " \
                f"Format the response as a numbered list (1., 2., etc.)."
        
        # Generate response options using the AI adapter
        response = self.adapter.generate_response(
            self.character,
            self.conversation_history,
            prompt
        )
        
        # Parse the response into a list of options
        options = []
        for line in response.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('- ')):
                # Remove the number/bullet and any following punctuation
                option = line.split('.', 1)[-1].strip()
                if len(option) > 0:
                    options.append(option)
        
        # If parsing failed or returned fewer options than requested, create some defaults
        while len(options) < num_options:
            options.append(f"[Option {len(options)+1} for {self.character.name}]")
        
        return options
    
    def present_options(self, options: List[str]) -> str:
        """Present response options to the user and get their choice.
        
        Args:
            options: List of response options to present
            
        Returns:
            str: The selected response (from options, custom input, or empty if skipped)
        """
        if not options:
            return ""
        
        print(f"\n--- {self.character.name}'s Response Options ---")
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        print("C. Type your own response")
        print("S. Skip (let another character respond)")
        print("----------------------------------------")
        
        while True:
            choice = input(f"Choose an option for {self.character.name}: ").strip().upper()
            
            if choice == 'S':
                print(f"Skipping {self.character.name}'s response.")
                return ""
            
            if choice == 'C':
                custom_response = input(f"Enter {self.character.name}'s response: ").strip()
                if custom_response:
                    return custom_response
                print("Response cannot be empty. Please try again.")
                continue
            
            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(options):
                    return options[choice_idx]
                else:
                    print(f"Please enter a number between 1 and {len(options)}, 'C', or 'S'.")
            except ValueError:
                print(f"Please enter a number between 1 and {len(options)}, 'C', or 'S'.")
    
    def handle_addressed(self, speaker: Character) -> str:
        """Handle when the character is addressed by another character.
        
        This method is called when the user-controlled character is addressed
        in a conversation. It generates response options, presents them to the user,
        and returns the selected response.
        
        Args:
            speaker: The character who addressed the user-controlled character
            
        Returns:
            str: The selected response (from options, custom input, or empty if skipped)
        """
        if not self.is_active:
            return ""
        
        # Generate response options
        options = self.generate_response_options()
        
        # Present options to the user and get their choice
        return self.present_options(options)