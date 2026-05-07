#!/bin/bash
echo "Setting up HarmonyForge environment..."
pip install music21 --quiet

echo "Running Logic Core..."
python3 engine/main.py

echo "Process complete. Check the 'output' folder."