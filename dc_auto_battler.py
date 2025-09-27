import pygame
import sys
import json
import os
import random

# Import game modules
from game_constants import GameConstants, Colors, GameState, DragState
from display_manager import DisplayManager
from unit import Unit
from player import Player
from ui_elements import Button

# Initialize Pygame
pygame.init()

# Configuration
CONFIG_FILE = "game_config.json"


def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            return {
                "resolution": [1920, 1080],
                "fullscreen": False,
                "borderless": False,
                "music_volume": 0.7,
                "sfx_volume": 0.8
            }
    else:
        with open(CONFIG_FILE, 'w') as f:
            default_config = {
                "resolution": [1920, 1080],
                "fullscreen": False,
                "borderless": False,
                "music_volume": 0.7,
                "sfx_volume": 0.8
            }
            json.dump(default_config, f, indent=4)
        return default_config


def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)


# Larger sizes for better readability and future PNG art
LARGE_UNIT_SIZE = 120
LARGE_SHOP_UNIT_SIZE = 140  # Made shop units even bigger for easier clicking
LARGE_BENCH_UNIT_SIZE = 100

# Define trait thresholds and descriptions
TRAIT_INFO = {
    "Hero": {
        "thresholds": [2, 4, 6],
        "description": "Heroes gain bonus damage and health when grouped together",
        "units": ["Batman", "Robin", "Wonder Woman", "Green Lantern", "Flash", "Nightwing", "Superman", "Aquaman"]
    },
    "Villain": {
        "thresholds": [2, 4, 6],
        "description": "Villains deal extra damage to Heroes and spread chaos effects",
        "units": ["Harley Quinn", "Joker", "Catwoman", "Bane", "Darkseid"]
    },
    "Tech": {
        "thresholds": [2, 3, 4],
        "description": "Tech units gain shields and bonus abilities from gadgets",
        "units": ["Batman"]
    },
    "Acrobat": {
        "thresholds": [2, 4],
        "description": "Acrobats dodge attacks and gain movement speed bonuses",
        "units": ["Harley Quinn", "Robin", "Catwoman", "Nightwing"]
    },
    "Chaos": {
        "thresholds": [1, 3, 5],
        "description": "Chaos units randomly buff allies or debuff enemies each round",
        "units": ["Joker"]
    },
    "Atlantean": {
        "thresholds": [1, 3, 5],
        "description": "Atlantean units control water and gain massive health bonuses",
        "units": ["Aquaman"]
    },
    "Amazon": {
        "thresholds": [1, 3, 5],
        "description": "Amazon warriors gain attack speed and critical strike chance",
        "units": ["Wonder Woman"]
    },
    "Corps": {
        "thresholds": [1, 3, 5],
        "description": "Green Lantern Corps members create protective constructs",
        "units": ["Green Lantern"]
    },
    "Brute": {
        "thresholds": [1, 3, 5],
        "description": "Brutes gain damage based on missing health and become unstoppable",
        "units": ["Bane"]
    },
    "Speedster": {
        "thresholds": [1, 3, 5],
        "description": "Speedsters attack multiple times per turn and dodge everything",
        "units": ["Flash"]
    },
    "Alien": {
        "thresholds": [1, 2, 3],
        "description": "Alien units have unique powerful abilities that scale with level",
        "units": ["Superman", "Darkseid"]
    }
}


def get_trait_display(trait_name, current_count):
    """Get the display string showing current count and next threshold"""
    if trait_name not in TRAIT_INFO:
        return f"{trait_name} ({current_count})"

    thresholds = TRAIT_INFO[trait_name]["thresholds"]

    # Find the next threshold
    next_threshold = None
    for threshold in thresholds:
        if current_count < threshold:
            next_threshold = threshold
            break

    if next_threshold is None:
        # Already at max, show current count
        return f"{trait_name} ({current_count})"
    else:
        # Show current/next threshold
        return f"{trait_name} ({current_count}/{next_threshold})"


def get_trait_full_info(trait_name):
    """Get the full threshold info for tooltips"""
    if trait_name not in TRAIT_INFO:
        return ""

    thresholds = TRAIT_INFO[trait_name]["thresholds"]
    return "/".join(map(str, thresholds))


def draw_trait_tooltip(surface, trait_name, mouse_pos, screen_width, screen_height):
    """Draw tooltip for trait on hover"""
    if trait_name not in TRAIT_INFO:
        return

    info = TRAIT_INFO[trait_name]
    font_title = pygame.font.SysFont('arial', 16, bold=True)
    font_desc = pygame.font.SysFont('arial', 12)
    font_units = pygame.font.SysFont('arial', 11)
    font_thresholds = pygame.font.SysFont('arial', 12, bold=True)

    # Prepare text
    title_text = font_title.render(trait_name, True, Colors.BUTTON_TEXT)
    thresholds_text = font_thresholds.render(f"Thresholds: {get_trait_full_info(trait_name)}", True, Colors.GOLD_COLOR)
    desc_text = font_desc.render(info["description"], True, Colors.BUTTON_TEXT)
    units_text = font_units.render(f"Units: {', '.join(info['units'][:4])}...", True, (200, 200, 200))

    # Calculate tooltip size
    tooltip_width = max(title_text.get_width(), thresholds_text.get_width(), desc_text.get_width(),
                        units_text.get_width()) + 20
    tooltip_height = 85

    # Position tooltip (avoid going off screen)
    tooltip_x = mouse_pos[0] + 15
    tooltip_y = mouse_pos[1] - 10

    if tooltip_x + tooltip_width > screen_width:
        tooltip_x = mouse_pos[0] - tooltip_width - 15
    if tooltip_y + tooltip_height > screen_height:
        tooltip_y = mouse_pos[1] - tooltip_height - 10

    # Draw tooltip background
    tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
    pygame.draw.rect(surface, (60, 60, 80), tooltip_rect, border_radius=8)
    pygame.draw.rect(surface, Colors.BUTTON_TEXT, tooltip_rect, 2, border_radius=8)

    # Draw text
    surface.blit(title_text, (tooltip_x + 10, tooltip_y + 8))
    surface.blit(thresholds_text, (tooltip_x + 10, tooltip_y + 28))
    surface.blit(desc_text, (tooltip_x + 10, tooltip_y + 48))
    surface.blit(units_text, (tooltip_x + 10, tooltip_y + 65))


