# main.py - Replit PyGame version
import os
import pygame

# Set up PyGame for Replit environment
os.environ['SDL_VIDEODRIVER'] = 'x11'
os.environ['DISPLAY'] = ':0'

# Initialize PyGame
pygame.init()

print("🎮 Starting DC Auto Battler...")
print("If you see a PyGame window, it's working!")

# Import and run your game
try:
    from dc_auto_battler import main
    main()
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()