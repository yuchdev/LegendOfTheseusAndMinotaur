"""
Group module for the text-based game quest.

This module defines the Group class, which represents a group of characters in the game.
The Group manages the relationships and emotions between characters, tracks the overall
mood and tension of the group, and handles interactions between characters.
"""

from typing import List, Dict, Optional
from character import Character
from emotion import Emotion

class Group:
    """Represents a group of characters in the game.

    A Group manages a collection of characters and their relationships with each other.
    It tracks the emotions characters feel toward each other, calculates the overall
    mood of the group, and maintains a tension level that reflects the state of the
    group's dynamics. The Group also handles interactions between characters, such as
    dialogue, which can affect relationships and tension.
    """
    def __init__(self, members: List[Character] = None):
        """Initialize a new Group instance.

        Creates a new group with the specified members. Initializes the group's mood,
        tension level, and the emotions between all members based on their existing
        relationships (friends/enemies).

        Args:
            members (List[Character], optional): Initial list of characters in the group.
                Defaults to an empty list.
        """
        self.members = members or []
        # general mood is a simple average of individual moods, or more complex
        self.general_mood: Dict[Emotion, float] = {}
        # pairwise emotions: who feels what about whom
        self.emotions: Dict[Character, Dict[Character, Emotion]] = {
            c: {} for c in self.members
        }
        # Group tension level (0.0 to 1.0)
        self.tension: float = 0.0
        # Initialize emotions for all members
        for c1 in self.members:
            for c2 in self.members:
                if c1 != c2:
                    # Initialize with NEUTRAL or based on friend/enemy status
                    if c2 in c1.friends:
                        self.emotions[c1][c2] = Emotion.FRIENDLY
                    elif c2 in c1.enemies:
                        self.emotions[c1][c2] = Emotion.HOSTILE
                    else:
                        self.emotions[c1][c2] = Emotion.NEUTRAL

    def add(self, char: Character):
        """Add a character to the group.

        Adds a character to the group and initializes their emotional relationships
        with all existing members. The initial emotions are based on existing
        friend/enemy relationships between characters.

        If the character is already in the group, this method does nothing.

        Args:
            char (Character): The character to add to the group
        """
        if char in self.members:
            return

        self.members.append(char)
        self.emotions[char] = {}
        for c in self.members:
            if c != char:
                # Initialize emotions based on friend/enemy status
                if c in char.friends:
                    self.emotions[char][c] = Emotion.FRIENDLY
                elif c in char.enemies:
                    self.emotions[char][c] = Emotion.HOSTILE
                else:
                    self.emotions[char][c] = Emotion.NEUTRAL

                if char in c.friends:
                    self.emotions[c][char] = Emotion.FRIENDLY
                elif char in c.enemies:
                    self.emotions[c][char] = Emotion.HOSTILE
                else:
                    self.emotions[c][char] = Emotion.NEUTRAL

    def remove(self, char: Character):
        """Remove a character from the group.

        Removes a character from the group and cleans up all emotional relationships
        involving that character. This includes removing the character's emotions
        toward others and others' emotions toward the character.

        If the character is not in the group, this method does nothing.

        Args:
            char (Character): The character to remove from the group
        """
        if char not in self.members:
            return

        self.members.remove(char)
        if char in self.emotions:
            del self.emotions[char]
        for c in self.members:
            if char in self.emotions[c]:
                del self.emotions[c][char]

    def update_mood(self):
        """Update the general mood of the group.

        Calculates the general mood of the group based on:
        1. The emotions characters feel toward each other
        2. The current emotions of all characters in the group

        The general mood is represented as a dictionary mapping emotions to their
        normalized frequency in the group. This can be used to determine the
        dominant emotion in the group.
        """
        # e.g. tally emotions to set a dominant group mood
        tally: Dict[Emotion, int] = {}
        for p in self.emotions.values():
            for emo in p.values():
                tally[emo] = tally.get(emo, 0) + 1

        # Also include current emotions of characters
        for char in self.members:
            tally[char.current_emotion] = tally.get(char.current_emotion, 0) + 1

        # normalize
        total = sum(tally.values()) if sum(tally.values()) > 0 else 1
        self.general_mood = {e: cnt/total for e, cnt in tally.items()}

    def apply_line(self, speaker: Character, line: str, addressed_to: Optional[Character] = None, emotion: Optional[Emotion] = None):
        """Apply the effects of a character's dialogue line to the group.

        When a character speaks a line, it can affect the group dynamics in several ways:
        1. The speaker's emotion affects the group tension
        2. If addressed to a specific character, it may change that character's feelings toward the speaker
        3. Other characters may react to the speaker's emotion
        4. The overall group mood is updated

        Args:
            speaker (Character): The character speaking the line
            line (str): The content of the dialogue line
            addressed_to (Optional[Character], optional): The character being addressed, if any.
                Defaults to None (speaking to the group in general).
            emotion (Optional[Emotion], optional): The emotion with which the line is spoken.
                Defaults to None (uses the speaker's current emotion).
        """
        if speaker not in self.members:
            return

        # Set the speaker's current emotion
        if emotion:
            speaker.set_emotion(emotion)

        # Update tension based on the emotion
        self.tension += speaker.current_emotion.get_tension_impact()
        self.tension = max(0.0, min(1.0, self.tension))  # Keep tension between 0 and 1

        # If addressed to someone specific
        if addressed_to and addressed_to in self.members:
            # The addressee's opinion of speaker may change based on the emotion
            if speaker.current_emotion.get_category() == "positive":
                self.emotions[addressed_to][speaker] = Emotion.FRIENDLY
            elif speaker.current_emotion.get_category() == "negative":
                self.emotions[addressed_to][speaker] = Emotion.HOSTILE

            # Check if the addressee would be offended
            if addressed_to.is_offended_by(speaker, speaker.current_emotion):
                # Increase tension if someone is offended (slightly less than negative emotions)
                self.tension += 0.015
                self.tension = min(1.0, self.tension)

        # For all members, react to the speaker's emotion
        for member in self.members:
            if member != speaker:
                member.react_to_emotion(speaker, speaker.current_emotion)

        # Recalculate group mood
        self.update_mood()

    def get_dominant_mood(self) -> Emotion:
        """Return the dominant mood of the group.

        The dominant mood is the emotion that occurs most frequently in the group,
        considering both the emotions characters feel toward each other and their
        current individual emotions.

        Returns:
            Emotion: The most prevalent emotion in the group. If the group has no
                emotions (e.g., empty group), returns Emotion.NEUTRAL.
        """
        if not self.general_mood:
            return Emotion.NEUTRAL

        return max(self.general_mood.items(), key=lambda x: x[1])[0]

    def get_tension_description(self) -> str:
        """Return a human-readable description of the current tension level.

        Converts the numerical tension value (0.0 to 1.0) to a descriptive string
        that represents the current state of tension in the group.

        The tension levels are:
        - 0.00 to 0.02: "relaxed"
        - 0.02 to 0.04: "slightly tense"
        - 0.04 to 0.06: "moderately tense"
        - 0.06 to 0.08: "very tense"
        - 0.08 to 1.00: "extremely tense"

        Returns:
            str: A description of the current tension level
        """
        if self.tension < 0.02:
            return "relaxed"
        elif self.tension < 0.04:
            return "slightly tense"
        elif self.tension < 0.06:
            return "moderately tense"
        elif self.tension < 0.08:
            return "very tense"
        else:
            return "extremely tense"