def get_unit_border_color(cost):
    """Return border color based on unit cost"""
    if cost == 1:
        return (150, 150, 150)  # Gray
    elif cost == 2:
        return (0, 200, 0)  # Green
    elif cost == 3:
        return (0, 100, 255)  # Blue
    elif cost == 4:
        return (180, 0, 255)  # Purple
    elif cost == 5:
        return (255, 215, 0)  # Gold
    else:
        return Colors.BUTTON_TEXT  # Default


def draw_unit_card(surface, unit, rect, show_details=False, is_shop_unit=False):
    """Draw a unit card with proper borders and information, optimized for PNGs"""
    if not unit:
        return

    # Draw card background with cost-based border
    border_color = get_unit_border_color(unit.cost)
    pygame.draw.rect(surface, Colors.UNIT_BG, rect, border_radius=8)
    pygame.draw.rect(surface, border_color, rect, 3, border_radius=8)

    # PNG placeholder takes up entire card area (minus border)
    image_area = pygame.Rect(rect.x + 3, rect.y + 3, rect.width - 6, rect.height - 6)
    pygame.draw.rect(surface, (40, 40, 40), image_area, border_radius=6)

    # Font sizes based on card size
    if is_shop_unit:
        font_large = pygame.font.SysFont('arial', 16, bold=True)
        font_medium = pygame.font.SysFont('arial', 14, bold=True)
        font_small = pygame.font.SysFont('arial', 11)
    else:
        font_large = pygame.font.SysFont('arial', 14, bold=True)
        font_medium = pygame.font.SysFont('arial', 12, bold=True)
        font_small = pygame.font.SysFont('arial', 10)

    # Draw unit name at the bottom (on top of PNG)
    name_text = font_large.render(unit.name, True, Colors.BUTTON_TEXT)
    # Add black outline for readability over PNG
    name_outline = font_large.render(unit.name, True, (0, 0, 0))
    name_rect = name_text.get_rect(centerx=rect.centerx, bottom=rect.bottom - 8)
    # Draw outline
    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
        surface.blit(name_outline, (name_rect.x + dx, name_rect.y + dy))
    surface.blit(name_text, name_rect)

    # Draw cost in top-right corner (on top of PNG)
    cost_text = font_large.render(f"{unit.cost}g", True, Colors.GOLD_COLOR)
    cost_outline = font_large.render(f"{unit.cost}g", True, (0, 0, 0))
    cost_rect = cost_text.get_rect(topright=(rect.right - 8, rect.y + 8))
    # Draw outline
    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
        surface.blit(cost_outline, (cost_rect.x + dx, cost_rect.y + dy))
    surface.blit(cost_text, cost_rect)

    # Draw stars in top-left corner (on top of PNG) - much more visible
    if unit.stars == 1:
        star_color = (200, 200, 200)  # Gray for 1 star
        star_bg = (100, 100, 100)
    elif unit.stars == 2:
        star_color = (255, 215, 0)  # Gold for 2 star
        star_bg = (150, 100, 0)
    else:  # 3 star
        star_color = (255, 100, 255)  # Purple/Pink for 3 star
        star_bg = (150, 0, 150)

    # Create a background circle for the star
    star_center = (rect.x + 20, rect.y + 20)
    pygame.draw.circle(surface, star_bg, star_center, 15)
    pygame.draw.circle(surface, star_color, star_center, 15, 2)

    star_text = font_medium.render(str(unit.stars), True, star_color)
    star_rect = star_text.get_rect(center=star_center)
    surface.blit(star_text, star_rect)

    # Draw traits on the left side of the card (on top of PNG)
    if show_details and is_shop_unit:
        trait_x = rect.x + 8
        trait_y = rect.y + 45  # Start below the star circle
        for i, trait in enumerate(unit.traits[:3]):  # Show up to 3 traits
            trait_text = font_small.render(trait, True, Colors.BUTTON_TEXT)
            trait_outline = font_small.render(trait, True, (0, 0, 0))
            trait_pos = (trait_x, trait_y + i * 14)
            # Draw outline for readability over PNG
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                surface.blit(trait_outline, (trait_pos[0] + dx, trait_pos[1] + dy))
            surface.blit(trait_text, trait_pos)


