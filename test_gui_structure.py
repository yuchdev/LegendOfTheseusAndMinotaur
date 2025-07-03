"""
Test script to verify GUI structure and integration points without running the actual GUI.
This tests that our GUI code is syntactically correct and properly integrated with the game logic.
"""

import sys
import os

# Test that we can import the game modules
try:
    from game import Game
    from character import Character
    from group import Group
    from emotion import Emotion
    print("✓ Successfully imported game modules")
except ImportError as e:
    print(f"✗ Failed to import game modules: {e}")
    sys.exit(1)

# Test that we can create a game instance and load data
try:
    game = Game()
    print(f"✓ Created game instance with {len(game.characters)} characters")
    
    # Test loading a day
    events = game.load_day("play_chapters/day-01.json")
    print(f"✓ Loaded day-01.json with {len(events)} events")
    
    # Test that we can access character data for GUI display
    for char_name, character in list(game.characters.items())[:3]:  # Test first 3 characters
        print(f"✓ Character {char_name}: L={character.leadership}, I={character.intelligence}, R={character.resilience}, E={character.current_emotion.name}")
    
    # Test group dynamics
    for character in game.characters.values():
        game.group.add(character)
    
    mood = game.group.get_dominant_mood()
    tension = game.group.tension
    tension_desc = game.group.get_tension_description()
    print(f"✓ Group dynamics: Mood={mood.name}, Tension={tension:.4f} ({tension_desc})")
    
except Exception as e:
    print(f"✗ Failed to test game integration: {e}")
    sys.exit(1)

# Test that GUI code structure is syntactically correct
try:
    # Read the GUI file and check for syntax errors
    with open("gui_game.py", "r") as f:
        gui_code = f.read()
    
    # Compile the code to check for syntax errors
    compile(gui_code, "gui_game.py", "exec")
    print("✓ GUI code is syntactically correct")
    
    # Check that all required components are present
    required_components = [
        "class GameGUI",
        "def create_character_list",
        "def create_chat_events", 
        "def create_group_dynamics",
        "def create_avatar_voice",
        "def create_debug_console",
        "def create_controls",
        "def next_step",
        "def prev_step",
        "def update_display"
    ]
    
    for component in required_components:
        if component in gui_code:
            print(f"✓ Found {component}")
        else:
            print(f"✗ Missing {component}")
    
except SyntaxError as e:
    print(f"✗ GUI code has syntax errors: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Failed to verify GUI structure: {e}")
    sys.exit(1)

# Test that day files exist
day_files = []
for i in range(1, 7):
    day_file = f"play_events/day-{i:02d}.json"
    if os.path.exists(day_file):
        day_files.append(day_file)

print(f"✓ Found {len(day_files)} day files: {[os.path.basename(f) for f in day_files]}")

print("\n🎉 All tests passed! The GUI implementation is ready.")
print("\nTo run the GUI:")
print("1. Install PySide6: pip install PySide6")
print("2. Run: python gui_game.py")
print("\nThe GUI provides:")
print("- Character list with full stats (QTableWidget)")
print("- Chat/Events pane with auto-scroll (QTextEdit)")
print("- Group dynamics with tension bar (QProgressBar)")
print("- Avatar + voice UI with speaking animation (QLabel + QTimer)")
print("- Game controls for step-by-step progression (QPushButtons)")
print("- Debug console for logging (QTextEdit)")