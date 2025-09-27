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
        """Sell unit from bench with proper star-based values"""
        if 0 <= bench_index < len(self.bench) and self.bench[bench_index]:
            unit = self.bench[bench_index]

            # Base sell value = cost
            sell_value = unit.cost

            # Apply star multipliers
            if unit.stars == 2:
                # 2-star: 1-cost gets 3, others get cost*2 + 1
                if unit.cost == 1:
                    sell_value = 3
                else:
                    sell_value = (unit.cost * 2) + 1
            elif unit.stars == 3:
                # 3-star: 1-cost gets 9, others get more complex formula
                if unit.cost == 1:
                    sell_value = 9
                else:
                    sell_value = (unit.cost * 5) + 2  # Example: 2-cost = 12, 3-cost = 17, etc.

            self.gold += sell_value
            self.bench[bench_index] = None
            return True
        return False

    def sell_board_unit(self, x, y):
        """Sell unit from board with proper star-based values"""
        if (0 <= x < GameConstants.BOARD_WIDTH and
                0 <= y < GameConstants.BOARD_HEIGHT and
                self.board[y][x]):

            unit = self.board[y][x]

            # Same sell logic as above
            sell_value = unit.cost
            if unit.stars == 2:
                if unit.cost == 1:
                    sell_value = 3
                else:
                    sell_value = (unit.cost * 2) + 1
            elif unit.stars == 3:
                if unit.cost == 1:
                    sell_value = 9
                else:
                    sell_value = (unit.cost * 5) + 2

            self.gold += sell_value
            self.board[y][x] = None
            self.calculate_traits()
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
        """Check for unit combinations across bench and board"""
        # Combine units by name and stars across both bench and board
        unit_counts = {}

        # Count units on bench
        for unit in self.bench:
            if unit:
                key = (unit.name, unit.stars)
                if key not in unit_counts:
                    unit_counts[key] = []
                unit_counts[key].append(('bench', unit))

        # Count units on board
        for y, row in enumerate(self.board):
            for x, unit in enumerate(row):
                if unit:
                    key = (unit.name, unit.stars)
                    if key not in unit_counts:
                        unit_counts[key] = []
                    unit_counts[key].append(('board', unit, (x, y)))

        # Check for combinations (need 3 of same name and stars)
        for (name, stars), units in unit_counts.items():
            if len(units) >= 3 and stars < 3:  # Can't combine beyond 3-star
                # Take first 3 units to combine
                base_unit_info = units[0]
                units_to_remove = units[1:3]

                # Get the base unit (the one that will be upgraded)
                if base_unit_info[0] == 'bench':
                    base_unit = base_unit_info[1]
                else:  # board
                    base_unit = base_unit_info[1]

                # Combine with the other 2 units
                for unit_info in units_to_remove:
                    if unit_info[0] == 'bench':
                        unit_to_combine = unit_info[1]
                        # Remove from bench
                        for i, bench_unit in enumerate(self.bench):
                            if bench_unit == unit_to_combine:
                                self.bench[i] = None
                                break
                    else:  # board
                        unit_to_combine = unit_info[1]
                        x, y = unit_info[2]
                        self.board[y][x] = None

                    # Perform the combination
                    base_unit.combine(unit_to_combine)

                # Re-check traits after combination
                self.calculate_traits()
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

    def can_combine_anywhere(self, unit_to_check):
        """Check if a unit can combine with existing units anywhere (bench or board)"""
        if not unit_to_check:
            return False
        count = 0
        # Count matching units on bench
        for bench_unit in self.bench:
            if bench_unit and bench_unit.name == unit_to_check.name and bench_unit.stars == unit_to_check.stars:
                count += 1
        # Count matching units on board
        for row in self.board:
            for board_unit in row:
                if board_unit and board_unit.name == unit_to_check.name and board_unit.stars == unit_to_check.stars:
                    count += 1
        return count >= 2  # Need 2 existing + the new one = 3 total

    def buy_and_combine(self, shop_index):
        """Buy a unit and automatically combine it with existing matching units"""
        if 0 <= shop_index < len(self.shop) and self.shop[shop_index]:
            unit = self.shop[shop_index]
            if self.gold >= unit.cost:
                # Find existing matching units to combine with
                units_to_combine = []

                # Check bench for matching units
                for i, bench_unit in enumerate(self.bench):
                    if bench_unit and bench_unit.name == unit.name and bench_unit.stars == unit.stars:
                        units_to_combine.append(('bench', i, bench_unit))

                # Check board for matching units
                for y, row in enumerate(self.board):
                    for x, board_unit in enumerate(row):
                        if board_unit and board_unit.name == unit.name and board_unit.stars == unit.stars:
                            units_to_combine.append(('board', (x, y), board_unit))

                # If we have at least 2 matching units (will make 3 with the new one)
                if len(units_to_combine) >= 2:
                    # Take the first 2 units to combine with
                    base_unit = units_to_combine[0][2]
                    second_unit = units_to_combine[1][2]

                    # Combine the units
                    base_unit.combine(second_unit)

                    # Remove the second unit from its location
                    if units_to_combine[1][0] == 'bench':
                        self.bench[units_to_combine[1][1]] = None
                    else:  # board
                        x, y = units_to_combine[1][1]
                        self.board[y][x] = None

                    # Pay for the unit and remove from shop
                    self.gold -= unit.cost
                    self.shop[shop_index] = None
                    self.calculate_traits()
                    return True

                # Fallback to normal purchase if combination didn't work
                return self.buy_unit(shop_index)
        return False