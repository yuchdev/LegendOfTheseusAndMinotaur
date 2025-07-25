"""
Game module for the text-based game quest.

This module defines the Game class, which is the main entry point for the game.
It handles initializing characters, loading and running chapters, and managing
the game state. It also provides utility functions for parsing chapter arguments
and running multiple chapters.
"""

import sys
import json
import random
from constants import CHARACTERS, resolve_character
from character import Character
from group import Group
from event import Event, EventType


class Game:
    """Main game class that manages the game state and progression.

    The Game class is responsible for initializing characters, loading chapter data
    from JSON files, and running the game loop. It maintains a collection of characters
    and a group that represents the current state of character interactions.

    The game progresses by loading and processing events from chapter files, which
    can include dialogue between characters, characters entering or leaving the group,
    and other game events.
    """
    def __init__(self):
        """Initialize a new Game instance.

        Creates a new game with an empty collection of characters and a new group.
        Initializes the characters with default attributes by calling initialize_characters().
        """
        self.characters = {}  # name -> Character
        self.group = Group()
        self.events = []
        self.initialize_characters()

    def initialize_characters(self):
        """Initialize characters with default attributes.

        Creates Character instances for all canonical characters defined in the CHARACTERS
        constant. Each character is initialized with specific attributes (leadership,
        intelligence, resilience) and special properties as defined in the character_attributes
        dictionary.

        The created characters are stored in the self.characters dictionary, keyed by
        their names.
        """
        character_attributes = {
            "Monstradamus": {
                "leadership": 85,
                "intelligence": 95,
                "resilience": 75
            },
            "IsoldA": {
                "leadership": 60,
                "intelligence": 75,
                "resilience": 65
            },
            "Nutscracker": {
                "leadership": 70,
                "intelligence": 90,
                "resilience": 55
            },
            "Organizm(-:": {
                "leadership": 40,
                "intelligence": 65,
                "resilience": 45
            },
            "Theseus": {
                "leadership": 80,
                "intelligence": 70,
                "resilience": 75
            },
            "Ariadne": {
                "leadership": 65,
                "intelligence": 85,
                "resilience": 65
            },
            "UGLI 666": {
                "leadership": 55,
                "intelligence": 60,
                "resilience": 45
            },
            "Romeo-y-Cohiba": {
                "leadership": 55,
                "intelligence": 65,
                "resilience": 35
            },
            "Sartrik": {
                "leadership": 50,
                "intelligence": 95,
                "resilience": 55,
                "special_properties": [lambda self, other: other.intelligence > 80]
            }
        }

        # Create all characters
        for name in CHARACTERS:
            attrs = character_attributes.get(name, {})
            special_props = attrs.pop("special_properties", None)
            self.characters[name] = Character(name, **attrs, special_properties=special_props)

    def load_day(self, day_file):
        """Load a day from a JSON file and convert it to a list of Event objects.

        Reads the specified JSON file, which should contain a list of event entries.
        Each entry is converted to the appropriate Event type based on the event_type field.

        Args:
            day_file (str): Path to the JSON file containing the day data

        Returns:
            list: A list of Event objects representing the day's events
        """
        with open(day_file, 'r') as f:
            day_data = json.load(f)

        events = []
        for entry in day_data:
            event_type_str = entry.get("event_type", "dialogue")

            # Handle different event types
            if event_type_str == "day_start":
                event = Event(event_type=EventType.DAY_START)
                events.append(event)
                continue
            elif event_type_str == "day_end":
                event = Event(event_type=EventType.DAY_END)
                events.append(event)
                continue
            elif event_type_str == "environment_change":
                # For environment_change events, we need a character
                char_name = entry.get("character", "")
                char_canonical, _ = resolve_character(char_name) if char_name else (None, None)
                character = self.characters.get(char_canonical)
                event = Event(
                    event_type=EventType.ENVIRONMENT_CHANGE,
                    actor=character,
                    payload=entry.get("payload", "")
                )
                events.append(event)
                continue

            # For events that require a character
            char_name = entry.get("character")
            if not char_name:
                print(f"Warning: Event {event_type_str} missing character field")
                continue

            char_canonical, _ = resolve_character(char_name)
            if not char_canonical:
                print(f"Warning: Unknown character {char_name}")
                continue

            character = self.characters.get(char_canonical)
            if not character:
                print(f"Warning: Character {char_canonical} not initialized")
                continue

            if event_type_str == "enter":
                event = Event(
                    event_type=EventType.ENTER,
                    actor=character
                )
                events.append(event)
            elif event_type_str == "leave":
                event = Event(
                    event_type=EventType.LEAVE,
                    actor=character
                )
                events.append(event)
            elif event_type_str == "offended":
                # Get the target character for offended events
                target = None
                target_name = entry.get("target")
                if target_name:
                    target_canonical, _ = resolve_character(target_name)
                    if target_canonical and target_canonical in self.characters:
                        target = self.characters[target_canonical]

                event = Event(
                    event_type=EventType.OFFENDED,
                    actor=character,
                    target=target
                )
                events.append(event)
            elif event_type_str == "ai_assume_control":
                # Create an AI_ASSUME_CONTROL event
                # This event allows AI to silently take control of a character
                # When processed, it will create and activate a chatbot for the character
                # The chatbot will generate responses based on the character's attributes and conversation context
                event = Event(
                    event_type=EventType.AI_ASSUME_CONTROL,
                    actor=character
                )
                events.append(event)
            elif event_type_str == "user_assume_control":
                # Create a USER_ASSUME_CONTROL event
                # This event allows the user to take control of a character
                # When processed, it will create and activate a UserControl for the character
                # The user will be presented with AI-generated response options when the character is addressed
                event = Event(
                    event_type=EventType.USER_ASSUME_CONTROL,
                    actor=character
                )
                events.append(event)
            elif event_type_str == "return_to_script":
                # Create a RETURN_TO_SCRIPT event
                # This event returns character control from AI or user back to script
                # When processed, it will deactivate both chatbot and user control for the character
                event = Event(
                    event_type=EventType.RETURN_TO_SCRIPT,
                    actor=character
                )
                events.append(event)
            elif event_type_str == "dialogue" or not event_type_str:
                # Get the target character(s) for dialogue
                target = None
                to_field = entry.get("to", "")
                if to_field:
                    if isinstance(to_field, list):
                        target = []
                        for target_name in to_field:
                            target_canonical, _ = resolve_character(target_name)
                            if target_canonical and target_canonical in self.characters:
                                target.append(self.characters[target_canonical])
                    else:
                        target_canonical, _ = resolve_character(to_field)
                        if target_canonical and target_canonical in self.characters:
                            target = self.characters[target_canonical]

                # Create a dialogue event
                event = Event(
                    event_type=EventType.DIALOGUE,
                    actor=character,
                    target=target,
                    payload={
                        "text": entry.get("text", ""),
                        "emotion": entry.get("mood", "neutral")
                    }
                )
                events.append(event)
            else:
                print(f"Warning: Unknown event type {event_type_str}")

        return events

    def run_day(self, day_file):
        """Run a day from a JSON file.

        This method loads a day from the specified JSON file, adds all characters
        to the group, and processes each event in the day. It displays the initial
        and final state of the group, as well as periodic status updates during the day.

        The method performs the following steps:
        1. Load the day events using load_day()
        2. Add all characters to the group
        3. Display the initial group state
        4. Process each event, applying it to the group
        5. Periodically display group status updates (5% chance after each event)
        6. Display the final group state

        Args:
            day_file (str): Path to the JSON file containing the day data
        """
        events = self.load_day(day_file)

        # Add all characters to the group initially
        for character in self.characters.values():
            self.group.add(character)

        print(f"\n=== Starting Day: {day_file} ===\n")
        print(
            f"Initial group state: {len(self.group.members)} members, mood: {self.group.get_dominant_mood().name}, tension: {self.group.get_tension_description()} ({self.group.tension:.4f})\n")

        # Process each event
        for event in events:
            event.apply(self.group)

            # After each event, show group status periodically
            if random.random() < 0.05:  # 5% chance to show status
                print(
                    f"\nGroup status: {len(self.group.members)} members, mood: {self.group.get_dominant_mood().name}, tension: {self.group.get_tension_description()} ({self.group.tension:.4f})")

                # Show some character relationships
                if self.group.members:
                    char = random.choice(self.group.members)
                    print(f"{char.name}'s current emotion: {char.current_emotion.name}")
                    for other in self.group.members:
                        if char != other and other in self.group.emotions.get(char, {}):
                            print(f"  → Feels {self.group.emotions[char][other].name} towards {other.name}")
                print()

        print(f"\n=== Day Complete ===")
        print(
            f"Final group state: {len(self.group.members)} members, mood: {self.group.get_dominant_mood().name}, tension: {self.group.get_tension_description()} ({self.group.tension:.4f})\n")


