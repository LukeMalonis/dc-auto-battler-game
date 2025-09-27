from enum import Enum

class GameConstants:
    SHOP_SLOTS = 5
    BENCH_SLOTS = 9
    BOARD_WIDTH = 7
    BOARD_HEIGHT = 4
    UNIT_SIZE = 80
    SHOP_UNIT_SIZE = 70
    BENCH_UNIT_SIZE = 60
    MAX_BOARD_UNITS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # Level 1-10

class Colors:
    BACKGROUND = (30, 30, 50)
    BUTTON_NORMAL = (70, 70, 120)
    BUTTON_HOVER = (90, 90, 150)
    BUTTON_TEXT = (255, 255, 255)
    TITLE_COLOR = (255, 215, 0)
    GOLD_COLOR = (255, 215, 0)
    SHOP_BG = (50, 50, 80)
    BENCH_BG = (60, 60, 90)
    BOARD_BG = (40, 40, 70)
    UNIT_BG = (80, 80, 120)
    TRAIT_BG = (90, 60, 120)
    INFO_BG = (60, 80, 100)
    DRAG_HIGHLIGHT = (255, 255, 255, 100)

class GameState(Enum):
    MAIN_MENU = 0
    PLAY_MENU = 1
    OPTIONS_SCREEN = 2
    SINGLE_PLAYER = 3
    MULTIPLAYER_SCREEN = 4

class DragState(Enum):
    NONE = 0
    FROM_BENCH = 1
    FROM_BOARD = 2
    FROM_SHOP = 3