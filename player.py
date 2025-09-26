import random
from game_constants import GameConstants


class Player:
    def __init__(self):
        self.gold = 8  # Start with 8 gold
        self.level = 1
        self.xp = 0
        self.xp_to_level = [2, 6, 10, 20, 36, 56, 80, 100]  # XP needed for levels 2-9
        self.bench = [None] * GameConstants.BENCH_SLOTS
        self.board = [[None for _ in range(GameConstants.BOARD_WIDTH)]
                      for _ in range(GameConstants.BOARD_HEIGHT)]
        self.shop = []
        self.traits = {}
        self.refresh_cost = 2
        self.round = 1
        self.generate_shop()

    def calculate_income(self):
        """Calculate gold income for next round"""
        base_income = 5
        interest = min(self.gold // 10, 5)  # 1 gold per 10, max 5
        return base_income + interest

    def end_turn(self):
        """End turn and receive income"""
        income = self.calculate_income()
        self.gold += income
        self.round += 1
        self.generate_shop()  # Free refresh each round
        return income

    def buy_xp(self):
        """Buy 4 XP for 4 gold"""
        if self.gold >= 4 and self.level < 9:
            self.gold -= 4
            self.xp += 4
            if self.level < 9 and self.xp >= self.xp_to_level[self.level - 1]:
                self.level += 1
                self.xp = 0
                return True
        return False

    def refresh_shop(self):
        """Refresh shop for 2 gold"""
        if self.gold >= self.refresh_cost:
            self.gold -= self.refresh_cost
            self.generate_shop()
            return True
        return False

    def generate_shop(self):
        """Generate shop units based on player level"""
        # Unit pools by cost tier
        cost_1_units = [
            self.create_unit("Batman", 1, ["Hero", "Tech"], 600, 50),
            self.create_unit("Harley Quinn", 1, ["Villain", "Acrobat"], 450, 55),
            self.create_unit("Robin", 1, ["Hero", "Acrobat"], 500, 45),
        ]
        cost_2_units = [
            self.create_unit("Joker", 2, ["Villain", "Chaos"], 500, 60),
            self.create_unit("Aquaman", 2, ["Hero", "Atlantean"], 850, 60),
            self.create_unit("Catwoman", 2, ["Villain", "Acrobat"], 550, 65),
        ]
        cost_3_units = [
            self.create_unit("Wonder Woman", 3, ["Hero", "Amazon"], 800, 70),
            self.create_unit("Green Lantern", 3, ["Hero", "Corps"], 750, 65),
            self.create_unit("Bane", 3, ["Villain", "Brute"], 900, 55),
        ]
        cost_4_units = [
            self.create_unit("Flash", 4, ["Hero", "Speedster"], 700, 90),
            self.create_unit("Nightwing", 4, ["Hero", "Acrobat"], 750, 75),
        ]
        cost_5_units = [
            self.create_unit("Superman", 5, ["Hero", "Alien"], 1000, 80),
            self.create_unit("Darkseid", 5, ["Villain", "Alien"], 1200, 70),
        ]

        # Shop odds based on level (simplified)
        shop_units = []
        for _ in range(GameConstants.SHOP_SLOTS):
            roll = random.random()
            if self.level == 1:
                pool = cost_1_units
            elif self.level <= 3:
                pool = cost_1_units + cost_2_units if roll > 0.7 else cost_1_units
            elif self.level <= 5:
                pool = cost_1_units + cost_2_units + cost_3_units
            elif self.level <= 7:
                pool = cost_2_units + cost_3_units + cost_4_units
            else:
                pool = cost_3_units + cost_4_units + cost_5_units

            shop_units.append(random.choice(pool))

        self.shop = shop_units

    def create_unit(self, name, cost, traits, health, damage):
        """Helper to create unit instances"""
        from unit import Unit
        return Unit(name, cost, traits, health, damage)

    def buy_unit(self, shop_index):
        """Buy unit from shop"""
        if 0 <= shop_index < len(self.shop) and self.shop[shop_index]:
            unit = self.shop[shop_index]
            if self.gold >= unit.cost:
                # Find empty bench slot
                for i, bench_unit in enumerate(self.bench):
                    if bench_unit is None:
                        # Create a new instance so we don't reference the shop unit
                        new_unit = self.create_unit(unit.name, unit.cost, unit.traits.copy(), unit.health, unit.damage)
                        self.bench[i] = new_unit
                        self.gold -= unit.cost
                        self.shop[shop_index] = None
                        self.check_combinations()
                        return True
        return False

    def sell_unit(self, bench_index):
        """Sell unit from bench for full cost"""
        if 0 <= bench_index < len(self.bench) and self.bench[bench_index]:
            unit = self.bench[bench_index]
            self.gold += unit.cost
            self.bench[bench_index] = None
            return True
        return False

    def move_unit_to_board(self, bench_index, board_x, board_y):
        """Move unit from bench to board"""
        if (0 <= bench_index < len(self.bench) and self.bench[bench_index] and
                0 <= board_x < GameConstants.BOARD_WIDTH and
                0 <= board_y < GameConstants.BOARD_HEIGHT and
                self.board[board_y][board_x] is None):

            # Check if we have board space for this level
            current_units = sum(1 for row in self.board for unit in row if unit is not None)
            if current_units < GameConstants.MAX_BOARD_UNITS[self.level - 1]:
                self.board[board_y][board_x] = self.bench[bench_index]
                self.bench[bench_index] = None
                self.calculate_traits()
                return True
        return False

    def move_unit_to_bench(self, board_x, board_y, bench_index):
        """Move unit from board to bench"""
        if (0 <= bench_index < len(self.bench) and self.bench[bench_index] is None and
                0 <= board_x < GameConstants.BOARD_WIDTH and
                0 <= board_y < GameConstants.BOARD_HEIGHT and
                self.board[board_y][board_x] is not None):
            self.bench[bench_index] = self.board[board_y][board_x]
            self.board[board_y][board_x] = None
            self.calculate_traits()
            return True
        return False

    def check_combinations(self):
        """Check for 3 of the same unit to combine"""
        # Count units by name and stars on bench
        unit_counts = {}
        for unit in self.bench:
            if unit:
                key = (unit.name, unit.stars)
                if key not in unit_counts:
                    unit_counts[key] = []
                unit_counts[key].append(unit)

        # Check for combinations
        for (name, stars), units in unit_counts.items():
            if len(units) >= 3:
                # Combine first 3 units
                base_unit = units[0]
                units_to_remove = units[1:3]

                for unit in units_to_remove:
                    base_unit.combine(unit)
                    # Remove the combined units from bench
                    for i, bench_unit in enumerate(self.bench):
                        if bench_unit == unit:
                            self.bench[i] = None
                break

    def calculate_traits(self):
        """Calculate active traits from board units"""
        trait_counts = {}

        # Count traits from board units only
        for row in self.board:
            for unit in row:
                if unit:
                    for trait in unit.traits:
                        trait_counts[trait] = trait_counts.get(trait, 0) + 1

        self.traits = trait_counts