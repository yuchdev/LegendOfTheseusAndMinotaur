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
            # Take control of all present characters using chatbots
            # This event allows AI to assume control over all present characters and generate
            # responses on their behalf based on their attributes and conversation context
            
            # Log the AI assume control event (to logs only, not to chat window)
            import logging
            import os
            import json
            import random
            
            # Get the write_to and dialog_directions fields from the payload
            write_to = self.payload.get("write_to", "") if self.payload else ""
            dialog_directions = self.payload.get("dialog_directions", []) if self.payload else []
            
            logging.info(f"Processing AI_ASSUME_CONTROL event with write_to: {write_to}")
            
            # Choose a random dialog direction if there are multiple
            if dialog_directions:
                chosen_direction = random.choice(dialog_directions)
                logging.info(f"Chosen dialog direction: {chosen_direction}")
            else:
                chosen_direction = ""
                logging.warning("No dialog directions provided")
            
            # Ensure the group has a chatbots dictionary
            if not hasattr(group, 'chatbots'):
                group.chatbots = {}  # Initialize chatbots dictionary if it doesn't exist
                logging.info(f"Initialized chatbots dictionary for group")
            
            # Take control of all present characters
            present_characters = list(group.members)
            logging.info(f"Taking control of {len(present_characters)} present characters")
            
            # Initialize chatbots for all present characters
            for character in present_characters:
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
            
            # Pre-generate messages based on dialog directions
            if chosen_direction and write_to:
                # Log detailed information about the event
                logging.info(f"AI_ASSUME_CONTROL event details:")
                logging.info(f"  - write_to: {write_to}")
                logging.info(f"  - chosen_direction: {chosen_direction}")
                logging.info(f"  - present_characters: {[char.name for char in present_characters]}")
                
                # Create the directory if it doesn't exist
                os.makedirs(os.path.dirname(os.path.join("resources", "scripted_events", write_to)), exist_ok=True)
                
                # Generate a prompt for the AI to pre-generate messages
                prompt = f"""
                You are controlling a conversation between the following characters:
                {', '.join([char.name for char in present_characters])}
                
                Please generate a conversation based on the following direction:
                {chosen_direction}
                
                Format the conversation as a list of JSON objects, each with the following fields:
                - character: The name of the speaking character
                - to: The name of the character being addressed (empty string if speaking to everyone)
                - mood: The emotion of the speaker (e.g., curious, angry, calm)
                - text: The text of the message
                - event_type: Always "dialogue"
                
                Example:
                [
                  {{
                    "character": "Character1",
                    "to": "Character2",
                    "mood": "curious",
                    "text": "What do you think about this situation?",
                    "event_type": "dialogue"
                  }},
                  {{
                    "character": "Character2",
                    "to": "Character1",
                    "mood": "calm",
                    "text": "I'm not sure, but we should be careful.",
                    "event_type": "dialogue"
                  }}
                ]
                """
                
                logging.info(f"Generated prompt for AI conversation:\n{prompt}")
                
                # Use the first character's chatbot to generate the conversation
                if present_characters:
                    first_character = present_characters[0]
                    if first_character in group.chatbots:
                        first_chatbot = group.chatbots[first_character]
                        
                        # Generate the conversation
                        logging.info(f"Generating conversation using {first_character.name}'s chatbot")
                        conversation_json = first_chatbot.generate_response(prompt)
                        
                        try:
                            # Check if the response is empty
                            if not conversation_json or conversation_json.strip() == "":
                                logging.warning("Empty response from AI, generating a simple conversation instead")
                                
                                # Generate a simple conversation based on the dialog direction
                                conversation = []
                                
                                # Generate a hardcoded conversation based on the dialog direction
                                # This is a simplified implementation for testing purposes
                                
                                # Add the conversation between Romeo and Nutscracker
                                conversation.append({
                                    "character": "Romeo-y-Cohiba",
                                    "to": "Nutscracker",
                                    "mood": "curious",
                                    "text": "Why are you so sure the message has been there for a long time?",
                                    "event_type": "dialogue"
                                })
                                conversation.append({
                                    "character": "Nutscracker",
                                    "to": "Romeo-y-Cohiba",
                                    "mood": "calm",
                                    "text": "I saw it several hours ago when I first logged in.",
                                    "event_type": "dialogue"
                                })
                                
                                # Add questions about how they ended up here
                                conversation.append({
                                    "character": "Romeo-y-Cohiba",
                                    "to": "",
                                    "mood": "confused",
                                    "text": "Do any of you remember how we ended up here?",
                                    "event_type": "dialogue"
                                })
                                conversation.append({
                                    "character": "Nutscracker",
                                    "to": "",
                                    "mood": "anxious",
                                    "text": "I don't remember anything before waking up in this room.",
                                    "event_type": "dialogue"
                                })
                                conversation.append({
                                    "character": "Organizm(-:",
                                    "to": "",
                                    "mood": "contemplative",
                                    "text": "It's like my memory has been wiped clean. I just found myself here with this computer.",
                                    "event_type": "dialogue"
                                })
                                
                                logging.info(f"Generated simple conversation with {len(conversation)} events")
                            else:
                                # Parse the JSON response
                                # The response might include markdown code block formatting, so we need to extract the JSON part
                                import re
                                logging.info(f"Raw response from AI: {conversation_json}")
                                
                                json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', conversation_json)
                                if json_match:
                                    conversation_json = json_match.group(1)
                                    logging.info(f"Extracted JSON from code block: {conversation_json}")
                                
                                # Parse the JSON
                                conversation = json.loads(conversation_json)
                                logging.info(f"Successfully parsed JSON: {len(conversation)} events")
                            
                            # Write the conversation to the specified file
                            output_path = os.path.join("resources", "scripted_events", write_to)
                            with open(output_path, 'w') as f:
                                json.dump(conversation, f, indent=2)
                            
                            logging.info(f"Wrote pre-generated conversation to {output_path}")
                            
                            # Print a message to the chat window
                            print(f"\nAI has taken control of all present characters and pre-generated a conversation.")
                            print(f"The conversation will be played out in the next steps.\n")
                            
                        except Exception as e:
                            logging.error(f"Error processing AI-generated conversation: {e}")
                            logging.error(f"Raw response: {conversation_json}")
                            print(f"\nError processing AI-generated conversation. See logs for details.\n")
                    else:
                        logging.error(f"No chatbot found for {first_character.name}")
                        print(f"\nError: No chatbot found for {first_character.name}. See logs for details.\n")
                else:
                    logging.error("No present characters found")
                    print("\nError: No present characters found. See logs for details.\n")
            
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
