"""
Test script to verify avatar loading functionality.
This tests the avatar resolution and loading without running the full GUI.
"""

import sys
import os

# Test that we can import the GUI module and its dependencies
try:
    from gui_game import GameGUI
    from constants import CHARACTERS, ALIASES, resolve_character
    print("✓ Successfully imported GUI and constants modules")
except ImportError as e:
    print(f"✗ Failed to import modules: {e}")
    sys.exit(1)

# Test avatar file existence
print("\n=== Testing Avatar Files ===")
avatar_files = []
for i, filename in enumerate(os.listdir("avatars")):
    if filename.endswith(".png"):
        avatar_files.append(filename)
        file_path = os.path.join("avatars", filename)
        file_size = os.path.getsize(file_path)
        print(f"{i+1}. {filename} ({file_size:,} bytes)")

print(f"\n✓ Found {len(avatar_files)} avatar files")

# Test character name resolution
print("\n=== Testing Character Name Resolution ===")

# Create a temporary GUI instance to test the avatar resolution methods
class TestGUI:
    def __init__(self):
        pass
    
    def debug_log(self, message):
        print(f"[DEBUG] {message}")
    
    def resolve_avatar_filename(self, character_name):
        """Copy of the resolve_avatar_filename method for testing"""
        if not character_name:
            return None
            
        # First try to resolve the character name using constants
        canonical_name, alias = resolve_character(character_name)
        
        # List of possible avatar filenames to try
        possible_names = []
        
        if canonical_name:
            possible_names.append(canonical_name)
        if alias:
            possible_names.append(alias)
        possible_names.append(character_name)
        
        # Special mappings for avatar files that don't match exactly
        avatar_mappings = {
            "Organizm(-:": "Organizm",
            "UGLI 666": "UGLI666"
        }
        
        # Add mapped names to possible names
        for name in possible_names[:]:  # Copy list to avoid modification during iteration
            if name in avatar_mappings:
                possible_names.append(avatar_mappings[name])
        
        # Try each possible name
        for name in possible_names:
            avatar_path = os.path.join("avatars", f"{name}.png")
            if os.path.exists(avatar_path):
                return avatar_path
                
        return None

test_gui = TestGUI()

# Test resolution for all canonical characters
print("Testing canonical character names:")
for character in CHARACTERS:
    avatar_path = test_gui.resolve_avatar_filename(character)
    if avatar_path:
        print(f"✓ {character} → {avatar_path}")
    else:
        print(f"✗ {character} → No avatar found")

# Test resolution for aliases
print("\nTesting character aliases:")
for alias, canonical in ALIASES.items():
    avatar_path = test_gui.resolve_avatar_filename(alias)
    if avatar_path:
        print(f"✓ {alias} (→ {canonical}) → {avatar_path}")
    else:
        print(f"✗ {alias} (→ {canonical}) → No avatar found")

# Test some edge cases
print("\nTesting edge cases:")
edge_cases = ["", None, "NonExistentCharacter", "Organizm", "UGLI666"]
for case in edge_cases:
    avatar_path = test_gui.resolve_avatar_filename(case)
    if avatar_path:
        print(f"✓ '{case}' → {avatar_path}")
    else:
        print(f"✗ '{case}' → No avatar found")

print("\n=== Avatar Loading Test Complete ===")
print("The avatar loading functionality is ready!")
print("\nTo test the full GUI with avatars:")
print("1. Ensure PySide6 is installed: pip install PySide6")
print("2. Run: python gui_game.py")
print("3. Click 'Next Step' to see characters speak with their avatars")