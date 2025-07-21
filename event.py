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
            print(f"Environment change: {self.payload}")
            
        elif self.event_type == EventType.AI_ASSUME_CONTROL:
            # Silently take control of the character using a chatbot
            # This event allows AI to assume control over a character and generate
            # responses on their behalf based on their attributes and conversation context
            
            # Ensure the group has a chatbots dictionary
            if not hasattr(group, 'chatbots'):
                group.chatbots = {}  # Initialize chatbots dictionary if it doesn't exist
                
            character = self.actor
            if character not in group.chatbots:
                # Create a new chatbot for this character if one doesn't exist
                group.chatbots[character] = Chatbot(character)
                
            # Activate the chatbot to take control of the character
            group.chatbots[character].activate()
            
            # No print statement - the AI silently takes control without notification
            
        elif self.event_type == EventType.USER_ASSUME_CONTROL:
            # Allow the user to take control of the character
            # This event enables the user to control a character and choose from
            # AI-generated response options when the character is addressed
            
            # Ensure the group has a user_controls dictionary
            if not hasattr(group, 'user_controls'):
                group.user_controls = {}  # Initialize user_controls dictionary if it doesn't exist
                
            character = self.actor
            if character not in group.user_controls:
                # Create a new UserControl for this character if one doesn't exist
                group.user_controls[character] = UserControl(character)
                
            # Activate user control for the character
            group.user_controls[character].activate()


    def __repr__(self):
        """Return a string representation of the event.

        Returns:
            str: A string representation in the format "<Event type by actor>"
        """
        return f"<Event {self.event_type} by {self.actor}>"