def parse_day_arg(arg):
    """
    Parse the day argument to determine if it's a single day or a range

    Args:
        arg (str): The day argument (e.g., "01", "01-03")

    Returns:
        list: A list of day numbers to run
    """
    if "-" in arg:
        # It's a range
        start, end = arg.split("-")
        try:
            start_num = int(start)
            end_num = int(end)
            return [f"{i:02d}" for i in range(start_num, end_num + 1)]
        except ValueError:
            print(f"Invalid day range: {arg}")
            return ["01"]  # Default to day 01
    else:
        # It's a single day
        try:
            # Ensure it's a valid number and format as 2 digits
            day_num = int(arg)
            return [f"{day_num:02d}"]
        except ValueError:
            # If it's already a full path, return it as is
            if arg.endswith(".json") and "/" in arg:
                return [arg]
            print(f"Invalid day number: {arg}")
            return ["01"]  # Default to day 01

def run_days(game, day_numbers):
    """
    Run a sequence of days

    Args:
        game (Game): The game instance
        day_numbers (list): List of day numbers to run
    """
    for i, day_num in enumerate(day_numbers):
        # Convert day number to filename if it's not already a path
        if not day_num.endswith(".json"):
            day_file = f"play_chapters/day-{day_num}.json"
        else:
            day_file = day_num

        # Add a day separator if this isn't the first day
        if i > 0:
            print("\n" + "="*50)
            print(f"=== DAY {i+1} ===")
            print("="*50 + "\n")

        # Run the day
        game.run_day(day_file)

def main():
    """
    Main entry point for the game.

    Usage:
        python game.py                # Run day 01
        python game.py 01             # Run day 01
        python game.py 01-03          # Run days 01, 02, and 03 in sequence
        python game.py path/to/file.json  # Run a specific day file

    :return: system exit code
    """
    if len(sys.argv) > 1:
        day_arg = sys.argv[1]
        day_numbers = parse_day_arg(day_arg)
    else:
        day_numbers = ["01"]  # Default to day 01

    game = Game()
    run_days(game, day_numbers)

    exit()



if __name__ == "__main__":
    sys.exit(main())
