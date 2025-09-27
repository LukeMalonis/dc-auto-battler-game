import random


class Unit:
    def __init__(self, name, cost, traits, health, damage):
        self.name = name
        self.cost = cost
        self.traits = traits
        self.health = health
        self.damage = damage
        self.stars = 1
        self.id = random.randint(1000, 9999)  # Unique ID for each unit

    def __eq__(self, other):
        return self.id == other.id if other else False

    def can_combine(self, other):
        return self.name == other.name and self.stars == other.stars

    def combine(self, other):
        if self.can_combine(other):
            self.stars += 1
            self.health = int(self.health * 1.8)
            self.damage = int(self.damage * 1.8)

            # If combining two 2-stars into a 3-star, apply additional bonus
            if self.stars == 3:
                self.health = int(self.health * 1.5)  # Extra bonus for 3-star
                self.damage = int(self.damage * 1.5)
            return True
        return False