# Drawing functions
def draw_main_menu(screen, buttons, mouse_pos, fonts, screen_width, screen_height):
    screen.fill(Colors.BACKGROUND)

    title_text = fonts['title'].render("DC AUTO BATTLE", True, Colors.TITLE_COLOR)
    title_rect = title_text.get_rect(center=(screen_width // 2, screen_height // 4))
    screen.blit(title_text, title_rect)

    for button in buttons:
        button.check_hover(mouse_pos)
        button.draw(screen)


def draw_play_menu(screen, buttons, back_button, mouse_pos, fonts, screen_width, screen_height):
    screen.fill(Colors.BACKGROUND)

    back_button.check_hover(mouse_pos)
    back_button.draw(screen)

    title_text = fonts['title'].render("SELECT MODE", True, Colors.TITLE_COLOR)
    title_rect = title_text.get_rect(center=(screen_width // 2, screen_height // 4))
    screen.blit(title_text, title_rect)

    for button in buttons:
        button.check_hover(mouse_pos)
        button.draw(screen)


def draw_options_menu(screen, buttons, back_button, mouse_pos, fonts, screen_width, screen_height, display_manager):
    screen.fill(Colors.BACKGROUND)

    back_button.check_hover(mouse_pos)
    back_button.draw(screen)

    title_text = fonts['title'].render("DISPLAY SETTINGS", True, Colors.TITLE_COLOR)
    title_rect = title_text.get_rect(center=(screen_width // 2, screen_height // 6))
    screen.blit(title_text, title_rect)

    res_text = fonts['button'].render(f"Current: {display_manager.get_current_resolution_name()}", True,
                                      Colors.BUTTON_TEXT)
    res_rect = res_text.get_rect(center=(screen_width // 2, screen_height // 3))
    screen.blit(res_text, res_rect)

    for button in buttons:
        button.check_hover(mouse_pos)
        button.draw(screen)


def draw_coming_soon(screen, back_button, mouse_pos, screen_name, fonts, screen_width, screen_height):
    screen.fill(Colors.BACKGROUND)

    back_button.check_hover(mouse_pos)
    back_button.draw(screen)

    message_text = fonts['title'].render(f"{screen_name} - Coming Soon!", True, Colors.BUTTON_TEXT)
    message_rect = message_text.get_rect(center=(screen_width // 2, screen_height // 2))
    screen.blit(message_text, message_rect)


def draw_sell_zone(screen, screen_width, screen_height, is_highlighted):
    """Draw the sell zone at the bottom of the screen"""
    sell_zone_height = 60
    sell_zone = pygame.Rect(0, screen_height - sell_zone_height, screen_width, sell_zone_height)

    # Red background that pulses when highlighted
    red_intensity = 200 if is_highlighted else 100
    pygame.draw.rect(screen, (red_intensity, 50, 50), sell_zone)
    pygame.draw.rect(screen, (255, 100, 100), sell_zone, 3)

    # Sell text
    font = pygame.font.SysFont('arial', 24, bold=True)
    sell_text = font.render("DRAG UNIT HERE TO SELL", True, (255, 255, 255))
    text_rect = sell_text.get_rect(center=(screen_width // 2, screen_height - sell_zone_height // 2))
    screen.blit(sell_text, text_rect)

    return sell_zone


def draw_single_player_game(screen, player, buttons, mouse_pos, fonts, screen_width, screen_height, drag_state,
                            drag_unit, drag_pos, drag_source_type):
    screen.fill(Colors.BACKGROUND)

    # Draw sell zone ONLY when dragging a unit (but not from shop)
    is_dragging_to_sell = (drag_state != DragState.NONE and
                           drag_source_type != 'shop' and
                           mouse_pos[1] > screen_height - 100)

    if drag_state != DragState.NONE and drag_source_type != 'shop':
        draw_sell_zone(screen, screen_width, screen_height, is_dragging_to_sell)

    # Draw game layout
    draw_board(screen, player, screen_width, screen_height, drag_state, drag_unit, drag_pos, mouse_pos)
    draw_bench(screen, player, screen_width, screen_height, drag_state, drag_unit, drag_pos, mouse_pos)
    draw_shop(screen, player, screen_width, screen_height, drag_state, drag_source_type, mouse_pos)
    draw_ui_elements(screen, player, buttons, mouse_pos, fonts, screen_width, screen_height)
    draw_traits_panel(screen, player, screen_width, screen_height, fonts, mouse_pos)
    draw_info_panel(screen, player, screen_width, screen_height, fonts)

    # Draw drag unit if dragging
    if drag_state != DragState.NONE and drag_unit:
        unit_rect = pygame.Rect(drag_pos[0] - LARGE_UNIT_SIZE // 2,
                                drag_pos[1] - LARGE_UNIT_SIZE // 2,
                                LARGE_UNIT_SIZE, LARGE_UNIT_SIZE)

        # Special visual for shop drag (green semi-transparent with BUY text)
        if drag_source_type == 'shop':
            unit_surface = pygame.Surface((LARGE_UNIT_SIZE, LARGE_UNIT_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(unit_surface, (100, 200, 100, 180), unit_surface.get_rect(), border_radius=8)
            pygame.draw.rect(unit_surface, (200, 255, 200, 200), unit_surface.get_rect(), 3, border_radius=8)
            screen.blit(unit_surface, unit_rect)

            # Add "BUY?" text
            font = pygame.font.SysFont('arial', 16, bold=True)
            buy_text = font.render("BUY?", True, (255, 255, 255))
            buy_rect = buy_text.get_rect(center=unit_rect.center)
            screen.blit(buy_text, buy_rect)
        else:
            # Normal drag visuals for bench/board
            if is_dragging_to_sell:
                unit_surface = pygame.Surface((LARGE_UNIT_SIZE, LARGE_UNIT_SIZE), pygame.SRCALPHA)
                pygame.draw.rect(unit_surface, (255, 100, 100, 200), unit_surface.get_rect(), border_radius=8)
                pygame.draw.rect(unit_surface, (255, 200, 200, 200), unit_surface.get_rect(), 3, border_radius=8)
                screen.blit(unit_surface, unit_rect)
            else:
                draw_unit_card(screen, drag_unit, unit_rect, show_details=True)


def draw_board(screen, player, screen_width, screen_height, drag_state, drag_unit, drag_pos, mouse_pos):
    board_width = GameConstants.BOARD_WIDTH * LARGE_UNIT_SIZE
    board_height = GameConstants.BOARD_HEIGHT * LARGE_UNIT_SIZE
    board_x = (screen_width - board_width) // 2
    board_y = screen_height // 6  # Moved up to accommodate larger units

    pygame.draw.rect(screen, Colors.BOARD_BG, (board_x - 10, board_y - 10,
                                               board_width + 20, board_height + 20), border_radius=10)

    for y in range(GameConstants.BOARD_HEIGHT):
        for x in range(GameConstants.BOARD_WIDTH):
            rect = pygame.Rect(board_x + x * LARGE_UNIT_SIZE,
                               board_y + y * LARGE_UNIT_SIZE,
                               LARGE_UNIT_SIZE - 4, LARGE_UNIT_SIZE - 4)

            # Highlight if mouse is over and we can drop here
            can_drop_here = (player.board[y][x] is None or
                             (drag_state != DragState.NONE and drag_unit != player.board[y][x]))

            is_highlighted = (drag_state != DragState.NONE and
                              rect.collidepoint(mouse_pos) and
                              can_drop_here)

            # Draw board slot
            slot_color = Colors.BUTTON_HOVER if is_highlighted else Colors.UNIT_BG
            pygame.draw.rect(screen, slot_color, rect, border_radius=8)
            pygame.draw.rect(screen, Colors.BUTTON_TEXT, rect, 1, border_radius=8)

            # Draw unit if present
            if player.board[y][x]:
                unit = player.board[y][x]
                draw_unit_card(screen, unit, rect)


def draw_bench(screen, player, screen_width, screen_height, drag_state, drag_unit, drag_pos, mouse_pos):
    bench_width = GameConstants.BENCH_SLOTS * LARGE_BENCH_UNIT_SIZE
    bench_x = (screen_width - bench_width) // 2
    bench_y = screen_height - 320  # Adjusted for larger shop units

    pygame.draw.rect(screen, Colors.BENCH_BG, (bench_x - 10, bench_y - 10,
                                               bench_width + 20, LARGE_BENCH_UNIT_SIZE + 20), border_radius=8)

    for i in range(GameConstants.BENCH_SLOTS):
        rect = pygame.Rect(bench_x + i * LARGE_BENCH_UNIT_SIZE, bench_y,
                           LARGE_BENCH_UNIT_SIZE - 4, LARGE_BENCH_UNIT_SIZE - 4)

        # Highlight if mouse is over and we can drop here (empty slot or different unit)
        can_drop_here = (player.bench[i] is None or
                         (drag_state != DragState.NONE and drag_unit != player.bench[i]))

        is_highlighted = (drag_state != DragState.NONE and
                          rect.collidepoint(mouse_pos) and
                          can_drop_here)

        # Draw bench slot
        slot_color = Colors.BUTTON_HOVER if is_highlighted else Colors.UNIT_BG
        pygame.draw.rect(screen, slot_color, rect, border_radius=6)
        pygame.draw.rect(screen, Colors.BUTTON_TEXT, rect, 1, border_radius=6)

        # Draw unit if present
        if i < len(player.bench) and player.bench[i]:
            unit = player.bench[i]
            draw_unit_card(screen, unit, rect)


def draw_shop(screen, player, screen_width, screen_height, drag_state, drag_source_type, mouse_pos):
    shop_width = GameConstants.SHOP_SLOTS * LARGE_SHOP_UNIT_SIZE
    shop_x = (screen_width - shop_width) // 2
    shop_y = screen_height - 180  # Adjusted for larger shop units

    # Larger shop background
    pygame.draw.rect(screen, Colors.SHOP_BG, (shop_x - 15, shop_y - 15,
                                              shop_width + 30, LARGE_SHOP_UNIT_SIZE + 30), border_radius=10)

    for i in range(GameConstants.SHOP_SLOTS):
        rect = pygame.Rect(shop_x + i * LARGE_SHOP_UNIT_SIZE, shop_y,
                           LARGE_SHOP_UNIT_SIZE - 6, LARGE_SHOP_UNIT_SIZE - 6)

        # Highlight shop slots when hovering (not dragging from shop)
        is_highlighted = (drag_state == DragState.NONE and
                          rect.collidepoint(mouse_pos) and
                          player.shop[i] is not None)

        # Draw shop slot
        slot_color = Colors.BUTTON_HOVER if is_highlighted else Colors.UNIT_BG
        pygame.draw.rect(screen, slot_color, rect, border_radius=8)
        pygame.draw.rect(screen, Colors.BUTTON_TEXT, rect, 2, border_radius=8)

        # Draw shop unit if present
        if i < len(player.shop) and player.shop[i]:
            unit = player.shop[i]
            draw_unit_card(screen, unit, rect, show_details=True, is_shop_unit=True)


def draw_ui_elements(screen, player, buttons, mouse_pos, fonts, screen_width, screen_height):
    # Use smaller font for top info
    font_small = pygame.font.SysFont('arial', 16)

    gold_text = font_small.render(f"Gold: {player.gold}", True, Colors.GOLD_COLOR)
    screen.blit(gold_text, (screen_width - 140, 20))

    level_text = font_small.render(f"Level: {player.level}", True, Colors.BUTTON_TEXT)
    screen.blit(level_text, (screen_width - 140, 45))

    xp_text = font_small.render(
        f"XP: {player.xp}/{player.xp_to_level[player.level - 1] if player.level < 9 else 'MAX'}", True,
        Colors.BUTTON_TEXT)
    screen.blit(xp_text, (screen_width - 140, 70))

    round_text = font_small.render(f"Round: {player.round}", True, Colors.BUTTON_TEXT)
    screen.blit(round_text, (screen_width - 140, 95))

    # Smaller buttons with appropriate text
    button_font = pygame.font.SysFont('arial', 14)

    buy_xp_button = Button(30, screen_height - 60, 100, 35, "Buy XP (F)", button_font)
    reroll_button = Button(140, screen_height - 60, 100, 35, "Reroll (D)", button_font)

    for button in [buy_xp_button, reroll_button]:
        button.check_hover(mouse_pos)
        button.draw(screen)

    # Draw other buttons (end turn, back)
    for button in buttons:
        button.check_hover(mouse_pos)
        button.draw(screen)


def draw_traits_panel(screen, player, screen_width, screen_height, fonts, mouse_pos):
    panel_width = 260
    panel_x = 15
    panel_y = 120
    panel_height = 240

    pygame.draw.rect(screen, Colors.TRAIT_BG, (panel_x, panel_y, panel_width, panel_height), border_radius=8)

    # Larger font for title
    font_title = pygame.font.SysFont('arial', 18, bold=True)
    trait_title = font_title.render("Active Traits", True, Colors.BUTTON_TEXT)
    screen.blit(trait_title, (panel_x + 15, panel_y + 12))

    # Larger font for traits
    font_trait = pygame.font.SysFont('arial', 16)
    y_offset = 50
    hovered_trait = None

    if player.traits:
        for trait, count in player.traits.items():
            trait_rect = pygame.Rect(panel_x + 15, panel_y + y_offset, panel_width - 30, 30)

            # Check if mouse is hovering over this trait
            if trait_rect.collidepoint(mouse_pos):
                hovered_trait = trait
                # Highlight the trait when hovering
                pygame.draw.rect(screen, (100, 100, 140), trait_rect, border_radius=6)

            trait_display = get_trait_display(trait, count)
            trait_text = font_trait.render(trait_display, True, Colors.BUTTON_TEXT)
            screen.blit(trait_text, (panel_x + 20, panel_y + y_offset + 6))
            y_offset += 35
    else:
        no_traits = font_trait.render("No active traits", True, Colors.BUTTON_TEXT)
        screen.blit(no_traits, (panel_x + 20, panel_y + 55))

    # Draw tooltip if hovering over a trait
    if hovered_trait:
        draw_trait_tooltip(screen, hovered_trait, mouse_pos, screen_width, screen_height)


def draw_info_panel(screen, player, screen_width, screen_height, fonts):
    panel_width = 250
    panel_x = screen_width - panel_width - 15
    panel_y = 120
    panel_height = 180

    pygame.draw.rect(screen, Colors.INFO_BG, (panel_x, panel_y, panel_width, panel_height), border_radius=8)

    # Larger font for title
    font_title = pygame.font.SysFont('arial', 18, bold=True)
    info_title = font_title.render("Game Info", True, Colors.BUTTON_TEXT)
    screen.blit(info_title, (panel_x + 15, panel_y + 12))

    # Larger font for info
    font_info = pygame.font.SysFont('arial', 16)

    income = player.calculate_income()
    board_units = sum(1 for row in player.board for unit in row if unit is not None)
    max_units = GameConstants.MAX_BOARD_UNITS[player.level - 1]
    bench_units = sum(1 for u in player.bench if u is not None)

    info_lines = [
        f"Income: +{income}g",
        f"Board: {board_units}/{max_units}",
        f"Bench: {bench_units}/9",
        f"Level: {player.level}",
        f"Round: {player.round}"
    ]

    y_offset = 50
    for line in info_lines:
        info_text = font_info.render(line, True, Colors.BUTTON_TEXT)
        screen.blit(info_text, (panel_x + 20, panel_y + y_offset))
        y_offset += 32


def main():
    display_manager = DisplayManager()
    clock = pygame.time.Clock()
    game_state = GameState.MAIN_MENU

    # Initialize player for single player game
    player = Player()

    # Drag state
    drag_state = DragState.NONE
    drag_unit = None
    drag_pos = (0, 0)
    drag_source_index = None
    drag_source_type = None  # 'bench', 'board', or 'shop'
    drag_start_pos = (0, 0)  # Track where drag started
    click_threshold = 5  # Minimum pixels to consider it a drag vs click

    # Initial UI setup with larger fonts
    screen_width, screen_height = display_manager.current_resolution
    base_size = screen_height / 15
    fonts = {
        'title': pygame.font.SysFont('arial', int(base_size * 1.6), bold=True),
        'button': pygame.font.SysFont('arial', int(base_size * 0.8))
    }

    # Create menu buttons with smaller menu font
    menu_font = pygame.font.SysFont('arial', int(base_size * 0.6))
    center_x, center_y = screen_width // 2, screen_height // 2

    # Main menu buttons
    play_button = Button(center_x - 100, center_y - 50, 200, 60, "PLAY", menu_font)
    options_button = Button(center_x - 100, center_y + 30, 200, 60, "OPTIONS", menu_font)
    quit_button = Button(center_x - 100, center_y + 110, 200, 60, "QUIT", menu_font)
    main_menu_buttons = [play_button, options_button, quit_button]

    # Play menu buttons
    single_player_button = Button(center_x - 150, center_y - 50, 300, 60, "SINGLE PLAYER", menu_font)
    multiplayer_button = Button(center_x - 150, center_y + 30, 300, 60, "MULTIPLAYER", menu_font)
    play_menu_buttons = [single_player_button, multiplayer_button]

    # Options menu buttons
    resolution_button = Button(center_x - 150, center_y - 50, 300, 60, "CHANGE RESOLUTION", menu_font)
    fullscreen_button = Button(center_x - 150, center_y + 30, 300, 60, "TOGGLE FULLSCREEN", menu_font)
    borderless_button = Button(center_x - 150, center_y + 110, 300, 60, "TOGGLE BORDERLESS", menu_font)
    options_buttons = [resolution_button, fullscreen_button, borderless_button]

    # Smaller back and end turn buttons
    back_button = Button(30, 30, 80, 30, "BACK", menu_font)
    end_turn_button = Button(screen_width // 2 - 50, 15, 100, 30, "End Turn", menu_font)
    game_buttons = [end_turn_button, back_button]

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        mouse_released = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_clicked = True
                    drag_start_pos = mouse_pos
                    # Start dragging
                    if game_state == GameState.SINGLE_PLAYER:
                        # Check bench for drag start
                        bench_width = GameConstants.BENCH_SLOTS * LARGE_BENCH_UNIT_SIZE
                        bench_x = (screen_width - bench_width) // 2
                        bench_y = screen_height - 320

                        for i in range(GameConstants.BENCH_SLOTS):
                            bench_rect = pygame.Rect(bench_x + i * LARGE_BENCH_UNIT_SIZE, bench_y,
                                                     LARGE_BENCH_UNIT_SIZE - 4, LARGE_BENCH_UNIT_SIZE - 4)
                            if bench_rect.collidepoint(mouse_pos) and player.bench[i]:
                                drag_state = DragState.FROM_BENCH
                                drag_unit = player.bench[i]
                                drag_source_index = i
                                drag_source_type = 'bench'
                                break

                        # Check board for drag start
                        if drag_state == DragState.NONE:
                            board_width = GameConstants.BOARD_WIDTH * LARGE_UNIT_SIZE
                            board_x = (screen_width - board_width) // 2
                            board_y = screen_height // 6

                            for y in range(GameConstants.BOARD_HEIGHT):
                                for x in range(GameConstants.BOARD_WIDTH):
                                    board_rect = pygame.Rect(board_x + x * LARGE_UNIT_SIZE,
                                                             board_y + y * LARGE_UNIT_SIZE,
                                                             LARGE_UNIT_SIZE - 4, LARGE_UNIT_SIZE - 4)
                                    if board_rect.collidepoint(mouse_pos) and player.board[y][x]:
                                        drag_state = DragState.FROM_BOARD
                                        drag_unit = player.board[y][x]
                                        drag_source_index = (x, y)
                                        drag_source_type = 'board'
                                        break
                                if drag_state != DragState.NONE:
                                    break

                        # Check shop for drag start (AFTER bench/board checks)
                        if drag_state == DragState.NONE:
                            shop_width = GameConstants.SHOP_SLOTS * LARGE_SHOP_UNIT_SIZE
                            shop_x = (screen_width - shop_width) // 2
                            shop_y = screen_height - 180

                            for i in range(GameConstants.SHOP_SLOTS):
                                shop_rect = pygame.Rect(shop_x + i * LARGE_SHOP_UNIT_SIZE, shop_y,
                                                        LARGE_SHOP_UNIT_SIZE - 6, LARGE_SHOP_UNIT_SIZE - 6)
                                if shop_rect.collidepoint(mouse_pos) and player.shop[i] is not None:
                                    drag_state = DragState.FROM_SHOP
                                    drag_unit = player.shop[i]
                                    drag_source_index = i
                                    drag_source_type = 'shop'
                                    break

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and drag_state != DragState.NONE:
                    mouse_released = True

                    # Calculate how far the mouse moved from start
                    drag_distance = ((mouse_pos[0] - drag_start_pos[0]) ** 2 +
                                    (mouse_pos[1] - drag_start_pos[1]) ** 2) ** 0.5

                    # Handle shop interactions - distinguish between click and drag
                    if drag_source_type == 'shop':
                        if drag_distance < click_threshold:
                            # This was a click, not a drag - purchase the unit
                            unit_to_buy = player.shop[drag_source_index]
                            if unit_to_buy and player.gold >= unit_to_buy.cost:
                                if player.can_combine_anywhere(unit_to_buy):
                                    player.buy_and_combine(drag_source_index)
                                else:
                                    player.buy_unit(drag_source_index)
                        else:
                            # This was a drag - only purchase if dragged outside shop area
                            shop_width = GameConstants.SHOP_SLOTS * LARGE_SHOP_UNIT_SIZE
                            shop_x = (screen_width - shop_width) // 2
                            shop_y = screen_height - 180

                            # Check if mouse is outside shop area (actually dragged away)
                            shop_area = pygame.Rect(shop_x - 15, shop_y - 15, shop_width + 30,
                                                    LARGE_SHOP_UNIT_SIZE + 30)
                            if not shop_area.collidepoint(mouse_pos):
                                # Try to purchase the unit
                                if player.can_combine_anywhere(drag_unit):
                                    player.buy_and_combine(drag_source_index)
                                else:
                                    player.buy_unit(drag_source_index)

                    # Check if dropped in sell zone (bottom of screen) - only for bench/board units
                    elif drag_source_type != 'shop' and mouse_pos[1] > screen_height - 100:
                        # Sell the unit
                        if drag_source_type == 'bench':
                            player.sell_unit(drag_source_index)
                        elif drag_source_type == 'board':
                            x, y = drag_source_index
                            player.sell_board_unit(x, y)

                    else:
                        # Handle normal drag drop for bench/board units
                        if game_state == GameState.SINGLE_PLAYER and drag_source_type != 'shop':
                            board_width = GameConstants.BOARD_WIDTH * LARGE_UNIT_SIZE
                            board_x = (screen_width - board_width) // 2
                            board_y = screen_height // 6

                            bench_width = GameConstants.BENCH_SLOTS * LARGE_BENCH_UNIT_SIZE
                            bench_x = (screen_width - bench_width) // 2
                            bench_y = screen_height - 320

                            # Check if dropped on board
                            board_dropped = False
                            for y in range(GameConstants.BOARD_HEIGHT):
                                for x in range(GameConstants.BOARD_WIDTH):
                                    board_rect = pygame.Rect(board_x + x * LARGE_UNIT_SIZE,
                                                             board_y + y * LARGE_UNIT_SIZE,
                                                             LARGE_UNIT_SIZE - 4, LARGE_UNIT_SIZE - 4)
                                    if board_rect.collidepoint(mouse_pos):
                                        if drag_source_type == 'bench':
                                            # Move from bench to board (swap if occupied)
                                            target_unit = player.board[y][x]
                                            if target_unit is None:
                                                # Empty spot - just move
                                                if player.move_unit_to_board(drag_source_index, x, y):
                                                    player.bench[drag_source_index] = None
                                            else:
                                                # Swap bench unit with board unit
                                                player.board[y][x] = drag_unit
                                                player.bench[drag_source_index] = target_unit
                                                player.calculate_traits()
                                        elif drag_source_type == 'board':
                                            # Move from board to different board position (swap)
                                            source_x, source_y = drag_source_index
                                            target_unit = player.board[y][x]

                                            # Swap the units
                                            player.board[y][x] = drag_unit
                                            player.board[source_y][source_x] = target_unit
                                            player.calculate_traits()
                                        board_dropped = True
                                        break
                                if board_dropped:
                                    break

                            if not board_dropped:
                                # Check if dropped on bench
                                for i in range(GameConstants.BENCH_SLOTS):
                                    bench_rect = pygame.Rect(bench_x + i * LARGE_BENCH_UNIT_SIZE, bench_y,
                                                             LARGE_BENCH_UNIT_SIZE - 4, LARGE_BENCH_UNIT_SIZE - 4)
                                    if bench_rect.collidepoint(mouse_pos):
                                        if drag_source_type == 'board':
                                            # Move from board to bench (swap if occupied)
                                            x, y = drag_source_index
                                            target_unit = player.bench[i]
                                            if target_unit is None:
                                                # Empty spot - just move
                                                if player.move_unit_to_bench(x, y, i):
                                                    player.board[y][x] = None
                                            else:
                                                # Swap board unit with bench unit
                                                player.bench[i] = drag_unit
                                                player.board[y][x] = target_unit
                                                player.calculate_traits()
                                        elif drag_source_type == 'bench':
                                            # Swap bench positions
                                            source_unit = player.bench[drag_source_index]
                                            target_unit = player.bench[i]
                                            player.bench[i] = source_unit
                                            player.bench[drag_source_index] = target_unit
                                        break

                    # Reset drag state
                    drag_state = DragState.NONE
                    drag_unit = None
                    drag_source_index = None
                    drag_source_type = None
                    drag_start_pos = (0, 0)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_state == GameState.SINGLE_PLAYER:
                        game_state = GameState.PLAY_MENU
                    elif game_state == GameState.PLAY_MENU or game_state == GameState.OPTIONS_SCREEN:
                        game_state = GameState.MAIN_MENU
                elif event.key == pygame.K_f and game_state == GameState.SINGLE_PLAYER:
                    player.buy_xp()
                elif event.key == pygame.K_d and game_state == GameState.SINGLE_PLAYER:
                    player.refresh_shop()
                elif event.key == pygame.K_s and game_state == GameState.SINGLE_PLAYER and drag_state == DragState.NONE:
                    # Sell unit under mouse (bench only for now)
                    bench_width = GameConstants.BENCH_SLOTS * LARGE_BENCH_UNIT_SIZE
                    bench_x = (screen_width - bench_width) // 2
                    bench_y = screen_height - 320

                    for i in range(GameConstants.BENCH_SLOTS):
                        bench_rect = pygame.Rect(bench_x + i * LARGE_BENCH_UNIT_SIZE, bench_y,
                                                 LARGE_BENCH_UNIT_SIZE - 4, LARGE_BENCH_UNIT_SIZE - 4)
                        if bench_rect.collidepoint(mouse_pos) and player.bench[i]:
                            player.sell_unit(i)
                            break

        # Update drag position
        if drag_state != DragState.NONE:
            drag_pos = mouse_pos

        # Handle button clicks (including Buy XP and Reroll buttons)
        if mouse_clicked and drag_state == DragState.NONE:
            if game_state == GameState.MAIN_MENU:
                if play_button.is_clicked(mouse_pos, True):
                    game_state = GameState.PLAY_MENU
                elif options_button.is_clicked(mouse_pos, True):
                    game_state = GameState.OPTIONS_SCREEN
                elif quit_button.is_clicked(mouse_pos, True):
                    running = False

            elif game_state == GameState.PLAY_MENU:
                if single_player_button.is_clicked(mouse_pos, True):
                    game_state = GameState.SINGLE_PLAYER
                    player = Player()  # Reset player for new game
                elif multiplayer_button.is_clicked(mouse_pos, True):
                    game_state = GameState.MULTIPLAYER_SCREEN
                elif back_button.is_clicked(mouse_pos, True):
                    game_state = GameState.MAIN_MENU

            elif game_state == GameState.OPTIONS_SCREEN:
                if resolution_button.is_clicked(mouse_pos, True):
                    new_index = (display_manager.current_res_index + 1) % len(display_manager.resolutions)
                    if display_manager.set_resolution(new_index):
                        screen_width, screen_height = display_manager.current_resolution
                        base_size = screen_height / 15
                        fonts = {
                            'title': pygame.font.SysFont('arial', int(base_size * 1.6), bold=True),
                            'button': pygame.font.SysFont('arial', int(base_size * 0.8))
                        }
                elif fullscreen_button.is_clicked(mouse_pos, True):
                    display_manager.toggle_fullscreen()
                    screen_width, screen_height = display_manager.current_resolution
                elif borderless_button.is_clicked(mouse_pos, True):
                    display_manager.toggle_borderless()
                    screen_width, screen_height = display_manager.current_resolution
                elif back_button.is_clicked(mouse_pos, True):
                    game_state = GameState.MAIN_MENU

            elif game_state == GameState.SINGLE_PLAYER:
                # Check shop clicks (only if not dragging)
                shop_clicked = False
                shop_width = GameConstants.SHOP_SLOTS * LARGE_SHOP_UNIT_SIZE
                shop_x = (screen_width - shop_width) // 2
                shop_y = screen_height - 180

                for i in range(GameConstants.SHOP_SLOTS):
                    shop_rect = pygame.Rect(shop_x + i * LARGE_SHOP_UNIT_SIZE, shop_y,
                                            LARGE_SHOP_UNIT_SIZE - 6, LARGE_SHOP_UNIT_SIZE - 6)
                    if shop_rect.collidepoint(mouse_pos) and player.shop[i] is not None:
                        # Check if this purchase would cause a combination
                        unit_to_buy = player.shop[i]
                        if player.can_combine_anywhere(unit_to_buy):
                            # Auto-combine if possible
                            player.buy_and_combine(i)
                        else:
                            # Normal purchase
                            player.buy_unit(i)
                        shop_clicked = True
                        break

                # Only check buttons if no shop unit was clicked
                if not shop_clicked:
                    # Create temporary buttons for Buy XP and Reroll
                    buy_xp_button = Button(30, screen_height - 60, 100, 35, "Buy XP (F)", fonts['button'])
                    reroll_button = Button(140, screen_height - 60, 100, 35, "Reroll (D)", fonts['button'])

                    if buy_xp_button.is_clicked(mouse_pos, True):
                        player.buy_xp()
                    elif reroll_button.is_clicked(mouse_pos, True):
                        player.refresh_shop()
                    elif end_turn_button.is_clicked(mouse_pos, True):
                        income = player.end_turn()
                        print(f"Round {player.round} started! Received {income} gold.")
                    elif back_button.is_clicked(mouse_pos, True):
                        game_state = GameState.PLAY_MENU

            elif game_state == GameState.MULTIPLAYER_SCREEN:
                if back_button.is_clicked(mouse_pos, True):
                    game_state = GameState.PLAY_MENU

        # Draw appropriate screen
        screen = display_manager.screen
        if game_state == GameState.MAIN_MENU:
            draw_main_menu(screen, main_menu_buttons, mouse_pos, fonts, screen_width, screen_height)
        elif game_state == GameState.PLAY_MENU:
            draw_play_menu(screen, play_menu_buttons, back_button, mouse_pos, fonts, screen_width, screen_height)
        elif game_state == GameState.OPTIONS_SCREEN:
            draw_options_menu(screen, options_buttons, back_button, mouse_pos, fonts, screen_width, screen_height,
                            display_manager)
        elif game_state == GameState.SINGLE_PLAYER:
            draw_single_player_game(screen, player, game_buttons, mouse_pos, fonts, screen_width, screen_height,
                                    drag_state, drag_unit, drag_pos, drag_source_type)
        elif game_state == GameState.MULTIPLAYER_SCREEN:
            draw_coming_soon(screen, back_button, mouse_pos, "Multiplayer", fonts, screen_width, screen_height)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()