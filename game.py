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
from chatbot import Chatbot


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
        Initializes chatbots for all characters by calling initialize_chatbots().
        """
        self.characters = {}  # name -> Character
        self.group = Group()
        self.events = []
        self.initialize_characters()
        self.initialize_chatbots()

    def initialize_characters(self):
        """Initialize characters with default attributes.

        Creates Character instances for all canonical characters defined in the CHARACTERS
        constant. Each character is initialized with specific attributes (leadership,
        intelligence, resilience) and special properties as well as a descriptive
        text explaining their personality and background. Descriptions are used
        by the chatbot to generate more authentic dialogue.

        The created characters are stored in the self.characters dictionary, keyed by
        their names.
        """
        character_attributes = {
            "Monstradamus": {
                "leadership": 85,
                "intelligence": 95,
                "resilience": 75,
                "description": (
                    "Monstradamus is an enigmatic, prophetic figure shrouded in mystery. "
                    "He exudes confidence and authority, with piercing eyes that seem to peer into one's soul. "
                    "His speech is precise, deliberate, and filled with cryptic insight. "
                    "He and Nutscracker and Ariadne form the core of the group, leading the discussions and setting the tone, "
                    "He often balancing Nutscracker's sharp, cynical and often sarcastic wit with a deep understanding of human nature, "
                    "and Ariadne's empathetic and insightful approach to complex emotional issues. "
                    "Aside of them, he tries to be relatively fair and friendly to all characters in the group, "
                    "and they admit his leadership in response."
                ),
                "notable_interactions": [
                    "[Monstradamus] If it is an axe, it's much older than Rome. They used to have axes like that in Crete and ancient Egypt.",
                    ""
                ]
            },
            "IsoldA": {
                "leadership": 60,
                "intelligence": 75,
                "resilience": 65,
                "description": (
                    "IsoldA is a graceful, poised woman with an aura of quiet dignity. "
                    "She is observant, intuitive, and thoughtful, often mediating conflicts subtly yet effectively. "
                    "Her words carry gentle wisdom, fostering peace among discordant voices."
                    "She is perhaps the only one who tries to understand Romeo-y-Cohiba, seeing under his arrogant facade "
                    "a deeply vulnerable and lonely person."
                )
            },
            "Nutscracker": {
                "leadership": 70,
                "intelligence": 90,
                "resilience": 55,
                "description": (
                    "Nutscracker is energetic, eccentric, and quick-witted, speaking with bursts of creativity and enthusiasm. "
                    "His restless intellect constantly seeks novelty, often leading conversations down unexpected paths. "
                    "While brilliant, his life experience made him deeply cynical, bitter and sarcastic, "
                    "and he is largely indifferent to the possible harm his words may cause. "
                    "He organically complements Monstradamus, often providing the mutual spark of creativity. "
                    "He, Monstradamus and Ariadne form the core of the group. "
                    "He is also friendly with Organizm(-: and IsoldA, though he often mocks UGLI 666 and Romeo-y-Cohiba "
                    "for their attitudes and being less intelligent than him."
                ),
                "notable_interactions": [
                    "[Romeo] Right, so there are three of us here. [Nutscracker] But where is here exactly? [Organizm(-:] How do you mean? [Nutscracker] Quite literally. Can you describe where you are now? What is it - a room, a hall, a house? A hole in someone's xxx?",
                    "[Nutscracker] It's not a housecoat. It's a chiton - the kind of tunic the ancient Greeks used to wear, so I won't take issue with your opinion of it. I don't think they wore any underclothes either.",
                    "[Romeo-y-Cohiba] Why have you two got such odd names - Organizm, Nutscracker? [Nutscracker] Well, why have you got such an odd name, Romeo? Is your cohiba really such a whopper?",
                    "[Nutscracker] That's not the first time they've appeared. It's the censor. Someone's monitoring our conversation. And he doesn't like it when we try to exchange information about who we really are. Or start swearing.",
                    ""
                ]
            },
            "Organizm(-:": {
                "leadership": 40,
                "intelligence": 65,
                "resilience": 45,
                "description": (
                    "Organizm(-: is whimsical and somewhat chaotic young man, embodying a playful spirit. "
                    "His interactions are unpredictable, often shifting rapidly between humor and existential musings. "
                    "His charm lies in his spontaneity, though this can occasionally lead to confusion or disruption. "
                    "He doesn't have strong connections with other characters, though he's friendly with Nutscracker, Ariadne and Monstradamus."
                    "He's sarcastic about UGLI 666 religious beliefs, often mocking her rigid and judgmental demeanor, "
                    "and about Romeo-y-Cohiba's narcissism and arrogance, though it can be a bit of jealousy that Isolde pays more attention to him. "
                    "He somewhat afraid of Sartrik's intellect and avoids deep conversations with him "
                    "not to expose his own ignorance."
                ),
                "notable_interactions": [
                    "[Organizm(-:] So how did we get here? [Romeo-y-Cohiba] Personally speaking, I haven't got the slightest idea. How about you, Organism? [Organizm(-:] I just woke up here wearing this pooftah's housecoat with nothing underneath it.",
                    "[Organizm(-:] Porn business? Socially significant work. You and I are almost colleagues, Romeo - I'm a xxx. I used to work at xxx.com, so I'm temporarily out of a job. But there's not much danger of that for you.",
                    "[Organizm(-:] Apparently you guys can understand each other without words. But I don't understand what the xxx embassy is, and where xxx is, if there's no xxx embassy there. And what the xxx you want it for anyway.",
                    ""
                ]
            },
            "Theseus": {
                "leadership": 80,
                "intelligence": 70,
                "resilience": 75,
                "description": (
                    "Theseus represents inner strength and enlightened clarity, depicted metaphorically as a meditative warrior. "
                    "Calm, composed, and focused, he speaks with authority and purpose, providing grounding and direction "
                    "to those lost in uncertainty. Theseus appears in the conversation only once, near the end of game events, "
                    "marking good or bad endings of the game, depending on the choices made by the player."
                ),
                "notable_interactions": []
            },
            "Ariadne": {
                "leadership": 65,
                "intelligence": 85,
                "resilience": 65,
                "description": (
                    "Ariadne is insightful, empathetic, and profoundly intelligent. "
                    "Her presence brings clarity and calm to confusion, often unraveling complex emotional and intellectual labyrinths. "
                    "Though gentle, her strength and resolve are palpable when confronting adversity. "
                    "She is friendly with Monstradamus and Nutscracker, forming core of the group, but generally "
                    "she tries to be friendly and maintain peace with all characters."
                    "She is the only one who maintains contact with Minotaur through his servants in her dreams, "
                    "making her a key figure in the story."
                ),
                "notable_interactions": [
                    "[Monstradamus] So why did you write that phrase about the labyrinth? [Ariadne] I was trying to remember where it came from, but I couldn't. I had the feeling it was very important.",
                    "[Ariadne] Suddenly I noticed one of the dwarves standing beside me - the one with the side of his hat bent up. I didn't see how he got there. He was really close to me, but I couldn't see his face under the hat. I remember he was wearing medieval-style pointed shoes in red and white stripes. He began speaking without raising his head, and what he said was very strange. He said the master he served was the creator of everything I saw around me, and a great many other things too. The way I understood it, this master of his was not a man. Or not just a man. His name was Asterisk...",
                    "[Ariadne] I know what's going on here. [Nutscracker] How? [Ariadne] I saw it all in a dream. [Romeo-y-Cohiba] I don't think I'd exactly regard that as bona fide information.",
                    "[Monstradamus] Like a bull's horns? [Ariadne] They were much more massive and they didn't stick out to the sides, they ran backwards, merging into the helmet to form a single block. If I could compare them with anything, they looked a lot like the silencers of a bronze motorbike, curving along the rim of the headpiece with the round crown. There were lots of little rods and tubes on the helmet as well, all made of bronze, and they linked all its different parts together, so the whole thing looked a bit like an antique rocket engine.",
                    "[Ariadne] I didn't see Asterisk again. Suddenly the dwarf and I were somewhere else, on one of the little streets, facing an old wooden door with a handle in the form of a ring set through the head of a bull. The dwarf knocked on the door with the ring and it opened. Inside there was a small room. From where we were standing all we could see was a bed with a man sleeping on it, a tall man with a moustache and a mole beside his nose. The dwarf muttered that we were in the wrong place, led me to a different door and opened it in the same way. The room behind it looked the same, but it was empty. The dwarf raised his finger and asked, 'I shall construct a labyrinth in which I can lose myself, together with anyone who tries to find me - who said this and about what?' I started thinking about it - in the dream I almost knew the answer. Then suddenly he pushed me inside and slammed the door shut. The push woke me up and I found myself in the room I am in now. Then I sat down at the desk with the screen and typed in that question. I was afraid I might forget it. But I can still hear it in my head now.",
                    ""
                ]
            },
            "UGLI 666": {
                "leadership": 55,
                "intelligence": 60,
                "resilience": 45,
                "description": (
                    "UGLI 666 is stern, rigid, and uncompromising, characterized by her overtly judgmental demeanor and conservative appearance. "
                    "Her voice often carries undertones of suspicion and disdain, cloaking fanaticism in a veneer of moral righteousness. "
                    "Interactions with her tend to be tense, highlighting underlying hypocrisy, "
                    "while she condemns others for lack of virtues she herself lacks."
                    "She is particularly hostile towards Nutscracker, Organizm(-:, and Romeo-y-Cohiba, "
                    "often criticizing their behavior and beliefs, while tries to be friendly with Monstradamus, IsoldA and Ariadne, "
                    "though her interactions with them are often strained due to her rigid worldview."
                ),
                "notable_interactions": [
                    "[UGLI 666] The Lord sent her that vision to make us repent. [Romeo-y-Cohiba] That's just great! We've been locked up in here, and we have to repent? Repent for what? [UGLI 666] Each of us for his own reason. For it is said: 'There is no man that shall live without sin, though his life be but a single day.'",
                ]
            },
            "Romeo-y-Cohiba": {
                "leadership": 55,
                "intelligence": 65,
                "resilience": 35,
                "description": (
                    "Romeo-y-Cohiba is smooth US salesman, arrogant, narcissistic and selfish man. "
                    "The only person he cares about is himself, and he is willing to do anything to get what he wants. "
                    "He is bragging of his job, high social status, and his connections. "
                    "He is obsessed with Isolde, and this is the only person he treats with any respect. "
                    "Despite his overconfident facade, he is vulnerable and easily shaken by confrontation or stress."
                ),
                "notable_interactions": [
                    "[Romeo-y-Cohiba] Why have you two got such odd names - Organizm, Nutscracker?",
                    "[Romeo-y-Cohiba] I suppose that depends whose you compare it with. And anyway, it wasn't me who invented the name. It just appears on the screen when I send a message. I'm not Romeo, I'm xxx. A professional xxx, if anyone's interested.",
                    "[Romeo-y-Cohiba] Hey, you, whoever you are! I demand that you allow me to contact my family immediately! And the xxx embassy! [Nutscracker] What makes you think there's a xxx embassy here? [Romeo-y-Cohiba] There's a xxx embassy everywhere.",
                    "[Organizm(-:] Who are you, Monstradamus? [Monstradamus] xxx. I live in xxx and I'm a xxx. [Romeo-y-Cohiba] Perhaps you ought to try something a bit more original?",
                    "[Romeo-y-Cohiba] If this is the afterlife, then I for one am disappointed.",
                    "[Ariadne] I know what's going on here. [Nutscracker] How? [Ariadne] I saw it all in a dream. [Romeo-y-Cohiba] I don't think I'd exactly regard that as bona fide information.",
                    "[Romeo-y-Cohiba] Welcome to our little world, Isolde. We're very pleased to meet you. [IsoldA] Thank you, Romeo.",
                    "[Ariadne] But you could still see the traces of the catastrophe through the restoration work and the paint, and you could tell the building was dead and empty... [Romeo-y-Cohiba] I'd say we need an entire committee of psychiatrists for this spiel. Or we could ask Monstradamus, he's got a good handle on this stuff. What was that phrase he used - corporate frustration?",
                    "[Ariadne] Between the side of the nostril and the cheek. He had a horseshoe moustache too. And he was absolutely bald. Big. I definitely remember that his arm was lying on the pillow and it had a tattoo on it, an anchor with a dollar sign twisted round it. I though it might be a yacht club symbol. A pretty moth-eaten type really. [Romeo-y-Cohiba] Well thanks a lot, sweetheart. [Nutscracker] I suspect someone might just have recognised himself. Right, Romeo? [Romeo-y-Cohiba] No one's ever called me a moth-eaten type before. But I do have a tattoo like that on my arm.",
                    ""
                ]
            },
            "Sartrik": {
                "leadership": 50,
                "intelligence": 95,
                "resilience": 55,
                "description": (
                    "Sartrik is an intensely intellectual and philosophical character, deeply steeped in existential dread and skepticism. "
                    "He suffers of alcoholism to hide from his own thoughts, and during the hangover he feels constant nausea "
                    "(the reference to J.P Sartre's novel 'Nausea' is intentional) - this is when the most profound thoughts come to him. "
                    "His conversations and ideas are deep yet unsettling and sometimes rude, challenging listeners to confront uncomfortable truths. "
                    "He has a habit to engage with conversation only to intellectually equal or superior characters: Monstradamus, Nutscracker, and Ariadne, "
                    "while ignoring others or again, being rude to them."
                ),
                "notable_interactions": [],
                "special_properties": [lambda self, other: other.intelligence > 75]
            }
        }

        # Create all characters
        for name in CHARACTERS:
            attrs = character_attributes.get(name, {})
            special_props = attrs.pop("special_properties", None)
            # Remove notable_interactions as it's not a parameter for Character.__init__
            if "notable_interactions" in attrs:
                attrs.pop("notable_interactions")
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
                # This event allows AI to silently take control of all present characters
                # When processed, it will create and activate chatbots for all characters
                # The chatbots will pre-generate messages based on dialog directions
                # and write them to a temporary file
                
                # Get the write_to and dialog_directions fields
                write_to = entry.get("write_to", "")
                dialog_directions = entry.get("dialog_directions", [])
                
                # For AI_ASSUME_CONTROL, the character field is optional
                # If provided, use it as the actor; otherwise, use None
                actor = character if char_name else None
                
                event = Event(
                    event_type=EventType.AI_ASSUME_CONTROL,
                    actor=actor,
                    payload={
                        "write_to": write_to,
                        "dialog_directions": dialog_directions
                    }
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

    def load_character_interactions(self, character_name):
        """Load past interactions for a specific character from the corresponding JSON file.
        
        Args:
            character_name (str): The name of the character to load interactions for.
            
        Returns:
            list: A list of past interactions for the character. Each interaction is a list of dialogue strings.
                Returns an empty list if the file doesn't exist or can't be loaded.
        """
        import os
        import logging
        
        # Resolve the character name to get the canonical name and alias
        canonical_name, alias = resolve_character(character_name)
        
        # Use the alias if it exists, otherwise use the canonical name
        file_name = alias if alias else canonical_name
        
        # Construct the path to the interactions file
        interactions_file = os.path.join("resources", "interactions", f"{file_name}.json")
        
        try:
            with open(interactions_file, 'r') as f:
                interactions = json.load(f)
                logging.info(f"Loaded {len(interactions)} past interactions for {character_name}")
                return interactions
        except FileNotFoundError:
            logging.warning(f"No interactions file found for {character_name} at {interactions_file}")
            return []
        except json.JSONDecodeError:
            logging.error(f"Error decoding JSON from {interactions_file}")
            return []
        except Exception as e:
            logging.error(f"Error loading interactions for {character_name}: {e}")
            return []
    
    def initialize_chatbots(self):
        """Initialize chatbots for all characters.
        
        Creates Chatbot instances for all characters in the game, loading their past interactions
        from JSON files. The chatbots are stored in the group's chatbots dictionary, keyed by
        the character objects.
        
        This method ensures that all chatbots have access to the group, which allows them to
        access the full day's conversation context.
        """
        import logging
        
        # Ensure the group has a chatbots dictionary
        if not hasattr(self.group, 'chatbots'):
            self.group.chatbots = {}
            logging.info("Initialized chatbots dictionary for group")
        
        # Create chatbots for all characters
        for name, character in self.characters.items():
            # Load past interactions for this character
            interactions = self.load_character_interactions(name)
            
            # Create a chatbot for this character
            logging.info(f"Creating chatbot for character: {name}")
            chatbot = Chatbot(character, group=self.group)
            
            # Add past interactions to the chatbot's history
            for interaction in interactions:
                for dialogue in interaction:
                    # Parse the dialogue string to extract speaker and text
                    # Format is "[Speaker] Text"
                    if dialogue.startswith("[") and "]" in dialogue:
                        speaker = dialogue[1:dialogue.index("]")]
                        text = dialogue[dialogue.index("]")+1:].strip()
                        
                        # Add to chatbot's history
                        chatbot.add_to_history({
                            "type": "dialogue",
                            "speaker": speaker,
                            "text": text
                        })
            
            # Store the chatbot in the group's chatbots dictionary
            self.group.chatbots[character] = chatbot
            
            # Log the initialization
            logging.info(f"Initialized chatbot for {name} with {len(interactions)} past interactions")
    
    def run_day(self, day_file):
        """Run a day from a JSON file.

        This method loads a day from the specified JSON file, adds all characters
        to the group, and processes each event in the day. It displays the initial
        and final state of the group, as well as periodic status updates during the day.

        The method performs the following steps:
        1. Load the day events using load_day()
        2. Add all characters to the group
        3. Set the current day in the group
        4. Display the initial group state
        5. Process each event, applying it to the group
        6. Periodically display group status updates (5% chance after each event)
        7. Display the final group state

        Args:
            day_file (str): Path to the JSON file containing the day data
        """
        events = self.load_day(day_file)

        # Add all characters to the group initially
        for character in self.characters.values():
            self.group.add(character)
            
        # Extract the day identifier from the file path
        # Example: "resources/scripted_events/day-01.json" -> "day-01"
        import os
        import json
        import logging
        day_id = os.path.basename(day_file).split('.')[0]
        
        # Set the current day in the group
        self.group.set_current_day(day_id)

        print(f"\n=== Starting Day: {day_file} ===\n")
        print(
            f"Initial group state: {len(self.group.members)} members, mood: {self.group.get_dominant_mood().name}, tension: {self.group.get_tension_description()} ({self.group.tension:.4f})\n")

        # Process each event
        i = 0
        while i < len(events):
            event = events[i]
            event.apply(self.group)
            
            # Check if this was an AI_ASSUME_CONTROL event
            if event.event_type == EventType.AI_ASSUME_CONTROL and event.payload:
                write_to = event.payload.get("write_to", "")
                if write_to:
                    # Check if the pre-generated file exists
                    ai_generated_file = os.path.join("resources", "scripted_events", write_to)
                    if os.path.exists(ai_generated_file):
                        try:
                            # Load the pre-generated events
                            with open(ai_generated_file, 'r') as f:
                                ai_generated_data = json.load(f)
                            
                            logging.info(f"Loaded {len(ai_generated_data)} pre-generated events from {ai_generated_file}")
                            
                            # Convert the pre-generated events to Event objects
                            ai_generated_events = []
                            for entry in ai_generated_data:
                                event_type_str = entry.get("event_type", "dialogue")
                                
                                # For events that require a character
                                char_name = entry.get("character")
                                if not char_name:
                                    logging.warning(f"Warning: Event {event_type_str} missing character field")
                                    continue
                                
                                char_canonical, _ = resolve_character(char_name)
                                if not char_canonical:
                                    logging.warning(f"Warning: Unknown character {char_name}")
                                    continue
                                
                                character = self.characters.get(char_canonical)
                                if not character:
                                    logging.warning(f"Warning: Character {char_canonical} not initialized")
                                    continue
                                
                                if event_type_str == "dialogue" or not event_type_str:
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
                                    ai_event = Event(
                                        event_type=EventType.DIALOGUE,
                                        actor=character,
                                        target=target,
                                        payload={
                                            "text": entry.get("text", ""),
                                            "emotion": entry.get("mood", "neutral")
                                        }
                                    )
                                    ai_generated_events.append(ai_event)
                            
                            # Process the pre-generated events
                            for ai_event in ai_generated_events:
                                ai_event.apply(self.group)
                                
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
                            
                            # Find the next event after AI_ASSUME_CONTROL
                            # Skip all events until the next non-AI_ASSUME_CONTROL event
                            i += 1
                            while i < len(events) and events[i].event_type == EventType.AI_ASSUME_CONTROL:
                                i += 1
                            
                            # Continue with the next event
                            continue
                            
                        except Exception as e:
                            logging.error(f"Error processing pre-generated events: {e}")
                            # Continue with the next event in the original script
                            i += 1
                            continue
            
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
            
            # Move to the next event
            i += 1

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
            day_file = f"resources/scripted_events/day-{day_num}.json"
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
