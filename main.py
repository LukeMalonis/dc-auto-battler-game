# main.py - Replit version that shows ACTUAL PyGame GUI
import pygame
import sys
import os

# Add current directory to path so imports work
sys.path.append(os.getcwd())

try:
    # Import your exact game
    from dc_auto_battler import main

    print("🎮 Starting DC Auto Battler with PyGame GUI...")
    print("The game window should appear in the Replit output pane!")

    # Run your EXACT game
    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all your game files are in the repository!")
except Exception as e:
    print(f"❌ Game error: {e}")
    import traceback

    traceback.print_exc()