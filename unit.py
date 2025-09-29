
import random
import pygame
import os

# --- GLOBAL PNG CACHE ---
UNIT_IMAGE_CACHE = {}

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
        """Load PNG image if available, using a global cache for speed."""
        if self.png_name:
            path = f"assets/{self.png_name}"
            if self.png_name in UNIT_IMAGE_CACHE:
                self.png_surface = UNIT_IMAGE_CACHE[self.png_name]
                return
            if os.path.exists(path):
                try:
                    original_image = pygame.image.load(path).convert_alpha()
                    scaled_png = pygame.transform.smoothscale(original_image, (100, 100))
                    UNIT_IMAGE_CACHE[self.png_name] = scaled_png
                    self.png_surface = scaled_png
                except Exception as e:
                    print(f"Failed to load image {path}: {e}")
            else:
                print(f"PNG not found for {self.name}: {path}")
        # else: do nothing

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
