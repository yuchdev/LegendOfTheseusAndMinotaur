#!/usr/bin/env python3
"""
Example script demonstrating the chatbot functionality.

This script shows how to use the AI_ASSUME_CONTROL event to make characters
respond using AI-generated dialogue.

Note: This script requires an OpenAI API key to be set in the OPENAI_API_KEY
environment variable or provided directly to the OpenAIAdapter.
"""

import os
import sys
from character import Character
from group import Group
from event import Event, EventType
from emotion import Emotion
from chatbot import Chatbot, OpenAIAdapter

def main():
    # Check if OpenAI API key is set
    if not os.environ.get("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY environment variable not set.")
        print("The script will run, but AI responses will be placeholders.")
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
    
    # Make AI assume control of Ariadne (silently)
    # This event is only logged, not displayed in the chat window
    ai_control_event = Event(
        event_type=EventType.AI_ASSUME_CONTROL,
        actor=ariadne
    )
    ai_control_event.apply(group)
    print()
    
    # Now when Theseus speaks to Ariadne, she will respond with AI-generated dialogue
    # but the user won't see any indication that AI is controlling Ariadne
    print("=== Continuing dialogue ===")
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
    
    # The AI response will be automatically generated and applied
    # If OpenAI API key is not set, a placeholder response will be used
    
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
    
    # Manually create and use a chatbot (silently)
    print("=== Theseus responds to Ariadne ===")
    # Create a chatbot for Theseus
    theseus_chatbot = Chatbot(theseus)
    
    # Add some conversation history
    theseus_chatbot.add_to_history({
        "type": "dialogue",
        "speaker": "Ariadne",
        "text": "Theseus, we need to find a way to defeat the Minotaur.",
        "emotion": "CONCERNED"
    })
    
    # Activate the chatbot (silently)
    theseus_chatbot.activate()
    
    # Generate a response
    response = theseus_chatbot.generate_response(
        prompt="Make the response brave and determined"
    )
    
    # Display the response without indicating it's AI-generated
    print(f"Theseus [determined]: {response}")
    print()
    
    print("=== Example complete ===")

if __name__ == "__main__":
    main()