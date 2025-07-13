"""
GUI Game module for the text-based game quest.

This module provides a PySide6-based graphical user interface for the game.
It includes components for displaying character information, chat/events,
group dynamics, character avatars, and game controls.
"""

import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QTextEdit, QTableWidget, QTableWidgetItem, QProgressBar, QLabel, QPushButton,
    QHeaderView, QGroupBox, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPixmap

from game import Game
from group import Group
from constants import resolve_character


class GameGUI(QMainWindow):
    """Main GUI window for the game."""

    def __init__(self):
        super().__init__()
        self.debug_text = None
        self.debug_group = None
        self.current_character = None
        self.leadership_value = None
        self.intelligence_value = None
        self.resilience_value = None
        self.emotion_value = None
        self.character_stats = None
        self.avatar_label = None
        self.avatar_group = None
        self.trust_label = None
        self.tension_bar = None
        self.mood_label = None
        self.dynamics_group = None
        self.chat_text = None
        self.chat_group = None
        self.character_table = None
        self.character_group = None
        self.speaking_label = None
        self.leadership_label = None
        self.intelligence_label = None
        self.resilience_label = None
        self.emotion_label = None
        self.game = Game()
        self.current_day = 1
        self.current_event_index = 0
        self.current_events = []
        self.speaking_animation = None

        # Cache for pre-loaded avatar images
        self.avatar_cache = {}

        self.init_ui()
        self.preload_avatar_images()
        self.load_current_day()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Legend - Interactive Game")
        self.setGeometry(100, 100, 1400, 900)

        # Apply background image styling
        self.apply_background_styling()

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main grid layout (2x3 grid)
        main_layout = QGridLayout(central_widget)

        # Create components
        self.create_character_list()
        self.create_chat_events()
        self.create_group_dynamics()
        self.create_avatar_voice()
        self.create_debug_console()
        self.create_controls()

        # Add components to grid layout
        # Row 0: Character List | Chat/Events
        main_layout.addWidget(self.character_group, 0, 0)
        main_layout.addWidget(self.chat_group, 0, 1)

        # Row 1: Group Dynamics | Avatar + Voice
        main_layout.addWidget(self.dynamics_group, 1, 0)
        main_layout.addWidget(self.avatar_group, 1, 1)

        # Row 2: Debug Console | Controls
        main_layout.addWidget(self.debug_group, 2, 0)
        main_layout.addWidget(self.controls_group, 2, 1)

        # Set column stretch to make columns equal width
        main_layout.setColumnStretch(0, 1)
        main_layout.setColumnStretch(1, 1)

    def apply_background_styling(self):
        """Apply background image styling to all Qt widgets from external QSS file."""
        # Load the stylesheet from the external QSS file
        qss_file = os.path.join("resources", "style.qss")

        if os.path.exists(qss_file):
            try:
                with open(qss_file, "r") as f:
                    stylesheet = f.read()

                # Apply the stylesheet to the main window
                self.setStyleSheet(stylesheet)
                self.debug_log(f"Applied stylesheet from {qss_file}")
            except Exception as e:
                self.debug_log(f"Error loading stylesheet: {str(e)}")
        else:
            self.debug_log(f"Stylesheet file not found: {qss_file}")

    def preload_avatar_images(self):
        """Pre-load all avatar images to avoid memory leaks from repeated loading."""
        self.debug_log("Pre-loading avatar images...")

        # Get the target height for scaling
        # We need to ensure the avatar_label is created first
        if hasattr(self, 'avatar_label'):
            target_height = self.avatar_label.maximumHeight() - 4  # Account for border
        else:
            target_height = 296  # Default fallback height (300 - 4)

        # List all avatar files in the avatars directory
        avatars_dir = "avatars"
        if os.path.exists(avatars_dir):
            for filename in os.listdir(avatars_dir):
                if filename.endswith('.png'):
                    avatar_path = os.path.join(avatars_dir, filename)
                    character_name = filename[:-4]  # Remove .png extension

                    try:
                        # Load the original image
                        pixmap = QPixmap(avatar_path)

                        # Scale the image to fit by height while maintaining the aspect ratio
                        if not pixmap.isNull():
                            # noinspection PyUnresolvedReferences
                            scaled_pixmap = pixmap.scaledToHeight(target_height, Qt.SmoothTransformation)

                            # Store in cache with character name as key
                            self.avatar_cache[character_name] = scaled_pixmap
                            self.debug_log(f"Pre-loaded avatar: {character_name}")
                        else:
                            self.debug_log(f"Failed to load avatar image: {avatar_path}")
                    except Exception as e:
                        self.debug_log(f"Error pre-loading avatar {character_name}: {str(e)}")

        self.debug_log(f"Pre-loaded {len(self.avatar_cache)} avatar images")

    def create_character_list(self):
        """Create the character list widget."""
        self.character_group = QGroupBox("Character List (with full stats)")
        layout = QVBoxLayout(self.character_group)

        # Create table widget for characters
        self.character_table = QTableWidget()
        self.character_table.setColumnCount(5)
        self.character_table.setHorizontalHeaderLabels([
            "Name", "Leadership", "Intelligence", "Resilience", "Emotion"
        ])

        # Set table properties
        header = self.character_table.horizontalHeader()
        header.setStretchLastSection(True)
        # noinspection PyUnresolvedReferences
        header.setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.character_table)

    def create_chat_events(self):
        """Create the chat/events widget."""
        self.chat_group = QGroupBox("Chat / Events (auto-scroll)")
        layout = QVBoxLayout(self.chat_group)

        # Create text edit for chat/events
        self.chat_text = QTextEdit()
        self.chat_text.setReadOnly(True)
        self.chat_text.setFont(QFont("Consolas", 10))

        layout.addWidget(self.chat_text)

    def create_group_dynamics(self):
        """Create the group dynamics widget."""
        self.dynamics_group = QGroupBox("Group Dynamic Window")
        layout = QVBoxLayout(self.dynamics_group)

        # Mood label
        self.mood_label = QLabel("Mood: NEUTRAL 😐")
        # noinspection PyUnresolvedReferences
        self.mood_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(self.mood_label)

        # Tension progress bar
        tension_layout = QHBoxLayout()
        tension_layout.addWidget(QLabel("Tension:"))
        self.tension_bar = QProgressBar()
        self.tension_bar.setRange(0, 100)
        self.tension_bar.setValue(0)
        self.tension_bar.setFormat("%p%")
        tension_layout.addWidget(self.tension_bar)
        layout.addLayout(tension_layout)

        # Trust matrix placeholder
        self.trust_label = QLabel("[Trust Matrix]")
        # noinspection PyUnresolvedReferences
        self.trust_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.trust_label)

    def create_avatar_voice(self):
        """Create the avatar and voice UI widget."""
        self.avatar_group = QGroupBox("Character Avatar + Voice UI")
        main_layout = QVBoxLayout(self.avatar_group)

        # Create horizontal layout for avatar and reserved space
        avatar_layout = QHBoxLayout()

        # Avatar image - aligned to left, scaled to fit by height
        self.avatar_label = QLabel()
        # noinspection PyUnresolvedReferences
        self.avatar_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.avatar_label.setStyleSheet("""
            QLabel {
                border: 2px solid gray;
                background-color: rgba(240, 240, 240, 220);
                font-size: 14px;
            }
        """)
        self.avatar_label.setText("[Avatar image]")
        self.avatar_label.setMinimumSize(150, 225)  # Maintain aspect ratio of 256x384
        self.avatar_label.setMaximumSize(200, 300)  # Set reasonable maximum size
        # noinspection PyUnresolvedReferences
        self.avatar_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Reserved space for character stats
        self.character_stats = QWidget()
        self.character_stats.setStyleSheet("background-image: url(resources/background.png); border: 1px dashed #ccc;")

        # Create layout for reserved space
        character_stats_layout = QVBoxLayout(self.character_stats)

        # Create grid layout for character stats
        stats_grid = QGridLayout()

        # Create labels for stats with light gray text
        stats_style = "color: #f0f0f0; font-weight: bold; background-color: rgba(50, 50, 50, 150); padding: 3px; border-radius: 3px; border: none;"
        values_style = "color: #f0f0f0; background-color: rgba(70, 70, 70, 150); padding: 3px; border-radius: 3px; border: none;"

        # Stat labels (left column)
        self.leadership_label = QLabel("Leadership:")
        self.leadership_label.setStyleSheet(stats_style)
        self.intelligence_label = QLabel("Intelligence:")
        self.intelligence_label.setStyleSheet(stats_style)
        self.resilience_label = QLabel("Resilience:")
        self.resilience_label.setStyleSheet(stats_style)
        self.emotion_label = QLabel("Emotion:")
        self.emotion_label.setStyleSheet(stats_style)

        # Value labels (right column)
        self.leadership_value = QLabel("--")
        self.leadership_value.setStyleSheet(values_style)
        self.intelligence_value = QLabel("--")
        self.intelligence_value.setStyleSheet(values_style)
        self.resilience_value = QLabel("--")
        self.resilience_value.setStyleSheet(values_style)
        self.emotion_value = QLabel("--")
        self.emotion_value.setStyleSheet(values_style)

        # Add labels to grid
        stats_grid.addWidget(self.leadership_label, 0, 0)
        stats_grid.addWidget(self.leadership_value, 0, 1)
        stats_grid.addWidget(self.intelligence_label, 1, 0)
        stats_grid.addWidget(self.intelligence_value, 1, 1)
        stats_grid.addWidget(self.resilience_label, 2, 0)
        stats_grid.addWidget(self.resilience_value, 2, 1)
        stats_grid.addWidget(self.emotion_label, 3, 0)
        stats_grid.addWidget(self.emotion_value, 3, 1)

        # Add grid to reserved layout
        character_stats_layout.addLayout(stats_grid)

        # Add stretch to push speaking label to bottom
        character_stats_layout.addStretch()

        # Speaking indicator - now at bottom of reserved space
        self.speaking_label = QLabel("⏺ Speaking (pulsing UI)")
        # noinspection PyUnresolvedReferences
        self.speaking_label.setAlignment(Qt.AlignCenter)
        self.speaking_label.setStyleSheet("color: red; font-weight: bold; background-color: rgba(255, 255, 255, 200);")
        self.speaking_label.hide()  # Initially hidden
        character_stats_layout.addWidget(self.speaking_label)

        # Add to horizontal layout
        avatar_layout.addWidget(self.avatar_label)
        avatar_layout.addWidget(self.character_stats, 1)  # Give reserved space stretch factor

        main_layout.addLayout(avatar_layout)

        # Initialize with a default character if available
        self.current_character = None

    def load_labyrinth_avatar(self):
        """Load the Labyrinth.png avatar as the default from cache."""
        # Try to get Labyrinth from cache
        labyrinth_pixmap = self.avatar_cache.get("Labyrinth")

        if labyrinth_pixmap:
            self.avatar_label.setPixmap(labyrinth_pixmap)
            self.avatar_label.setText("")  # Clear any text
            self.current_character = "Labyrinth"
            self.debug_log("Loaded cached Labyrinth avatar as default")
        else:
            # Fallback to text if not in cache
            self.avatar_label.clear()
            self.avatar_label.setText("[Labyrinth]")
            self.debug_log("Labyrinth avatar not found in cache, using text fallback")

    def update_current_character_avatar(self, character_name):
        """Update the avatar display with the current character."""
        if character_name != self.current_character:
            self.current_character = character_name

            if character_name:
                # Load and display the character's avatar
                avatar_pixmap = self.load_avatar_image(character_name)

                if avatar_pixmap:
                    # Display the avatar image
                    self.avatar_label.setPixmap(avatar_pixmap)
                    self.avatar_label.setText("")  # Clear any text
                    self.debug_log(f"Updated avatar display for {character_name}")
                else:
                    # Fallback to text if no avatar found
                    self.avatar_label.clear()
                    self.avatar_label.setText(f"[{character_name}]")
                    self.debug_log(f"No avatar found for {character_name}, showing text fallback")
            else:
                # Clear avatar if no character
                self.avatar_label.clear()
                self.avatar_label.setText("[Avatar image]")

            # Update character stats display
            self.update_character_stats()

    def create_debug_console(self):
        """Create the debug console widget."""
        self.debug_group = QGroupBox("Debug Console")
        layout = QVBoxLayout(self.debug_group)

        # Create text edit for debug output
        self.debug_text = QTextEdit()
        self.debug_text.setFont(QFont("Consolas", 9))
        self.debug_text.setMaximumHeight(150)

        layout.addWidget(self.debug_text)

    def create_controls(self):
        """Create the game controls widget."""
        self.controls_group = QGroupBox("Controls (Game)")
        layout = QVBoxLayout(self.controls_group)

        # Next step button
        self.next_button = QPushButton("Next Step →")
        self.next_button.clicked.connect(self.next_step)
        layout.addWidget(self.next_button)

        # Previous step button
        self.prev_button = QPushButton("← Undo Last Step")
        self.prev_button.clicked.connect(self.prev_step)
        layout.addWidget(self.prev_button)

        # Day navigation
        day_layout = QHBoxLayout()
        self.prev_day_button = QPushButton("← Previous Day")
        self.prev_day_button.clicked.connect(self.prev_day)
        self.next_day_button = QPushButton("Next Day →")
        self.next_day_button.clicked.connect(self.next_day)

        day_layout.addWidget(self.prev_day_button)
        day_layout.addWidget(self.next_day_button)
        layout.addLayout(day_layout)

        # Current day label
        self.day_label = QLabel(f"Current Day: {self.current_day}")
        # noinspection PyUnresolvedReferences
        self.day_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.day_label)

    def load_current_day(self):
        """Load the current day's events."""
        try:
            day_file = f"play_events/day-{self.current_day:02d}.json"
            self.current_events = self.game.load_day(day_file)
            self.current_event_index = 0

            # Reset game state
            self.game.group = Group()
            for character in self.game.characters.values():
                self.game.group.add(character)

            # Initialize avatar with Labyrinth.png by default
            self.load_labyrinth_avatar()

            self.debug_log(f"Loaded day {self.current_day} with {len(self.current_events)} events")

            # Automatically execute the first event if it exists
            if self.current_events and len(self.current_events) > 0:
                first_event = self.current_events[0]
                # Apply event to game
                first_event.apply(self.game.group)
                # Display event in chat
                self.display_event(first_event)
                # Show speaking animation if there's an actor
                if hasattr(first_event, 'actor') and first_event.actor:
                    self.show_speaking_animation(first_event.actor, first_event.event_type)

                self.current_event_index = 1  # Move to next event
                self.debug_log(f"Automatically executed first event: {first_event.event_type}")

            self.update_display()

        except FileNotFoundError:
            self.debug_log(f"Day file not found: day-{self.current_day:02d}.json")
        except Exception as e:
            self.debug_log(f"Error loading day: {str(e)}")

    def next_step(self):
        """Process the next event."""
        if self.current_event_index < len(self.current_events):
            event = self.current_events[self.current_event_index]

            # Apply event to game
            event.apply(self.game.group)

            # Display event in chat
            self.display_event(event)

            # Show speaking animation
            self.show_speaking_animation(event.actor, event.event_type)

            self.current_event_index += 1
            self.update_display()

            self.debug_log(f"Processed event {self.current_event_index}/{len(self.current_events)}")
        else:
            self.debug_log("No more events in current day")

    def prev_step(self):
        """Undo the last step (simplified implementation)."""
        if self.current_event_index > 0:
            self.current_event_index -= 1
            # For PoC, just reload the day and replay up to current index
            self.reload_day_to_index()
            self.debug_log(f"Undid step, now at {self.current_event_index}/{len(self.current_events)}")
        else:
            self.debug_log("Already at the beginning of the day")

    def next_day(self):
        """Move to the next day."""
        if os.path.exists(f"play_events/day-{self.current_day + 1:02d}.json"):
            self.current_day += 1
            self.day_label.setText(f"Current Day: {self.current_day}")
            self.load_current_day()
            self.chat_text.clear()
        else:
            self.debug_log(f"No next day available (day-{self.current_day + 1:02d}.json)")

    def prev_day(self):
        """Move to the previous day."""
        if self.current_day > 1:
            self.current_day -= 1
            self.day_label.setText(f"Current Day: {self.current_day}")
            self.load_current_day()
            self.chat_text.clear()
        else:
            self.debug_log("Already at day 1")

    def reload_day_to_index(self):
        """Reload the current day and replay events up to current index."""
        # Reset game state
        self.game.group = Group()
        for character in self.game.characters.values():
            self.game.group.add(character)

        # Clear chat
        self.chat_text.clear()

        # Replay events up to current index
        for i in range(self.current_event_index):
            event = self.current_events[i]
            event.apply(self.game.group)
            self.display_event(event)

        self.update_display()

    def resolve_avatar_filename(self, character_name):
        """
        Resolve a character name to an avatar filename.

        Args:
            character_name (str): The character name to resolve

        Returns:
            str or None: The avatar filename if found, None otherwise
        """
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

    def load_avatar_image(self, character_name, target_height=None):
        """
        Get a cached avatar image for a character.

        Args:
            character_name (str): The character name
            target_height (int): Target height for scaling (unused, kept for compatibility)

        Returns:
            QPixmap or None: The cached avatar image, or None if not found
        """
        # First try to find the character name directly in cache
        if character_name in self.avatar_cache:
            self.debug_log(f"Retrieved cached avatar for {character_name}")
            return self.avatar_cache[character_name]

        # Try to resolve the character name using the existing mapping logic
        avatar_path = self.resolve_avatar_filename(character_name)
        if avatar_path:
            # Extract the filename without extension to use as cache key
            filename = os.path.basename(avatar_path)
            cache_key = filename[:-4] if filename.endswith('.png') else filename

            if cache_key in self.avatar_cache:
                self.debug_log(f"Retrieved cached avatar for {character_name} using key {cache_key}")
                return self.avatar_cache[cache_key]

        self.debug_log(f"No cached avatar found for {character_name}")
        return None

    def display_event(self, event):
        """Display an event in the chat window."""
        if hasattr(event, 'actor') and event.actor:
            actor_name = event.actor.name

            # Handle environment_change events
            if hasattr(event, 'event_type') and event.event_type.name == 'ENVIRONMENT_CHANGE':
                if hasattr(event, 'payload') and event.payload:
                    # Capitalize the payload and format as required
                    payload_text = str(event.payload).upper()
                    message = f"<b>[{actor_name}]</b> {payload_text}"
                else:
                    message = f"<b>[{actor_name}]</b> [ENVIRONMENT CHANGE]"
            # Handle events with payload (dialogue events)
            elif hasattr(event, 'payload') and event.payload:
                text = event.payload.get('text', '')
                emotion = event.payload.get('emotion', 'neutral')

                # Format the message
                if hasattr(event, 'target') and event.target:
                    if isinstance(event.target, list):
                        target_names = [t.name for t in event.target]
                        target_str = f"[to {', '.join(target_names)}]"
                    else:
                        target_str = f"[to {event.target.name}]"
                else:
                    target_str = ""

                message = f"<b>[{actor_name}]{target_str}[{emotion}]</b> {text}"
            else:
                # Handle events without payload (enter, leave, etc.)
                event_type_name = event.event_type.name if hasattr(event.event_type, 'name') else str(event.event_type)
                message = f"[{event_type_name}] {actor_name}"

            # Add to chat with color coding based on emotion
            self.chat_text.insertHtml(message + "<br>")

            # Auto-scroll to bottom
            scrollbar = self.chat_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    def show_speaking_animation(self, character, event_type=None):
        """Show speaking animation for a character."""
        if character:
            # Only show speaking animation for dialogue events
            if event_type and hasattr(event_type, 'name') and event_type.name == 'DIALOGUE':
                # Update the character avatar for dialogue events
                self.update_current_character_avatar(character.name)

                # Show speaking indicator
                self.speaking_label.setText(f"⏺ {character.name} Speaking")
                self.speaking_label.show()

                # Hide speaking indicator after 2 seconds
                QTimer.singleShot(2000, self.speaking_label.hide)

    def update_display(self):
        """Update all display components."""
        self.update_character_list()
        self.update_group_dynamics()
        self.update_controls()
        self.update_character_stats()

    def update_character_list(self):
        """Update the character list table."""
        characters = list(self.game.group.members)
        self.character_table.setRowCount(len(characters))

        for i, character in enumerate(characters):
            self.character_table.setItem(i, 0, QTableWidgetItem(character.name))
            self.character_table.setItem(i, 1, QTableWidgetItem(str(character.leadership)))
            self.character_table.setItem(i, 2, QTableWidgetItem(str(character.intelligence)))
            self.character_table.setItem(i, 3, QTableWidgetItem(str(character.resilience)))
            self.character_table.setItem(i, 4, QTableWidgetItem(character.current_emotion.name))

    def update_group_dynamics(self):
        """Update the group dynamics display."""
        if self.game.group.members:
            # Update mood
            dominant_mood = self.game.group.get_dominant_mood()
            mood_emoji = self.get_mood_emoji(dominant_mood)
            self.mood_label.setText(f"Mood: {dominant_mood.name} {mood_emoji}")

            # Update tension
            tension_percent = int(self.game.group.tension * 100)
            self.tension_bar.setValue(tension_percent)

            # Update tension bar color based on level
            if tension_percent < 30:
                color = "green"
            elif tension_percent < 70:
                color = "orange"
            else:
                color = "red"

            self.tension_bar.setStyleSheet(f"""
                QProgressBar {{
                    background-color: rgba(255, 255, 255, 200);
                    border: 1px solid gray;
                    border-radius: 3px;
                    text-align: center;
                }}
                QProgressBar::chunk {{
                    background-color: {color};
                    border-radius: 2px;
                }}
            """)

            # Update trust matrix (simplified)
            trust_info = f"Group Size: {len(self.game.group.members)}\n"
            trust_info += f"Tension: {self.game.group.get_tension_description()}"
            self.trust_label.setText(trust_info)

    def update_controls(self):
        """Update the control buttons state."""
        self.next_button.setEnabled(self.current_event_index < len(self.current_events))
        self.prev_button.setEnabled(self.current_event_index > 0)

        # Update day navigation
        self.prev_day_button.setEnabled(self.current_day > 1)
        next_day_exists = os.path.exists(f"play_events/day-{self.current_day + 1:02d}.json")
        self.next_day_button.setEnabled(next_day_exists)

    def update_character_stats(self):
        """Update the character stats display in the reserved space."""
        if self.current_character:
            # Resolve character name to canonical form
            canonical_name, _ = resolve_character(self.current_character)

            # If not a canonical name, try to find it in the characters dictionary
            if not canonical_name:
                # For characters like "Labyrinth" that might not be in CHARACTERS list
                if self.current_character in self.game.characters:
                    canonical_name = self.current_character
                else:
                    # If we can't resolve the name, show placeholder values
                    self.leadership_value.setText("--")
                    self.intelligence_value.setText("--")
                    self.resilience_value.setText("--")
                    self.emotion_value.setText("--")
                    return

            # Get the Character object
            character = self.game.characters.get(canonical_name)

            if character:
                # Update stats display
                self.leadership_value.setText(str(character.leadership))
                self.intelligence_value.setText(str(character.intelligence))
                self.resilience_value.setText(str(character.resilience))
                self.emotion_value.setText(character.current_emotion.name)
            else:
                # If character not found, show placeholder values
                self.leadership_value.setText("--")
                self.intelligence_value.setText("--")
                self.resilience_value.setText("--")
                self.emotion_value.setText("--")
        else:
            # If no current character, show placeholder values
            self.leadership_value.setText("--")
            self.intelligence_value.setText("--")
            self.resilience_value.setText("--")
            self.emotion_value.setText("--")

    def get_mood_emoji(self, emotion):
        """Get emoji for emotion."""
        emotion_emojis = {
            'NEUTRAL': '😐',
            'CALM': '😌',
            'HAPPY': '😊',
            'EXCITED': '😃',
            'ANGRY': '😠',
            'ANXIOUS': '😰',
            'CONFUSED': '😕',
            'HOPEFUL': '🙂',
            'IRRITATED': '😤',
            'FEARFUL': '😨',
            'PROUD': '😎',
            'COMPASSIONATE': '🥰',
        }
        return emotion_emojis.get(emotion.name, '😐')

    def debug_log(self, message):
        """Add a message to the debug console."""
        # Check if debug_text exists (it might not during initialization)
        if hasattr(self, 'debug_text') and self.debug_text is not None:
            self.debug_text.append(f"[DEBUG] {message}")

            # Auto-scroll to bottom
            scrollbar = self.debug_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
        else:
            # Print to console if debug_text doesn't exist yet
            print(f"[DEBUG] {message}")


def main():
    """Main entry point for the GUI application."""
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("Legend - Interactive Game")
    app.setApplicationVersion("1.0")

    # Create and show main window
    window = GameGUI()
    window.show()

    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
