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

    def load_chapter(self, chapter_file):
        """Load a chapter from a JSON file and convert it to a list of Event objects.

        Reads the specified JSON file, which should contain a list of dialogue entries.
        Each entry is converted to a DIALOGUE Event with the appropriate character,
        target, and payload.

        Args:
            chapter_file (str): Path to the JSON file containing the chapter data

        Returns:
            list: A list of Event objects representing the chapter's events
        """
        with open(chapter_file, 'r') as f:
            chapter_data = json.load(f)

        events = []
        for entry in chapter_data:
            # Get the character (or create if not exists)
            char_name = entry.get("character")
            char_canonical, _ = resolve_character(char_name)

            if not char_canonical:
                print(f"Warning: Unknown character {char_name}")
                continue

            character = self.characters.get(char_canonical)
            if not character:
                print(f"Warning: Character {char_canonical} not initialized")
                continue

            # Get the target character(s)
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
                type=EventType.DIALOGUE,
                actor=character,
                target=target,
                payload={
                    "text": entry.get("text", ""),
                    "emotion": entry.get("mood", "neutral")
                }
            )

            events.append(event)

        return events

    def run_chapter(self, chapter_file):
        """Run a chapter from a JSON file.

        This method loads a chapter from the specified JSON file, adds all characters
        to the group, and processes each event in the chapter. It displays the initial
        and final state of the group, as well as periodic status updates during the chapter.

        The method performs the following steps:
        1. Load the chapter events using load_chapter()
        2. Add all characters to the group
        3. Display the initial group state
        4. Process each event, applying it to the group
        5. Periodically display group status updates (5% chance after each event)
        6. Display the final group state

        Args:
            chapter_file (str): Path to the JSON file containing the chapter data
        """
        events = self.load_chapter(chapter_file)

        # Add all characters to the group initially
        for character in self.characters.values():
            self.group.add(character)

        print(f"\n=== Starting Chapter: {chapter_file} ===\n")
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

        print(f"\n=== Chapter Complete ===")
        print(
            f"Final group state: {len(self.group.members)} members, mood: {self.group.get_dominant_mood().name}, tension: {self.group.get_tension_description()} ({self.group.tension:.4f})\n")


def parse_chapter_arg(arg):
    """
    Parse the chapter argument to determine if it's a single chapter or a range

    Args:
        arg (str): The chapter argument (e.g., "01", "01-03")

    Returns:
        list: A list of chapter numbers to run
    """
    if "-" in arg:
        # It's a range
        start, end = arg.split("-")
        try:
            start_num = int(start)
            end_num = int(end)
            return [f"{i:02d}" for i in range(start_num, end_num + 1)]
        except ValueError:
            print(f"Invalid chapter range: {arg}")
            return ["01"]  # Default to chapter 01
    else:
        # It's a single chapter
        try:
            # Ensure it's a valid number and format as 2 digits
            chapter_num = int(arg)
            return [f"{chapter_num:02d}"]
        except ValueError:
            # If it's already a full path, return it as is
            if arg.endswith(".json") and "/" in arg:
                return [arg]
            print(f"Invalid chapter number: {arg}")
            return ["01"]  # Default to chapter 01

def run_chapters(game, chapter_numbers):
    """
    Run a sequence of chapters

    Args:
        game (Game): The game instance
        chapter_numbers (list): List of chapter numbers to run
    """
    for i, chapter_num in enumerate(chapter_numbers):
        # Convert chapter number to filename if it's not already a path
        if not chapter_num.endswith(".json"):
            chapter_file = f"play_chapters/chapter-{chapter_num}.json"
        else:
            chapter_file = chapter_num

        # Add a day separator if this isn't the first chapter
        if i > 0:
            print("\n" + "="*50)
            print(f"=== DAY {i+1} ===")
            print("="*50 + "\n")

        # Run the chapter
        game.run_chapter(chapter_file)

def main():
    """
    Main entry point for the game.

    Usage:
        python game.py                # Run chapter 01
        python game.py 01             # Run chapter 01
        python game.py 01-03          # Run chapters 01, 02, and 03 in sequence
        python game.py path/to/file.json  # Run a specific chapter file

    :return: system exit code
    """
    if len(sys.argv) > 1:
        chapter_arg = sys.argv[1]
        chapter_numbers = parse_chapter_arg(chapter_arg)
    else:
        chapter_numbers = ["01"]  # Default to chapter 01

    game = Game()
    run_chapters(game, chapter_numbers)

    exit()



if __name__ == "__main__":
    sys.exit(main())
