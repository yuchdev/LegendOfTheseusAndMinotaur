#!/bin/bash

# Ubuntu 22.04 LTS
sudo apt update
sudo apt install -y libxcb-cursor0 # new hard-dependency since Qt 6.5
sudo apt install -y libxkbcommon-x11-0 # keyboard mapping for X11 / XWayland
sudo apt install -y libxcb-xinerama0 # multi-monitor info (used by QScreen)
sudo apt install -y libxcb-xinput0 # input events for high-DPI/Wacom
sudo apt install -y libxcb-randr0 # screen resize / rotate
sudo apt install -y libxcb-icccm4 # window-manager convenience helpers
sudo apt install -y libxcb-image0 # pixel conversions used by QtGui
sudo apt install -y libxcb-keysyms1 # key-symbol look-ups
