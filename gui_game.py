"""
GUI Game module for the text-based game quest.

This module provides a PySide6-based graphical user interface for the game.
It includes components for displaying character information, chat/events,
group dynamics, character avatars, and game controls.
"""

import sys
import os
import json
from typing import List, Optional
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QTextEdit, QTableWidget, QTableWidgetItem, QProgressBar, QLabel, QPushButton,
    QSplitter, QFrame, QHeaderView, QGroupBox
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QRect, Signal, QThread
from PySide6.QtGui import QFont, QPixmap, QPalette, QColor

from game import Game
from character import Character
from group import Group
from emotion import Emotion
from constants import resolve_character, CHARACTERS, ALIASES


class GameGUI(QMainWindow):
    """Main GUI window for the game."""

    def __init__(self):
        super().__init__()
        self.game = Game()
        self.current_day = 1
        self.current_event_index = 0
        self.current_events = []
        self.speaking_animation = None

        self.init_ui()
        self.load_current_day()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Legend - Interactive Game")
        self.setGeometry(100, 100, 1400, 900)

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
        self.trust_label.setAlignment(Qt.AlignCenter)
        self.trust_label.setStyleSheet("border: 1px solid gray; padding: 10px;")
        layout.addWidget(self.trust_label)

    def create_avatar_voice(self):
        """Create the avatar and voice UI widget."""
        self.avatar_group = QGroupBox("Character Avatar + Voice UI")
        layout = QVBoxLayout(self.avatar_group)

        # Avatar image placeholder
        self.avatar_label = QLabel()
        self.avatar_label.setAlignment(Qt.AlignCenter)
        self.avatar_label.setStyleSheet("""
            QLabel {
                border: 2px solid gray;
                background-color: #f0f0f0;
                min-height: 150px;
                font-size: 14px;
            }
        """)
        self.avatar_label.setText("[Avatar image]")
        layout.addWidget(self.avatar_label)

        # Speaking indicator
        self.speaking_label = QLabel("⏺ Speaking (pulsing UI)")
        self.speaking_label.setAlignment(Qt.AlignCenter)
        self.speaking_label.setStyleSheet("color: red; font-weight: bold;")
        self.speaking_label.hide()  # Initially hidden
        layout.addWidget(self.speaking_label)

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
        self.day_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.day_label)

    def load_current_day(self):
        """Load the current day's events."""
        try:
            day_file = f"play_chapters/day-{self.current_day:02d}.json"
            self.current_events = self.game.load_day(day_file)
            self.current_event_index = 0

            # Reset game state
            self.game.group = Group()
            for character in self.game.characters.values():
                self.game.group.add(character)

            self.debug_log(f"Loaded day {self.current_day} with {len(self.current_events)} events")
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
            self.show_speaking_animation(event.actor)

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
        if os.path.exists(f"play_chapters/day-{self.current_day + 1:02d}.json"):
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

    def load_avatar_image(self, character_name):
        """
        Load an avatar image for a character.

        Args:
            character_name (str): The character name

        Returns:
            QPixmap or None: The loaded avatar image, or None if not found
        """
        avatar_path = self.resolve_avatar_filename(character_name)

        if avatar_path and os.path.exists(avatar_path):
            try:
                pixmap = QPixmap(avatar_path)
                if not pixmap.isNull():
                    # Scale the image to fit the avatar label while maintaining aspect ratio
                    scaled_pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.debug_log(f"Loaded avatar for {character_name}: {avatar_path}")
                    return scaled_pixmap
                else:
                    self.debug_log(f"Failed to load avatar image: {avatar_path}")
            except Exception as e:
                self.debug_log(f"Error loading avatar for {character_name}: {str(e)}")
        else:
            self.debug_log(f"Avatar not found for {character_name}")

        return None

    def display_event(self, event):
        """Display an event in the chat window."""
        if hasattr(event, 'actor') and hasattr(event, 'payload'):
            actor_name = event.actor.name if event.actor else "Unknown"
            text = event.payload.get('text', '')
            emotion = event.payload.get('emotion', 'neutral')

            # Format the message
            if hasattr(event, 'target') and event.target:
                if isinstance(event.target, list):
                    target_names = [t.name for t in event.target]
                    target_str = f" (to {', '.join(target_names)})"
                else:
                    target_str = f" (to {event.target.name})"
            else:
                target_str = ""

            message = f"{actor_name}{target_str}: \"{text}\" [{emotion}]"

            # Add to chat with color coding based on emotion
            self.chat_text.append(message)

            # Auto-scroll to bottom
            scrollbar = self.chat_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    def show_speaking_animation(self, character):
        """Show speaking animation for a character."""
        if character:
            # Load and display the character's avatar
            avatar_pixmap = self.load_avatar_image(character.name)

            if avatar_pixmap:
                # Display the avatar image
                self.avatar_label.setPixmap(avatar_pixmap)
                self.avatar_label.setText("")  # Clear any text
            else:
                # Fallback to text if no avatar found
                self.avatar_label.clear()
                self.avatar_label.setText(f"[{character.name}]")

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
                QProgressBar::chunk {{
                    background-color: {color};
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
        next_day_exists = os.path.exists(f"play_chapters/day-{self.current_day + 1:02d}.json")
        self.next_day_button.setEnabled(next_day_exists)

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
        self.debug_text.append(f"[DEBUG] {message}")

        # Auto-scroll to bottom
        scrollbar = self.debug_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


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
