import pygame
import math


class HexBoard:
    def __init__(self, screen_width, screen_height, is_player_board=True):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.is_player_board = is_player_board
        self.hex_size = 35
        self.rows = 4
        self.cols = 7

        # Colors
        self.hex_color = (50, 50, 80) if is_player_board else (80, 50, 50)
        self.border_color = (100, 150, 255) if is_player_board else (255, 150, 100)

        self.calculate_board_position()

    def calculate_board_position(self):
        hex_width = self.hex_size * math.sqrt(3)
        hex_height = self.hex_size * 2

        total_width = (self.cols + 0.5) * hex_width
        total_height = (self.rows * 0.75 + 0.25) * hex_height

        if self.is_player_board:
            # Player board at normal position
            self.board_x = (self.screen_width - total_width) // 2
            self.board_y = self.screen_height - total_height - 200
        else:
            # Opponent board at top
            self.board_x = (self.screen_width - total_width) // 2
            self.board_y = 50

    def get_hex_center(self, row, col):
        hex_width = self.hex_size * math.sqrt(3)
        hex_height = self.hex_size * 2

        # TFT-style zigzag: even rows offset right
        x_offset = hex_width / 2 if row % 2 == 0 else 0

        x = self.board_x + col * hex_width + x_offset
        y = self.board_y + row * hex_height * 0.75

        return (x, y)

    def get_hex_corners(self, center_x, center_y):
        corners = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.pi / 180 * angle_deg
            x = center_x + self.hex_size * math.cos(angle_rad)
            y = center_y + self.hex_size * math.sin(angle_rad)
            corners.append((x, y))
        return corners

    def draw(self, screen, board_units):
        # Draw hexes and units
        for row in range(self.rows):
            for col in range(self.cols):
                center_x, center_y = self.get_hex_center(row, col)

                # Draw hex
                corners = self.get_hex_corners(center_x, center_y)
                pygame.draw.polygon(screen, self.hex_color, corners)
                pygame.draw.polygon(screen, self.border_color, corners, 2)

                # Draw unit if present
                if (row < len(board_units) and col < len(board_units[row]) and
                        board_units[row][col] is not None):
                    unit = board_units[row][col]
                    self.draw_unit(screen, unit, center_x, center_y)

    def draw_unit(self, screen, unit, center_x, center_y):
        # Draw unit circle
        unit_color = self.get_unit_color(unit.cost)
        pygame.draw.circle(screen, unit_color, (int(center_x), int(center_y)), 18)

        # Draw unit name letter
        font = pygame.font.SysFont('arial', 12, bold=True)
        letter = font.render(unit.name[0], True, (255, 255, 255))
        text_rect = letter.get_rect(center=(int(center_x), int(center_y)))
        screen.blit(letter, text_rect)

    def get_unit_color(self, cost):
        colors = {
            1: (200, 200, 200),  # Gray
            2: (100, 200, 100),  # Green
            3: (100, 150, 255),  # Blue
            4: (200, 100, 255),  # Purple
            5: (255, 200, 100)  # Gold
        }
        return colors.get(cost, (200, 200, 200))