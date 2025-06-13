# Legend

Continue the task. 

Process the complete following JSON fragment which is the 5th chapter of a play "The Legend of Theseus and Minotaur"

Use these characters list and moods dict for I reminded the task below.

```
# Canonical characters
CHARACTERS = {
    "Monstradamus", "IsoldA", "Nutscracker", "Organizm(-:",
    "Theseus", "Ariadne", "UGLI 666", "Romeo-y-Cohiba", "Sartrik"
}

# Aliases
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

MOODS = {
    "positive": [
        "calm",
        "caring",
        "joyful",
        "hopeful",
        "loving",
        "proud"
    ],
    "neutral": [
        "confused",
        "curious",
        "indifferent",
        "contemplative",
        "resigned"
    ],
    "negative": [
        "angry",
        "anxious",
        "fearful",
        "sad",
        "ashamed"
    ],
    "complex": [
        "sarcastic",
        "skeptical",
        "surprised",
        "playful",
        "jealous",
        "manipulative",
        "desperate"
    ]
}
```
Continue the task. 

Process the complete following JSON fragment in JSON format where "character" of character's name and "text" of character's line are filled out, but "to" and "mood" are not.

Note that "to" can be another character's name, list of characters, if explicitly addressed to more than one, or empty string if the line is not addressed anyone particularly.

From the context of the play's action, fill out these fields ("to" from characters list, "mood" from the list you just offered. 
If the line is not addressing particularly anyone, keep it empty string. 

List of characters and their aliases are below, so as imprecise mood list. If there are not enough definitions of moods to express the line, feel free add more.

Return JSON with a single completed result.

```

```
