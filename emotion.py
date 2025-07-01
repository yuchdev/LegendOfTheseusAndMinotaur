"""
Emotion module for the text-based game quest.

This module defines the Emotion enum class, which represents different emotions that
characters can experience in the game. It provides methods for converting between
string representations and enum values, categorizing emotions, and determining their
impact on group tension.
"""

from enum import Enum, auto

class Emotion(Enum):
    """Enumeration of emotions that characters can experience in the game.

    Emotions are categorized into positive, neutral, negative, and complex types.
    Each emotion has different effects on character relationships and group dynamics.
    """
    # Positive emotions
    COMPASSIONATE = auto()
    EXCITED = auto()
    FLIRTY = auto()
    HOPEFUL = auto()
    HUMOROUS = auto()
    PROUD = auto()
    RESPECTFUL = auto()
    SOLEMN = auto()

    # Neutral emotions
    CALM = auto()
    CONFUSED = auto()
    CONTEMPLATIVE = auto()
    CURIOUS = auto()
    SURPRISED = auto()
    RESIGNED = auto()

    # Negative emotions
    ANGRY = auto()
    ANXIOUS = auto()
    DOWN = auto()
    EMBARRASSED = auto()
    FEARFUL = auto()
    IRRITATED = auto()

    # Complex emotions
    DEFENSIVE = auto()
    DESPERATE = auto()
    DISMISSIVE = auto()
    JEALOUS = auto()
    SARCASTIC = auto()
    SKEPTICAL = auto()

    # General categories
    FRIENDLY = auto()
    NEUTRAL = auto()
    HOSTILE = auto()
    ADMIRATION = auto()
    FEAR = auto()

    @classmethod
    def from_string(cls, emotion_str: str) -> 'Emotion':
        """Convert a string emotion to an Emotion enum value.

        This method takes a string representation of an emotion and converts it to
        the corresponding Emotion enum value. The conversion is case-insensitive.
        If the string does not match any known emotion, NEUTRAL is returned as a default.

        Args:
            emotion_str (str): The string representation of the emotion

        Returns:
            Emotion: The corresponding Emotion enum value, or NEUTRAL if not found
        """
        emotion_map = {
            # Positive emotions
            "compassionate": cls.COMPASSIONATE,
            "excited": cls.EXCITED,
            "flirty": cls.FLIRTY,
            "hopeful": cls.HOPEFUL,
            "humorous": cls.HUMOROUS,
            "proud": cls.PROUD,
            "respectful": cls.RESPECTFUL,
            "solemn": cls.SOLEMN,

            # Neutral emotions
            "calm": cls.CALM,
            "confused": cls.CONFUSED,
            "contemplative": cls.CONTEMPLATIVE,
            "curious": cls.CURIOUS,
            "surprised": cls.SURPRISED,
            "resigned": cls.RESIGNED,

            # Negative emotions
            "angry": cls.ANGRY,
            "anxious": cls.ANXIOUS,
            "down": cls.DOWN,
            "embarrassed": cls.EMBARRASSED,
            "fearful": cls.FEARFUL,
            "irritated": cls.IRRITATED,

            # Complex emotions
            "defensive": cls.DEFENSIVE,
            "desperate": cls.DESPERATE,
            "dismissive": cls.DISMISSIVE,
            "jealous": cls.JEALOUS,
            "sarcastic": cls.SARCASTIC,
            "skeptical": cls.SKEPTICAL,

            # General categories
            "friendly": cls.FRIENDLY,
            "neutral": cls.NEUTRAL,
            "hostile": cls.HOSTILE,
            "admiration": cls.ADMIRATION,
            "fear": cls.FEAR,
        }

        return emotion_map.get(emotion_str.lower(), cls.NEUTRAL)

    def get_category(self) -> str:
        """Return the category of the emotion.

        This method determines which category an emotion belongs to:
        - positive: Emotions that generally have a positive effect on relationships
        - neutral: Emotions that have minimal impact on relationships
        - negative: Emotions that generally have a negative effect on relationships
        - complex: Emotions that have mixed or context-dependent effects
        - unknown: If the emotion doesn't fit into any of the above categories

        Returns:
            str: The category of the emotion as a string ('positive', 'neutral', 'negative', 'complex', or 'unknown')
        """
        positive = {Emotion.COMPASSIONATE, Emotion.EXCITED, Emotion.FLIRTY, 
                   Emotion.HOPEFUL, Emotion.HUMOROUS, Emotion.PROUD, 
                   Emotion.RESPECTFUL, Emotion.SOLEMN, Emotion.FRIENDLY, 
                   Emotion.ADMIRATION}

        neutral = {Emotion.CALM, Emotion.CONFUSED, Emotion.CONTEMPLATIVE, 
                  Emotion.CURIOUS, Emotion.SURPRISED, Emotion.RESIGNED, 
                  Emotion.NEUTRAL}

        negative = {Emotion.ANGRY, Emotion.ANXIOUS, Emotion.DOWN, 
                   Emotion.EMBARRASSED, Emotion.FEARFUL, Emotion.IRRITATED, 
                   Emotion.HOSTILE, Emotion.FEAR}

        complex = {Emotion.DEFENSIVE, Emotion.DESPERATE, Emotion.DISMISSIVE, 
                  Emotion.JEALOUS, Emotion.SARCASTIC, Emotion.SKEPTICAL}

        if self in positive:
            return "positive"
        elif self in neutral:
            return "neutral"
        elif self in negative:
            return "negative"
        elif self in complex:
            return "complex"
        else:
            return "unknown"

    def get_tension_impact(self) -> float:
        """Return the impact on group tension for this emotion.

        This method calculates how much an emotion affects the tension level in a group.
        Different categories of emotions have different impacts:
        - positive emotions: Significantly reduce tension (-0.03)
        - neutral emotions: Have no effect on tension (0.0)
        - negative emotions: Increase tension (0.02)
        - complex emotions: Slightly increase tension (0.01)

        The values are designed so that positive emotions decrease tension more effectively
        than negative emotions increase it, creating a balanced group dynamic.

        Returns:
            float: The tension impact value (negative values reduce tension, positive values increase it)
        """
        category = self.get_category()
        if category == "positive":
            return -0.03   # Reduces tension (significantly stronger than negative increases it)
        elif category == "neutral":
            return 0.0     # No effect on tension
        elif category == "negative":
            return 0.02    # Increases tension
        elif category == "complex":
            return 0.01    # Slightly increases tension
        return 0.0
