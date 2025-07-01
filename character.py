"""
Character module for the text-based game quest.

This module defines the Character class, which represents characters in the game world.
Characters have attributes like leadership, intelligence, and resilience, as well as
relationships with other characters. They can experience emotions and react to the
emotions of others.
"""

from typing import List, Callable, Union
import random
from emotion import Emotion

class Character:
    """Represents a character in the game world.

    Characters are the main entities in the game. They have attributes that define their
    personality and capabilities, relationships with other characters, and can experience
    and react to emotions. Characters can interact with each other and influence the
    group dynamics.
    """
    def __init__(
        self,
        name: str,
        leadership: int = 50,
        intelligence: int = 50,
        resilience: int = 50,
        friends: List["Character"] = None,
        enemies: List["Character"] = None,
        special_properties: List[Callable[["Character", "Character"], bool]] = None
    ):
        """Initialize a new Character instance.

        Args:
            name (str): The character's name
            leadership (int, optional): Leadership attribute (0-100). Defaults to 50.
            intelligence (int, optional): Intelligence attribute (0-100). Defaults to 50.
            resilience (int, optional): Resilience attribute (0-100). Defaults to 50.
            friends (List[Character], optional): Initial list of friends. Defaults to empty list.
            enemies (List[Character], optional): Initial list of enemies. Defaults to empty list.
            special_properties (List[Callable], optional): Special behavior predicates. 
                Each callable takes (self, other) and returns a boolean.
                Defaults to empty list.
        """
        self.name = name
        self.leadership = leadership
        self.intelligence = intelligence
        self.resilience = resilience
        self.friends = friends or []
        self.enemies = enemies or []
        # each property is a predicate (self, other) → bool
        self.special_properties = special_properties or []
        self.current_emotion = Emotion.NEUTRAL

    def can_talk_to(self, other: "Character") -> bool:
        """Determine if this character can talk to another character.

        This method checks if the character can talk to another character based on
        their special properties. By default, all characters can talk to each other,
        but special properties can restrict this ability.

        Args:
            other (Character): The character to potentially talk to

        Returns:
            bool: True if this character can talk to the other character, False otherwise
        """
        # default: everyone can talk
        for prop in self.special_properties:
            if not prop(self, other):
                return False
        return True

    def set_emotion(self, emotion: Union[str, Emotion]) -> None:
        """Set the character's current emotion.

        This method updates the character's current emotional state, which affects
        how they interact with other characters and influences group dynamics.

        Args:
            emotion (Union[str, Emotion]): The emotion to set. Can be either a string
                (which will be converted to an Emotion enum value) or an Emotion enum value.
        """
        if isinstance(emotion, str):
            self.current_emotion = Emotion.from_string(emotion)
        else:
            self.current_emotion = emotion

    def react_to_emotion(self, other: "Character", emotion: Emotion) -> None:
        """React to another character's emotion.

        This method updates the character's relationship with another character based on
        the emotion displayed by that character. Positive emotions can improve relationships
        (turning enemies into friends), while negative emotions can worsen relationships
        (turning friends into enemies).

        Args:
            other (Character): The character displaying the emotion
            emotion (Emotion): The emotion being displayed
        """
        # If the other character is showing a positive emotion, improve relationship
        if emotion.get_category() == "positive" and other in self.enemies:
            self.enemies.remove(other)
            if other not in self.friends:
                self.friends.append(other)

        # If the other character is showing a negative emotion, worsen relationship
        elif emotion.get_category() == "negative" and other in self.friends:
            self.friends.remove(other)
            if other not in self.enemies:
                self.enemies.append(other)

    def is_offended_by(self, other: "Character", emotion: Emotion) -> bool:
        """Determine if this character would be offended by another's emotion.

        This method calculates whether a character would take offense at an emotion
        displayed by another character. The likelihood depends on several factors:
        - The character's resilience attribute
        - The relationship between the characters (friends or enemies)
        - The type and intensity of the emotion

        Characters with high resilience are less likely to be offended. Characters are
        more likely to be offended by negative emotions from enemies, and even friends
        can cause offense with very negative emotions like anger.

        Args:
            other (Character): The character displaying the emotion
            emotion (Emotion): The emotion being displayed

        Returns:
            bool: True if this character is offended, False otherwise
        """
        # Characters with high resilience are less likely to be offended
        if self.resilience > 70:
            return False

        # Characters are more likely to be offended by negative emotions from enemies
        if other in self.enemies and emotion.get_category() in ["negative", "complex"]:
            return random.random() < 0.7

        # Even friends can offend with very negative emotions
        if other in self.friends and emotion == Emotion.ANGRY:
            return random.random() < 0.3

        # General chance of being offended by negative emotions
        if emotion.get_category() == "negative":
            return random.random() < 0.5

        return False

    def __repr__(self):
        """Return a string representation of the character.

        Returns:
            str: A string representation in the format "<Char name>"
        """
        return f"<Char {self.name}>"

    def __eq__(self, other):
        """Compare this character to another object for equality.

        Characters are considered equal if they have the same name.

        Args:
            other: The object to compare with

        Returns:
            bool: True if the objects are equal, False otherwise
        """
        if isinstance(other, Character):
            return self.name == other.name
        return False

    def __hash__(self):
        """Return a hash value for the character.

        The hash is based on the character's name, which allows characters
        to be used as dictionary keys or in sets.

        Returns:
            int: A hash value for the character
        """
        return hash(self.name)
