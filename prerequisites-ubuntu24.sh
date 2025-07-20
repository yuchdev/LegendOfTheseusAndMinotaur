#!/bin/bash

# Ubuntu 22.04 LTS
sudo apt update

# Install Qt6 and PySide6 dependencies
sudo apt install -y qt6-base-dev # Qt6 base libraries
sudo apt install -y qt6-declarative-dev # Qt6 QML libraries
sudo apt install -y qt6-tools-dev # Qt6 tools (e.g., qmake)
sudo apt install -y qt6-quickcontrols2 # Qt6 Quick Controls 2
sudo apt install -y qt6-graphicaleffects # Qt6 graphical effects
sudo apt install -y qt6-svg # Qt6 SVG support
sudo apt install -y qt6-wayland # Qt6 Wayland support
sudo apt install -y qt6-webengine # Qt6 WebEngine for web content
sudo apt install -y python3-pyside6 # PySide6 bindings for Python

# Install other dependencies
sudo apt install -y libxcb-cursor0 # new hard-dependency since Qt 6.5
sudo apt install -y libxkbcommon-x11-0 # keyboard mapping for X11 / XWayland
sudo apt install -y libxcb-xinerama0 # multi-monitor info (used by QScreen)
sudo apt install -y libxcb-xinput0 # input events for high-DPI/Wacom
sudo apt install -y libxcb-randr0 # screen resize / rotate
sudo apt install -y libxcb-icccm4 # window-manager convenience helpers
sudo apt install -y libxcb-image0 # pixel conversions used by QtGui
sudo apt install -y libxcb-keysyms1 # key-symbol look-ups
