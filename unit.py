import random
import pygame
import os


class Unit:
    def __init__(self, name, cost, traits, health, damage, png_name=None):
        self.name = name
        self.cost = cost
        self.traits = traits
        self.health = health
        self.damage = damage
        self.stars = 1
        self.id = random.randint(1000, 9999)
        self.png_name = png_name
        self.png_surface = None
        self.load_png()

    def load_png(self):
        """Load PNG image if available"""
        if self.png_name:
            print(f"Attempting to load PNG for {self.name}: {self.png_name}")  # Debug

            # Try different possible paths
            possible_paths = [
                f"assets/{self.png_name}",
                f"unit_pngs/{self.png_name}",
                self.png_name,
                f"./assets/{self.png_name}",
                f"./unit_pngs/{self.png_name}"
            ]

            for path in possible_paths:
                if os.path.exists(path):
                    try:
                        print(f"Found PNG at: {path}")  # Debug
                        original_image = pygame.image.load(path).convert_alpha()
                        # Scale to appropriate size
                        self.png_surface = pygame.transform.smoothscale(original_image, (100, 100))
                        print(f"Successfully loaded PNG for {self.name}")  # Debug
                        return
                    except Exception as e:
                        print(f"Failed to load image {path}: {e}")

            print(f"PNG not found for {self.name}. Tried: {possible_paths}")  # Debug
        else:
            print(f"No PNG name specified for {self.name}")  # Debug

    def __eq__(self, other):
        return self.id == other.id if other else False

    def can_combine(self, other):
        return self.name == other.name and self.stars == other.stars

    def combine(self, other):
        if self.can_combine(other):
            self.stars += 1
            self.health = int(self.health * 1.8)
            self.damage = int(self.damage * 1.8)

            if self.stars == 3:
                self.health = int(self.health * 1.5)
                self.damage = int(self.damage * 1.5)
            return True
        return False