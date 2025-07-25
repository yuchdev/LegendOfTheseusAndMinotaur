"""
Event module for the text-based game quest.

This module defines the EventType enum and Event class, which represent different
types of events that can occur in the game and their effects on the game state.
Events include character dialogue, characters entering or leaving the group,
characters being offended, and various other game events.
"""

from enum import Enum, auto
from typing import Any, List, Dict, Optional
from datetime import datetime
from character import Character
from group import Group
from emotion import Emotion
from chatbot import Chatbot
from user_control import UserControl

class EventType(Enum):
    """Enumeration of different types of events that can occur in the game.

    Each event type represents a different kind of action or occurrence that
    can affect the game state, such as dialogue between characters, characters
    entering or leaving the group, or changes in the game world.
    """
    DAY_START = auto()
    DAY_END = auto()
    DIALOGUE = auto()
    ENTER = auto()
    LEAVE = auto()
    OFFENDED = auto()
    ENVIRONMENT_CHANGE = auto()
    # Event type for AI to silently take control of a character
    AI_ASSUME_CONTROL = auto()
    # Event type for user to assume control of a character
    USER_ASSUME_CONTROL = auto()
    # Event type to return character control from AI or user back to script
    RETURN_TO_SCRIPT = auto()

class Event:
    """Represents an event that can occur in the game.

    An event is something that happens in the game world that can affect the game state.
    Events have a type (from EventType), an actor (the character initiating the event),
    an optional target (another character or object affected by the event), and an
    optional payload (additional data specific to the event type).

    Events can be applied to a group to modify the group state according to the
    event's type and data.
    """
    def __init__(
        self,
        event_type: EventType,
        timestamp: datetime = None,
        actor: Character = None,
        target: Any = None,
        payload: Any = None
    ):
        """Initialize a new Event instance.

        Args:
            event_type (EventType): The type of event (DIALOGUE, ENTER, LEAVE, etc.)
            timestamp (datetime, optional): When the event occurred. Defaults to current time.
            actor (Character, optional): The character initiating the event. Defaults to None.
            target (Any, optional): The target of the event (another character, object, etc.). 
                Defaults to None.
            payload (Any, optional): Additional data specific to the event type. For DIALOGUE
                events, this would include the text and emotion. Defaults to None.
        """
        self.event_type = event_type
        self.timestamp = timestamp or datetime.utcnow()
        self.actor = actor
        self.target = target
        self.payload = payload  # e.g. the line text, or reason for leaving

    def apply(self, group: Group):
        """Apply the event's effects to a group.

        This method applies the event to the given group, modifying the group state
        according to the event type. Different event types have different effects:

        - ENTER: Adds the actor to the group
        - LEAVE: Removes the actor from the group
        - DIALOGUE: Processes dialogue between characters, updating emotions and relationships
        - OFFENDED: Makes the actor hostile toward the target
        - Other event types: Currently just print information

        The method also handles printing appropriate messages to describe the event.

        Args:
            group (Group): The group to which the event should be applied
        """
        if self.event_type == EventType.DAY_START:
            print("It is now daytime.")
        elif self.event_type == EventType.DAY_END:
            print("It is now nighttime.")
        elif self.event_type == EventType.ENTER:
            group.add(self.actor)
            print(f"{self.actor.name} has entered the chatroom.")

        elif self.event_type == EventType.LEAVE:
            group.remove(self.actor)
            print(f"{self.actor.name} has left the chatroom.")

        elif self.event_type == EventType.DIALOGUE:
            speaker, addressed_to, text, emotion = self.actor, self.target, self.payload.get("text", ""), self.payload.get("emotion")
            
            # Check if the speaker is under AI or user control
            is_under_ai_control = False
            is_under_user_control = False
            
            if hasattr(group, 'chatbots') and speaker in group.chatbots and group.chatbots[speaker].is_active:
                is_under_ai_control = True
            if hasattr(group, 'user_controls') and speaker in group.user_controls and group.user_controls[speaker].is_active:
                is_under_user_control = True
                
            # If the speaker is under control, generate a response instead of using the scripted line
            if is_under_ai_control:
                # Log AI control information to logs only, not to chat window
                import logging
                logging.info(f"Character {speaker.name} is under AI control - generating AI response instead of using scripted line")
                
                # Add the addressed character's line to the chatbot's conversation history
                if addressed_to:
                    # Format the target for the conversation history
                    target_name = ""
                    if isinstance(addressed_to, list):
                        target_name = ", ".join([char.name for char in addressed_to])
                    else:
                        target_name = addressed_to.name
                    
                    # Log the original scripted line that's being replaced (to logs only, not to chat window)
                    logging.info(f"Original scripted line: {speaker.name} [to {target_name}, {emotion}]: {text}")
                
                # Generate an AI response
                chatbot = group.chatbots[speaker]
                
                # Add the current context to the chatbot's history
                # This helps the AI understand what it's responding to
                if addressed_to:
                    chatbot.add_to_history({
                        "type": "dialogue",
                        "speaker": "System",
                        "text": f"You are being addressed by {addressed_to.name if not isinstance(addressed_to, list) else ', '.join([char.name for char in addressed_to])}"
                    })
                
                # Generate the AI response
                ai_response = chatbot.generate_response()
                # Log the AI-generated response to logs only, not to chat window
                import logging
                logging.info(f"AI-generated response for {speaker.name}: {ai_response}")
                
                # Format and display the AI-generated dialogue (without AI-controlled tag for seamless experience)
                if addressed_to:
                    if isinstance(addressed_to, list):
                        addressed_names = ", ".join([char.name for char in addressed_to])
                        print(f"{speaker.name} [to {addressed_names}, {emotion}]: {ai_response}")
                    else:
                        print(f"{speaker.name} [to {addressed_to.name}, {emotion}]: {ai_response}")
                else:
                    print(f"{speaker.name} [{emotion}]: {ai_response}")
                
                # Apply the dialogue effects using the AI-generated response
                if isinstance(addressed_to, list):
                    for target in addressed_to:
                        group.apply_line(speaker, ai_response, target, Emotion.from_string(emotion) if isinstance(emotion, str) else emotion)
                elif addressed_to:
                    group.apply_line(speaker, ai_response, addressed_to, Emotion.from_string(emotion) if isinstance(emotion, str) else emotion)
                
            elif is_under_user_control:
                # Stub for user-controlled characters
                import logging
                logging.info(f"Character {speaker.name} is under user control - user control response generation not implemented yet")
                logging.info(f"Original scripted line would have been: {speaker.name} [{emotion}]: {text}")
                # TODO: Implement user control response generation
                
                # For now, just display the scripted line as if it's from the user
                if addressed_to:
                    if isinstance(addressed_to, list):
                        addressed_names = ", ".join([char.name for char in addressed_to])
                        print(f"{speaker.name} [to {addressed_names}, {emotion}]: {text}")
                    else:
                        print(f"{speaker.name} [to {addressed_to.name}, {emotion}]: {text}")
                else:
                    print(f"{speaker.name} [{emotion}]: {text}")
                    
                # Apply the dialogue effects using the scripted line
                if isinstance(addressed_to, list):
                    for target in addressed_to:
                        group.apply_line(speaker, text, target, Emotion.from_string(emotion) if isinstance(emotion, str) else emotion)
                elif addressed_to:
                    group.apply_line(speaker, text, addressed_to, Emotion.from_string(emotion) if isinstance(emotion, str) else emotion)
            else:
                # Process the dialogue normally for characters not under control
                
                # Format the dialogue output
                if addressed_to:
                    if isinstance(addressed_to, list):
                        addressed_names = ", ".join([char.name for char in addressed_to])
                        print(f"{speaker.name} [to {addressed_names}, {emotion}]: {text}")
                    else:
                        print(f"{speaker.name} [to {addressed_to.name}, {emotion}]: {text}")
                else:
                    print(f"{speaker.name} [{emotion}]: {text}")
    
                # Apply the dialogue effects
                if isinstance(addressed_to, list):
                    for target in addressed_to:
                        group.apply_line(speaker, text, target, Emotion.from_string(emotion) if isinstance(emotion, str) else emotion)
                else:
                    group.apply_line(speaker, text, addressed_to, Emotion.from_string(emotion) if isinstance(emotion, str) else emotion)

        elif self.event_type == EventType.OFFENDED:
            # actor takes offense at target → hostility
            if self.actor in group.members and self.target in group.members:
                group.emotions[self.actor][self.target] = Emotion.HOSTILE
                print(f"{self.actor.name} is offended by {self.target.name}!")
                group.update_mood()

        elif self.event_type == EventType.ENVIRONMENT_CHANGE:
            if self.actor:
                print(f"{self.actor.name}: ENVIRONMENT CHANGE: {self.payload}".upper())
            else:
                print(f"ENVIRONMENT CHANGE: {self.payload}".upper())
            
        elif self.event_type == EventType.AI_ASSUME_CONTROL:
            # Take control of the character using a chatbot
            # This event allows AI to assume control over a character and generate
            # responses on their behalf based on their attributes and conversation context
            
            # Log the AI assume control event (to logs only, not to chat window)
            import logging
            logging.info(f"Processing AI_ASSUME_CONTROL event for character: {self.actor.name}")
            
            # Ensure the group has a chatbots dictionary
            if not hasattr(group, 'chatbots'):
                group.chatbots = {}  # Initialize chatbots dictionary if it doesn't exist
                logging.info(f"Initialized chatbots dictionary for group")
                
            character = self.actor
            if character not in group.chatbots:
                # Create a new chatbot for this character if one doesn't exist
                logging.info(f"Creating new chatbot for character: {character.name}")
                # Pass the group to the chatbot so it can access the full day's context
                group.chatbots[character] = Chatbot(character, group=group)
            else:
                logging.info(f"Using existing chatbot for character: {character.name}")
                # Update the group reference in case it changed
                group.chatbots[character].group = group
                
            # Activate the chatbot to take control of the character
            # The activate method will log details about the activation and API key source
            group.chatbots[character].activate()
            
        elif self.event_type == EventType.USER_ASSUME_CONTROL:
            # Allow the user to take control of the character
            # This event enables the user to control a character and choose from
            # AI-generated response options when the character is addressed
            
            # Log the USER_ASSUME_CONTROL event (to logs only, not to chat window)
            import logging
            logging.info(f"Processing USER_ASSUME_CONTROL event for character: {self.actor.name}")
            
            # Ensure the group has a user_controls dictionary
            if not hasattr(group, 'user_controls'):
                group.user_controls = {}  # Initialize user_controls dictionary if it doesn't exist
                logging.info(f"Initialized user_controls dictionary for group")
                
            character = self.actor
            if character not in group.user_controls:
                # Create a new UserControl for this character if one doesn't exist
                logging.info(f"Creating new UserControl for character: {character.name}")
                group.user_controls[character] = UserControl(character)
            else:
                logging.info(f"Using existing UserControl for character: {character.name}")
                
            # Activate user control for the character
            group.user_controls[character].activate()
            
        elif self.event_type == EventType.RETURN_TO_SCRIPT:
            # Return character control from AI or user back to script
            # This event deactivates both chatbot and user control for the character
            
            import logging
            logging.info(f"Processing RETURN_TO_SCRIPT event for character: {self.actor.name}")
            
            character = self.actor
            
            # Deactivate chatbot if it exists and is active
            if hasattr(group, 'chatbots') and character in group.chatbots:
                group.chatbots[character].deactivate()
                logging.info(f"{character.name} is now following the script again.")
                
            # Deactivate user control if it exists and is active
            if hasattr(group, 'user_controls') and character in group.user_controls:
                group.user_controls[character].deactivate()
                logging.info(f"User control deactivated for {character.name}.")


    def __repr__(self):
        """Return a string representation of the event.

        Returns:
            str: A string representation in the format "<Event type by actor>"
        """
        return f"<Event {self.event_type} by {self.actor}>"
