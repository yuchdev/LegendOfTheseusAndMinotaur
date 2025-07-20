#!/bin/zsh

# macOS Qt6 and PySide6 dependencies installation script
# Requires Homebrew to be installed

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "Error: Homebrew is not installed. Please install Homebrew first:"
    echo '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    exit 1
fi

# Update Homebrew
echo "Updating Homebrew..."
brew update

# Install Qt6
echo "Installing Qt6..."
brew install qt6

# Install Python and pip if not already installed
echo "Installing Python3..."
brew install python3

# Install PySide6 via pip
echo "Installing PySide6..."
pip3 install PySide6

# Verify installations
echo "Verifying installations..."
echo "Qt6 version:"
brew list --versions qt6

echo "PySide6 version:"
python3 -c "import PySide6; print(f'PySide6 version: {PySide6.__version__}')" 2>/dev/null || echo "PySide6 installation verification failed"

echo "Installation complete!"
echo "Note: Qt6 libraries are installed at: $(brew --prefix qt6)"
