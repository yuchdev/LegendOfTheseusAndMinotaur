# Legend of Theseus and the Minotaur

![Game Screenshot](https://github.com/yuchdev/LegendOfTheseusAndMinotaur/blob/master/resources/screenshots/game.png)

A narrative-driven, text-based game with a graphical interface that reimagines the classic Greek myth of Theseus and the Minotaur. The game features a complex social simulation system with AI-powered characters, emotional interactions, and dynamic relationships.

## Features

- **Rich Character Interactions**: Characters have attributes (leadership, intelligence, resilience), relationships, and emotional states that evolve based on interactions.
- **Day-by-Day Narrative**: Experience a story that unfolds over multiple days, with events loaded from JSON files.
- **Graphical User Interface**: A Qt-based GUI displays character avatars, dialogue, and group dynamics.
- **AI-Powered Characters**: Characters can be controlled by AI using OpenAI's API, generating contextually appropriate dialogue.
- **User Control System**: Take control of characters and choose from AI-generated dialogue options.
- **Dynamic Group Simulation**: Watch as characters form friendships, develop rivalries, and react emotionally to each other.

## Installation

### Prerequisites

#### macOS

1. Install [Homebrew](https://brew.sh/) if you don't have it already:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. Run the prerequisites script:
   ```bash
   ./scripts/prerequisites-macos.sh
   ```

#### Ubuntu 24.04

Run the prerequisites script:
```bash
./scripts/prerequisites-ubuntu24.sh
```

### Python Dependencies

Install the required Python packages:
```bash
pip install -r requirements.txt
```

### OpenAI API Key (Optional)

If you want to use the AI-powered character functionality, you'll need an OpenAI API key:

1. Get an API key from [OpenAI](https://platform.openai.com/)
2. Set it as an environment variable:
   ```bash
   export OPENAI_API_KEY="your-api-key"
   ```

## Usage

### Running the Game

To start the game with the graphical interface:
```bash
python gui_game.py
```

To run a specific day or sequence of days:
```bash
python gui_game.py 1 2 3  # Run days 1, 2, and 3
```

### Game Controls

- **Next Step**: Advance to the next event in the current day
- **Previous Step**: Go back to the previous event
- **Next Day**: Advance to the next day
- **Previous Day**: Go back to the previous day

### Character Control

The game provides two ways to control characters:

1. **AI Control**: Characters can be controlled by an AI model that generates dialogue based on their attributes and the conversation context.
2. **User Control**: You can take control of characters and choose from AI-generated dialogue options when they're addressed in a conversation.

For more details on the chatbot and user control functionality, see [CHATBOT.md](CHATBOT.md).

## Project Structure

- **Core Game Logic**:
  - `game.py`: Main game class and logic
  - `character.py`: Character class with attributes and relationships
  - `event.py`: Event system for game actions
  - `group.py`: Group dynamics and character interactions
  - `emotion.py`: Emotion system for characters

- **User Interface**:
  - `gui_game.py`: Qt-based graphical user interface

- **AI Integration**:
  - `chatbot.py`: AI-controlled character functionality
  - `user_control.py`: User-controlled character functionality

- **Content**:
  - `play_events/`: JSON files containing day events
  - `avatars/`: Character avatar images
  - `resources/`: UI resources (background images, stylesheets)

- **Tools and Scripts**:
  - `scripts/`: Installation scripts
  - `tools/`: Utility scripts for content creation

## Dependencies

- **PySide6** (≥ 6.6.0): Python bindings for Qt6
- **Qt6**: Cross-platform application framework
- **OpenAI API** (optional): For AI-powered character functionality

## Development

### Adding New Days

Create new JSON files in the `play_events/` directory following the format of the existing files. Each file should contain an array of event objects with appropriate event types and data.

### Adding New Characters

1. Add the character to the `CHARACTERS` constant in `constants.py`
2. Add character attributes in the `initialize_characters` method in `game.py`
3. Add an avatar image in the `avatars/` directory

## Credits

- Based on Victor Pelevin's novel/play "The Helmet of Horror, or the Myth of Theseus and the Minotaur"
- Developed to test boundaries of AI-powered interactive storytelling

## License

MIT License 
