import random
from game_constants import GameConstants
import os

class Player:
    def __init__(self):
        self.gold = 8
        self.level = 1
        self.xp = 0
        self.xp_to_level = [2, 2, 6, 10, 20, 36, 48, 76, 84]
        self.bench = [None] * GameConstants.BENCH_SLOTS
        self.board = [[None for _ in range(GameConstants.BOARD_WIDTH)]
                      for _ in range(GameConstants.BOARD_HEIGHT)]
        self.shop = []
        self.traits = {}
        self.refresh_cost = 2
        self.round = 1
        self.hugo_replacement_choice = None   # <--- ADD THIS LINE
        self.generate_shop()

    def calculate_income(self):
        """Calculate gold income for next round"""
        base_income = 5
        interest = min(self.gold // 10, 5)  # 1 gold per 10, max 5
        return base_income + interest

    def end_turn(self):
        """End turn, receive income, and grant 2 XP (with correct level-up behavior up to 10)"""
        income = self.calculate_income()
        self.gold += income
        self.round += 1

        # Give 2 XP per round, but do not exceed level 10
        if self.level < 10:
            self.xp += 2
            while self.level < 10:
                xp_needed = self.xp_to_level[self.level - 1] if self.level <= len(self.xp_to_level) else 100
                if self.xp >= xp_needed:
                    self.xp -= xp_needed
                    self.level += 1
                    if self.level == 10:
                        self.xp = 0  # XP is capped at 10
                        break
                else:
                    break

        self.generate_shop()  # Free refresh each round
        return income

    def buy_xp(self):
        """Buy 4 XP for 4 gold (works up to level 10, handles overflow XP)"""
        if self.gold >= 4 and self.level < 10:
            self.gold -= 4
            self.xp += 4
            while self.level < 10:
                xp_needed = self.xp_to_level[self.level - 1] if self.level <= len(self.xp_to_level) else 100
                if self.xp >= xp_needed:
                    self.xp -= xp_needed
                    self.level += 1
                    if self.level == 10:
                        self.xp = 0  # Cap XP at 0 on max level
                        break
                else:
                    break
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
        # Use assets directory for PNGs
        png_dir = "assets"
        png_files = []
        if os.path.exists(png_dir):
            png_files = os.listdir(png_dir)

        # Unit pools by cost tier with updated roster
        cost_1_units = [
            self.create_unit("Martian Manhunter", 1, ["Justice League", "Bruiser"], 700, 45, png_files),
            self.create_unit("Robin", 1, ["Bat Family", "League of Assassins"], 550, 55, png_files),
            self.create_unit("Amazo", 1, ["Duelists", "Robots"], 600, 50, png_files),
            self.create_unit("Batgirl", 1, ["Bat Family", "N/A"], 500, 60, png_files),
            self.create_unit("Captain Boomerang", 1, ["Snipers", "Suicide Squad", "Rogues Gallery"], 450, 65, png_files),
            self.create_unit("Krypto", 1, ["Animals", "Kryptonians"], 400, 70, png_files),
            self.create_unit("Killer Croc", 1, ["Suicide Squad", "Bruiser"], 650, 40, png_files),
            self.create_unit("Captain Cold", 1, ["Rogues Gallery", "Bruiser"], 520, 58, png_files),
            self.create_unit("Mirror Master", 1, ["Rogues Gallery", "Snipers"], 460, 62, png_files),
            self.create_unit("Pied Piper", 1, ["Rogues Gallery"], 440, 60, png_files),
            self.create_unit("Trickster", 1, ["Rogues Gallery"], 430, 65, png_files),
            self.create_unit("Heatwave", 1, ["Rogues Gallery", "Bruiser"], 540, 56, png_files),
            self.create_unit("Deadshot", 1, ["Suicide Squad", "Snipers"], 470, 68, png_files),
        ]

        cost_2_units = [
            self.create_unit("Catwoman", 2, ["Bat Family", "Duelists"], 600, 70, png_files),
            self.create_unit("Green Arrow", 2, ["Justice League", "Snipers"], 550, 75, png_files),
            self.create_unit("Aquaman", 2, ["Justice League", "Form Swapper"], 800, 60, png_files),
            self.create_unit("Power Girl", 2, ["Kryptonians", "Bruiser"], 750, 65, png_files),
            self.create_unit("Cheetah", 2, ["Animals", "Legion of Doom"], 650, 72, png_files),
            self.create_unit("Nightwing", 2, ["Teen Titans", "Form Swapper"], 620, 68, png_files),
            self.create_unit("Starfire", 2, ["Teen Titans"], 580, 74, png_files),
            self.create_unit("Harley Quinn", 2, ["Suicide Squad", "Clown Prince of Crime"], 560, 70, png_files),
            self.create_unit("Lex Luthor", 2, ["Legion of Doom", "Bruiser"], 680, 58, png_files),
            # REMOVED Mr. Freeze, Two Face, and Poison Ivy from 2-cost pool!
            self.create_unit("Rae Al Ghul", 2, ["League of Assassins"], 590, 66, png_files),
        ]

        cost_3_units = [
            self.create_unit("Weather Wizard", 3, ["Bruiser", "Sorcerer", "Rogues Gallery"], 700, 68, png_files),
            self.create_unit("Beast Boy", 3, ["Animals", "Teen Titans"], 650, 72, png_files),
            self.create_unit("Batman", 3, ["Justice League", "Bat Family"], 720, 75, png_files),
            self.create_unit("Green Lantern", 3, ["Justice League", "Sorcerer"], 680, 70, png_files),
            self.create_unit("Supergirl", 3, ["Kryptonians", "Snipers"], 740, 78, png_files),
            # Hugo logic handled below
            self.create_unit("Raven", 3, ["Teen Titans", "Sorcerer"], 660, 74, png_files),
            self.create_unit("Cyborg", 3, ["Teen Titans", "Robots", "Bruiser"], 780, 65, png_files),
            self.create_unit("Bane", 3, ["Legion of Doom", "Bruiser"], 820, 62, png_files),
            self.create_unit("Star Sapphire", 3, ["Legion of Doom", "Sorcerer"], 640, 76, png_files),
            self.create_unit("Black Manta", 3, ["Legion of Doom", "Form Swapper"], 690, 71, png_files),
            self.create_unit("Swamp Thing", 3, ["Form Swapper", "Justice League Dark"], 750, 64, png_files),
            self.create_unit("Constantine", 3, ["Sorcerer", "Justice League Dark"], 580, 80, png_files),
            self.create_unit("Zatanna", 3, ["Sorcerer", "Justice League Dark"], 610, 77, png_files),
        ]

        # Remove Hugo Strange from the pool unless no replacement chosen yet
        if self.hugo_replacement_choice is None:
            cost_3_units.append(self.create_unit("Hugo Strange", 3, ["Mind Games"], 600, 65, png_files))
        else:
            # Only show the chosen replacement instead of Hugo
            # Make sure to use Mind Games trait, cost 3, correct stats for the character
            hugo_map = {
                "Mr. Freeze": (3, ["Mind Games"], 720, 52),
                "Two Face": (3, ["Mind Games"], 520, 78),
                "Poison Ivy": (3, ["Mind Games"], 480, 76),
            }
            if self.hugo_replacement_choice in hugo_map:
                cost, traits, health, damage = hugo_map[self.hugo_replacement_choice]
                cost_3_units.append(
                    self.create_unit(self.hugo_replacement_choice, cost, traits, health, damage, png_files))

        cost_4_units = [
            self.create_unit("Superman", 4, ["Justice League", "Kryptonians"], 1000, 80, png_files),
            self.create_unit("Wonder Woman", 4, ["Justice League", "Bruiser"], 950, 82, png_files),
            self.create_unit("Gorilla Grodd", 4, ["Animals", "Bruiser"], 1100, 70, png_files),
            self.create_unit("Deathstroke", 4, ["League of Assassins"], 920, 85, png_files),
            self.create_unit("Talia Al Ghul", 4, ["League of Assassins"], 880, 78, png_files),
            self.create_unit("Solomon Grundy", 4, ["Legion of Doom", "Resurrection"], 1200, 65, png_files),
            self.create_unit("Metallo", 4, ["Robots"], 850, 88, png_files),
            self.create_unit("Red Tornado", 4, ["Robots"], 870, 84, png_files),
            self.create_unit("King Shark", 4, ["Animals", "Lurking In The Waters"], 1150, 72, png_files),
            self.create_unit("The Question", 4, ["I Have A Question"], 780, 90, png_files),
            self.create_unit("Amazo", 4, ["Robots", "Duelists"], 940, 83, png_files),
            self.create_unit("Brainiac", 4, ["Robots", "Threat"], 890, 86, png_files),
            self.create_unit("Zoom", 4, ["Threat"], 820, 92, png_files),
        ]

        cost_5_units = [
            self.create_unit("Flash", 5, ["Justice League", "Fastest Man Alive"], 900, 95, png_files),
            self.create_unit("Dr. Fate", 5, ["5 Cost Trait", "Sorcerer"], 850, 90, png_files),
            self.create_unit("Red Hood", 5, ["Bat Family", "Snipers"], 920, 88, png_files),
            self.create_unit("Solomon Grundy", 5, ["Legion of Doom", "Resurrection"], 1300, 75, png_files),
            self.create_unit("King Shark", 5, ["Animals", "Lurking In The Waters"], 1250, 80, png_files),
            self.create_unit("Darkseid", 5, ["Threat"], 1400, 85, png_files),
            self.create_unit("Brainiac", 5, ["Robots", "Threat"], 950, 92, png_files),
            self.create_unit("Zoom", 5, ["Threat"], 880, 98, png_files),
            self.create_unit("The Question", 5, ["I Have A Question", "Threat"], 800, 95, png_files),
        ]

        # Shop odds table for each level: [1, 2, 3, 4, 5]-cost units (percentages)
        shop_odds = {
            1: [1.00, 0.00, 0.00, 0.00, 0.00],  # Level 1
            2: [1.00, 0.00, 0.00, 0.00, 0.00],  # Level 2
            3: [0.75, 0.25, 0.00, 0.00, 0.00],  # Level 3
            4: [0.55, 0.30, 0.15, 0.00, 0.00],  # Level 4
            5: [0.45, 0.33, 0.20, 0.02, 0.00],  # Level 5
            6: [0.30, 0.40, 0.25, 0.05, 0.00],  # Level 6
            7: [0.19, 0.30, 0.40, 0.10, 0.01],  # Level 7
            8: [0.17, 0.24, 0.32, 0.24, 0.03],  # Level 8
            9: [0.15, 0.18, 0.25, 0.30, 0.12],  # Level 9
            10: [0.05, 0.10, 0.20, 0.40, 0.25]  # Level 10
        }
        unit_pools = [cost_1_units, cost_2_units, cost_3_units, cost_4_units, cost_5_units]

        shop_units = []
        for _ in range(GameConstants.SHOP_SLOTS):
            roll = random.random()
            level = max(1, min(self.level, 10))
            odds = shop_odds[level]
            cumulative = 0.0
            for idx, chance in enumerate(odds):
                cumulative += chance
                if roll < cumulative:
                    pool = unit_pools[idx]
                    break
            else:
                pool = unit_pools[0]  # fallback, should never hit
            shop_units.append(random.choice(pool))
        self.shop = shop_units

    def create_unit(self, name, cost, traits, health, damage, png_files):
        from unit import Unit
        png_name = None
        for file in png_files:
            file_name = file.replace('.png', '').replace('_', ' ')
            if name.lower() in file_name.lower() or file_name.lower() in name.lower():
                png_name = file
                break

        return Unit(name, cost, traits, health, damage, png_name)

    def buy_unit(self, shop_index):
        """Buy unit from shop"""
        if 0 <= shop_index < len(self.shop) and self.shop[shop_index]:
            unit = self.shop[shop_index]
            if self.gold >= unit.cost:
                # Find empty bench slot
                for i, bench_unit in enumerate(self.bench):
                    if bench_unit is None:
                        # Create a new instance so we don't reference the shop unit
                        new_unit = self.create_unit(unit.name, unit.cost, unit.traits.copy(), unit.health, unit.damage,
                                                    [])
                        if unit.png_name:
                            new_unit.png_name = unit.png_name
                        if unit.png_surface:
                            new_unit.png_surface = unit.png_surface
                        self.bench[i] = new_unit
                        self.gold -= unit.cost
                        self.shop[shop_index] = None
                        self.check_combinations()
                        return True
        return False

    def sell_unit(self, bench_index):
        if 0 <= bench_index < len(self.bench) and self.bench[bench_index]:
            unit = self.bench[bench_index]
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
            self.bench[bench_index] = None
            return True
        return False

    def sell_board_unit(self, x, y):
        if (0 <= x < GameConstants.BOARD_WIDTH and
                0 <= y < GameConstants.BOARD_HEIGHT and
                self.board[y][x]):

            unit = self.board[y][x]
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
        if (0 <= bench_index < len(self.bench) and self.bench[bench_index] and
                0 <= board_x < GameConstants.BOARD_WIDTH and
                0 <= board_y < GameConstants.BOARD_HEIGHT and
                self.board[board_y][board_x] is None):

            current_units = sum(1 for row in self.board for unit in row if unit is not None)
            if current_units < GameConstants.MAX_BOARD_UNITS[self.level - 1]:
                self.board[board_y][board_x] = self.bench[bench_index]
                self.bench[bench_index] = None
                self.calculate_traits()
                self.check_combinations()  # <--- ADD THIS LINE
                return True
        return False

    def move_unit_to_bench(self, board_x, board_y, bench_index):
        if (0 <= bench_index < len(self.bench) and self.bench[bench_index] is None and
                0 <= board_x < GameConstants.BOARD_WIDTH and
                0 <= board_y < GameConstants.BOARD_HEIGHT and
                self.board[board_y][board_x] is not None):
            self.bench[bench_index] = self.board[board_y][board_x]
            self.board[board_y][board_x] = None
            self.calculate_traits()
            self.check_combinations()  # <--- ADD THIS LINE
            return True
        return False

    def check_combinations(self):
        """Check for unit combinations across bench and board (repeat until no more possible)"""
        while True:
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

            found = False
            for (name, stars), units in unit_counts.items():
                if len(units) >= 3 and stars < 3:
                    base_unit_info = units[0]
                    units_to_remove = units[1:3]

                    if base_unit_info[0] == 'bench':
                        base_unit = base_unit_info[1]
                    else:
                        base_unit = base_unit_info[1]

                    for unit_info in units_to_remove:
                        if unit_info[0] == 'bench':
                            unit_to_combine = unit_info[1]
                            for i, bench_unit in enumerate(self.bench):
                                if bench_unit == unit_to_combine:
                                    self.bench[i] = None
                                    break
                        else:
                            unit_to_combine = unit_info[1]
                            x, y = unit_info[2]
                            self.board[y][x] = None

                        base_unit.combine(unit_to_combine)

                    self.calculate_traits()
                    found = True
                    break  # Need to restart because star count changed
            if not found:
                break

    def calculate_traits(self):
        trait_counts = {}

        for row in self.board:
            for unit in row:
                if unit:
                    for trait in unit.traits:
                        if trait != "N/A":
                            trait_counts[trait] = trait_counts.get(trait, 0) + 1

        self.traits = trait_counts

    def can_combine_anywhere(self, unit_to_check):
        if not unit_to_check:
            return False
        count = 0
        for bench_unit in self.bench:
            if bench_unit and bench_unit.name == unit_to_check.name and bench_unit.stars == unit_to_check.stars:
                count += 1
        for row in self.board:
            for board_unit in row:
                if board_unit and board_unit.name == unit_to_check.name and board_unit.stars == unit_to_check.stars:
                    count += 1
        return count >= 2

    def buy_and_combine(self, shop_index):
        """Buy a unit and automatically combine it with existing matching units"""
        if 0 <= shop_index < len(self.shop) and self.shop[shop_index]:
            unit = self.shop[shop_index]
            if self.gold >= unit.cost:
                units_to_combine = []

                for i, bench_unit in enumerate(self.bench):
                    if bench_unit and bench_unit.name == unit.name and bench_unit.stars == unit.stars:
                        units_to_combine.append(('bench', i, bench_unit))

                for y, row in enumerate(self.board):
                    for x, board_unit in enumerate(row):
                        if board_unit and board_unit.name == unit.name and board_unit.stars == unit.stars:
                            units_to_combine.append(('board', (x, y), board_unit))

                if len(units_to_combine) >= 2:
                    base_unit = units_to_combine[0][2]
                    second_unit = units_to_combine[1][2]

                    base_unit.combine(second_unit)

                    if units_to_combine[1][0] == 'bench':
                        self.bench[units_to_combine[1][1]] = None
                    else:
                        x, y = units_to_combine[1][1]
                        self.board[y][x] = None

                    self.gold -= unit.cost
                    self.shop[shop_index] = None
                    self.calculate_traits()
                    return True

                # If no combine, just buy as normal (ensure PNG transfer)
                for i, bench_unit in enumerate(self.bench):
                    if bench_unit is None:
                        new_unit = self.create_unit(unit.name, unit.cost, unit.traits.copy(), unit.health, unit.damage, [])
                        if unit.png_name:
                            new_unit.png_name = unit.png_name
                        if unit.png_surface:
                            new_unit.png_surface = unit.png_surface
                        self.bench[i] = new_unit
                        self.gold -= unit.cost
                        self.shop[shop_index] = None
                        self.check_combinations()
                        return True
        return False