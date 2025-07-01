"""
Constants module for the text-based game quest.

This module contains constants used throughout the game, including character names,
aliases, and emotion categories. It also provides utility functions for character name resolution.
"""

# Canonical characters
"""List of canonical character names used in the game.

These are the official names of characters that appear in the game world.
All character references should ultimately resolve to one of these names.
"""
CHARACTERS = [
    "Monstradamus", 
    "IsoldA", 
    "Nutscracker", 
    "Organizm(-:",
    "Theseus", 
    "Ariadne", 
    "UGLI 666", 
    "Romeo-y-Cohiba", 
    "Sartrik"
]

# Aliases
"""Dictionary mapping alternative character names to their canonical names.

Characters may be referred to by different names or spellings in the game text.
This dictionary helps resolve these alternative names to their canonical forms.
"""
ALIASES = {
    "Nut$cracker": "Nutscracker",
    "UGLI666": "UGLI 666",
    "Isolda": "IsoldA",
    "Romeo": "Romeo-y-Cohiba",
    "Organizm)-": "Organizm(-:",
    "Organizm(-": "Organizm(-:",
    "Organizm)-:": "Organizm(-:",
    "TheZeus": "Theseus"
}

"""Dictionary categorizing emotions into different types.

Emotions are categorized into four types:
- positive: Emotions that generally have a positive effect on relationships and reduce tension
- neutral: Emotions that have minimal impact on relationships and tension
- negative: Emotions that generally have a negative effect on relationships and increase tension
- complex: Emotions that have mixed or context-dependent effects

These categories are used to determine how emotions affect character relationships and group dynamics.
"""
EMOTIONS = {
    "positive": [
        "compassionate",
        "excited",
        "flirty",
        "hopeful",
        "humorous",
        "proud",
        "respectful",
        "solemn"
    ],
    "neutral": [
        "calm",
        "confused",
        "contemplative",
        "curious",
        "surprised",
        "resigned"
    ],
    "negative": [
        "angry",
        "anxious",
        "down",
        "embarrassed",
        "fearful",
        "irritated"
    ],
    "complex": [
        "defensive",
        "desperate",
        "dismissive",
        "jealous",
        "sarcastic",
        "skeptical"
    ]
}

def resolve_character(name):
    """Resolve a character name to its canonical form.

    This function takes a character name and attempts to resolve it to its canonical form.
    If the name is already canonical, it returns the name as is. If the name is an alias,
    it returns the canonical name and the original alias. If the name is unknown, it returns
    None for both values.

    Args:
        name (str): The character name to resolve

    Returns:
        tuple: A tuple containing (canonical_name, alias) where:
            - canonical_name (str or None): The canonical name if found, None otherwise
            - alias (str or None): The original alias if an alias was used, None otherwise
    """
    if name in CHARACTERS:
        return name, None
    elif name in ALIASES:
        return ALIASES[name], name
    return None, None
