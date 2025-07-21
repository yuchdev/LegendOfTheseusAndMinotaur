#!/usr/bin/env python3
"""
Example script demonstrating the user control functionality.

This script shows how to use the USER_ASSUME_CONTROL event to make characters
respond using user-selected dialogue options.

Note: This script requires an OpenAI API key to be set in the OPENAI_API_KEY
environment variable or provided directly to the OpenAIAdapter for generating
response options.
"""

import os
import sys
from character import Character
from group import Group
from event import Event, EventType
from emotion import Emotion
from user_control import UserControl

def main():
    # Check if OpenAI API key is set
    if not os.environ.get("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY environment variable not set.")
        print("The script will run, but AI-generated response options may be placeholders.")
        print("Set the OPENAI_API_KEY environment variable to use the OpenAI API.")
        print()

    # Create characters
    theseus = Character("Theseus", leadership=80, intelligence=70, resilience=75)
    ariadne = Character("Ariadne", leadership=65, intelligence=85, resilience=65)
    
    # Make them friends
    theseus.friends.append(ariadne)
    ariadne.friends.append(theseus)
    
    # Create a group
    group = Group([theseus, ariadne])
    
    print("=== Initial state ===")
    print(f"Group has {len(group.members)} members: {', '.join([c.name for c in group.members])}")
    print()
    
    # Simulate some dialogue
    print("=== Normal dialogue ===")
    dialogue_event = Event(
        event_type=EventType.DIALOGUE,
        actor=theseus,
        target=ariadne,
        payload={
            "text": "Hello Ariadne, how are you today?",
            "emotion": "friendly"
        }
    )
    dialogue_event.apply(group)
    
    dialogue_event = Event(
        event_type=EventType.DIALOGUE,
        actor=ariadne,
        target=theseus,
        payload={
            "text": "I'm doing well, Theseus. Thank you for asking.",
            "emotion": "friendly"
        }
    )
    dialogue_event.apply(group)
    print()
    
    # Make user assume control of Ariadne
    print("=== User assuming control of Ariadne ===")
    user_control_event = Event(
        event_type=EventType.USER_ASSUME_CONTROL,
        actor=ariadne
    )
    user_control_event.apply(group)
    print()
    
    # Now when Theseus speaks to Ariadne, the user will be presented with response options
    print("=== Dialogue with user-controlled Ariadne ===")
    print("(Theseus speaks to Ariadne, and you'll be presented with response options)")
    dialogue_event = Event(
        event_type=EventType.DIALOGUE,
        actor=theseus,
        target=ariadne,
        payload={
            "text": "Ariadne, what do you think about the Labyrinth?",
            "emotion": "curious"
        }
    )
    dialogue_event.apply(group)
    
    # The user will be presented with response options and can choose one
    # The selected response will be automatically applied
    
    # Continue the conversation
    dialogue_event = Event(
        event_type=EventType.DIALOGUE,
        actor=theseus,
        target=ariadne,
        payload={
            "text": "That's interesting. Do you think we can find a way out?",
            "emotion": "hopeful"
        }
    )
    dialogue_event.apply(group)
    print()
    
    # Manually create and use a UserControl
    print("=== Manually using UserControl ===")
    # Create a UserControl for Theseus
    theseus_control = UserControl(theseus)
    
    # Add some conversation history
    theseus_control.add_to_history({
        "type": "dialogue",
        "speaker": "Ariadne",
        "text": "Theseus, we need to find a way to defeat the Minotaur.",
        "emotion": "CONCERNED"
    })
    
    # Activate user control
    theseus_control.activate()
    
    # Generate response options and present them to the user
    print("Generating response options for Theseus...")
    options = theseus_control.generate_response_options()
    response = theseus_control.present_options(options)
    
    if response:
        print(f"Theseus [user-selected]: {response}")
    else:
        print("You chose to skip Theseus's response.")
    print()
    
    # Deactivate user control
    theseus_control.deactivate()
    
    print("=== Example complete ===")
    print("This example demonstrated how to use the USER_ASSUME_CONTROL event")
    print("to allow users to control characters and choose from AI-generated")
    print("response options when the character is addressed in a conversation.")

if __name__ == "__main__":
    main()