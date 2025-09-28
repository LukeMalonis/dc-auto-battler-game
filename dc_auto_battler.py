import pygame
import sys
import json
import os
import random
import math

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


# Small height increase to close the gap between boards
UNIT_WIDTH = 180    # Keep the same width
UNIT_HEIGHT = 110   # Small increase from 100 to 110 (only 10 pixels taller)
LARGE_SHOP_UNIT_SIZE = 200
card_gap = 20
LARGE_BENCH_UNIT_SIZE = 200

# Define trait thresholds and descriptions
TRAIT_INFO = {
    "Bat Family": {
        "thresholds": [3, 5],
        "description": "Bat Family units gain bonus attack damage and critical strike chance",
        "bonuses": ["3: +30% Attack Damage", "5: +50% Attack Damage & 25% Crit Chance"]
    },
    "Justice League": {
        "thresholds": [2, 4, 6, 8],
        "description": "Justice League members protect each other with shields and bonus stats",
        "bonuses": ["2: +100 Health to all JL", "4: +200 Health & Shield", "6: +300 Health & Attack Speed",
                    "8: +500 Health & Teamwide Buff"]
    },
    "Rogues Gallery": {
        "thresholds": [3, 5, 7],
        "description": "Rogues gain power from losing streaks and chaos effects",
        "bonuses": ["3: +2 Gold after losing streak", "5: +5 Gold & Bonus Damage", "7: +8 Gold & Chaos Auras"]
    },
    "Teen Titans": {
        "thresholds": [3, 5],
        "description": "Teen Titans work together with combo attacks and synergy bonuses",
        "bonuses": ["3: Combo attacks trigger", "5: Ultimate team attack unlocked"]
    },
    "Threat": {
        "thresholds": [1],
        "description": "Threat units are powerful solo carries that dominate the battlefield",
        "bonuses": ["1: Massive solo power boost"]
    },
    "Mind Games": {
        "thresholds": [1],
        "description": "Hugo Strange manipulates the enemy team and creates unique opportunities",
        "bonuses": ["1: Choose a special unit to appear in shop"]
    },
    "Suicide Squad": {
        "thresholds": [2, 4],
        "description": "Suicide Squad members have explosive attacks",
        "bonuses": ["2: Abilities now deal explosive aoe damage", "4: Bonus damage to all suicide squad members"]
    },
    "Legion of Doom": {
        "thresholds": [2, 4, 6, 8],
        "description": "Legion of Doom members grow stronger together with dark powers",
        "bonuses": ["2: +10% Damage", "4: +25% Damage & Health", "6: +40% Stats", "8: Ultimate Evil Unleashed"]
    },
    "Kryptonians": {
        "thresholds": [2, 4],
        "description": "Kryptonians draw power from the sun, gaining massive stat bonuses",
        "bonuses": ["2: +50% Health", "4: +100% Health & Damage"]
    },
    "League of Assassins": {
        "thresholds": [2, 4],
        "description": "Assassins strike from the shadows with lethal precision",
        "bonuses": ["2: Execute low health targets", "4: Global execute threshold"]
    },
    "Bruiser": {
        "thresholds": [2, 4, 6],
        "description": "Bruisers are tough frontliners who gain bonus health and damage reduction",
        "bonuses": ["2: +200 Health", "4: +500 Health & 20% Damage Reduction", "6: +1000 Health & 40% Damage Reduction"]
    },
    "Form Swapper": {
        "thresholds": [2, 4],
        "description": "Form Swappers adapt to battle conditions, changing from tank to damage roles",
        "bonuses": ["2: Adaptive form switching", "4: Perfect form mastery"]
    },
    "Snipers": {
        "thresholds": [2, 4, 6],
        "description": "Snipers attack from range with increased damage and critical strikes",
        "bonuses": ["2: +2 Range & 25% Damage", "4: +3 Range & 50% Damage", "6: Global Range & 100% Damage"]
    },
    "Robots": {
        "thresholds": [2, 4],
        "description": "Robots evolve during combat, gaining permanent stat improvements",
        "bonuses": ["2: Evolve each round", "4: Ultimate evolution unlocked"]
    },
    "Animals": {
        "thresholds": [2, 4, 6],
        "description": "Animal units hunt together with pack tactics and ferocious attacks",
        "bonuses": ["2: Pack hunting bonus", "4: Alpha predator buff", "6: Primal fury unleashed"]
    },
    "Sorcerer": {
        "thresholds": [2, 4, 6, 8],
        "description": "Sorcerers wield magical powers that manipulate the battlefield",
        "bonuses": ["2: Basic spells", "4: Advanced magic", "6: Master spells", "8: Arcane supremacy"]
    },
    "Justice League Dark": {
        "thresholds": [2, 4],
        "description": "Justice League Dark deals with supernatural threats using dark magic",
        "bonuses": ["2: Dark magic attacks", "4: Supernatural mastery"]
    },
    "Duelists": {
        "thresholds": [2, 4],
        "description": "Duelists gain attack speed with each attack, becoming faster as combat continues",
        "bonuses": ["2: 5% stacking attack speed on hi", "4: 10% stacking attack speed on hit"]
    },
    "Fastest Man Alive": {
        "thresholds": [1],
        "description": "The Flash moves and attacks at impossible speeds",
        "bonuses": ["1: Infinite speed scaling"]
    },
    "5 Cost Trait": {
        "thresholds": [1],
        "description": "5-cost units have unique game-changing abilities",
        "bonuses": ["1: Ultimate ability unlocked"]
    },
    "Resurrection": {
        "thresholds": [1],
        "description": "Solomon Grundy refuses to stay dead, returning to fight again",
        "bonuses": ["1: Revive once per combat"]
    },
    "Lurking In The Waters": {
        "thresholds": [1],
        "description": "King Shark ambushes enemies from below with devastating attacks",
        "bonuses": ["1: Ambush from any water tile"]
    },
    "I Have A Question": {
        "thresholds": [1],
        "description": "The Question uncovers secrets that give strategic advantages",
        "bonuses": ["1: Reveal enemy team secrets"]
    },
    "Clown Prince of Crime": {
        "thresholds": [1],
        "description": "Joker creates chaos and mayhem with unpredictable effects",
        "bonuses": ["1: Random chaos effects"]
    },
    "ADC": {
        "thresholds": [1],
        "description": "Attack Damage Carries focus on pure damage output",
        "bonuses": ["1: Massive damage scaling"]
    },
    "Mage": {
        "thresholds": [1],
        "description": "Mages wield powerful area-of-effect spells",
        "bonuses": ["1: Area damage spells"]
    },
    "N/A": {
        "thresholds": [],
        "description": "No additional trait",
        "bonuses": []
    },
    "Nabu's Chosen": {
        "thresholds": [1],
        "description": "While your team has more members Dr. Fate heals, if you have more Dr. Fate deals massive damage",
        "bonuses": ["1: Either heal or deal damage depending on board state"]
    },
    "Familial Bond": {
        "thresholds": [2],
        "description": "Increasing familial bond gives your team significantly more damage",
        "bonuses": "2: When you play both ghul's on your board, give your team +30% damage"

    }
}


def get_trait_display(trait_name, current_count):
    """Get the display string showing current count and next threshold"""
    if trait_name not in TRAIT_INFO:
        return f"{trait_name} ({current_count})"

    thresholds = TRAIT_INFO[trait_name]["thresholds"]

    if not thresholds:  # For traits like "N/A" with no thresholds
        return f"{trait_name}"

    # Find current active threshold and next threshold
    active_threshold = 0
    next_threshold = None

    for threshold in thresholds:
        if current_count >= threshold:
            active_threshold = threshold
        else:
            if next_threshold is None:
                next_threshold = threshold
            break

    if next_threshold is None:
        # Max threshold reached
        return f"{trait_name} ({current_count} - MAX)"
    else:
        # Show current/next
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
    font_bonus = pygame.font.SysFont('arial', 11)
    font_thresholds = pygame.font.SysFont('arial', 12, bold=True)

    # Prepare text
    title_text = font_title.render(trait_name, True, Colors.BUTTON_TEXT)
    thresholds_text = font_thresholds.render(f"Thresholds: {get_trait_full_info(trait_name)}", True, Colors.GOLD_COLOR)
    desc_text = font_desc.render(info["description"], True, Colors.BUTTON_TEXT)

    # Calculate tooltip size based on content
    tooltip_width = max(title_text.get_width(), thresholds_text.get_width(), desc_text.get_width()) + 20
    tooltip_height = 60 + len(info["bonuses"]) * 15

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

    # Draw bonuses
    for i, bonus in enumerate(info["bonuses"]):
        bonus_text = font_bonus.render(bonus, True, (200, 200, 100))
        surface.blit(bonus_text, (tooltip_x + 10, tooltip_y + 65 + i * 15))


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
    """Draw a unit card with proper borders and information, with PNG support"""
    if not unit:
        return

    # Draw card background with cost-based border
    border_color = get_unit_border_color(unit.cost)
    pygame.draw.rect(surface, Colors.UNIT_BG, rect, border_radius=8)
    pygame.draw.rect(surface, border_color, rect, 3, border_radius=8)

    # Draw PNG if available
    image_area = pygame.Rect(rect.x + 3, rect.y + 3, rect.width - 6, rect.height - 6)

    if unit.png_surface is not None:
        try:
            # Scale PNG to fit the card
            png_rect = unit.png_surface.get_rect()
            scale_factor = min(image_area.width / png_rect.width, image_area.height / png_rect.height) * 0.8
            new_size = (int(png_rect.width * scale_factor), int(png_rect.height * scale_factor))
            scaled_png = pygame.transform.smoothscale(unit.png_surface, new_size)
            png_pos = (rect.centerx - new_size[0] // 2, rect.centery - new_size[1] // 2)
            surface.blit(scaled_png, png_pos)
        except Exception as e:
            # Fallback to placeholder if PNG fails
            pygame.draw.rect(surface, (40, 40, 40), image_area, border_radius=6)
            print(f"Error drawing PNG for {unit.name}: {e}")
    else:
        # Placeholder
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
            if trait != "N/A":  # Skip N/A traits
                trait_text = font_small.render(trait, True, Colors.BUTTON_TEXT)
                trait_outline = font_small.render(trait, True, (0, 0, 0))
                trait_pos = (trait_x, trait_y + i * 14)
                # Draw outline for readability over PNG
                for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    surface.blit(trait_outline, (trait_pos[0] + dx, trait_pos[1] + dy))
                surface.blit(trait_text, trait_pos)


def draw_hugo_strange_choice(screen, choices, buttons, mouse_pos, screen_width, screen_height):
    """Draw the Hugo Strange unit choice overlay"""
    # Semi-transparent overlay covering the entire screen
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Dark semi-transparent
    screen.blit(overlay, (0, 0))

    # Main choice panel
    panel_width = 700
    panel_height = 500
    panel_x = (screen_width - panel_width) // 2
    panel_y = (screen_height - panel_height) // 2

    # Panel background
    pygame.draw.rect(screen, (40, 40, 60), (panel_x, panel_y, panel_width, panel_height), border_radius=15)
    pygame.draw.rect(screen, Colors.GOLD_COLOR, (panel_x, panel_y, panel_width, panel_height), 4, border_radius=15)

    # Title
    font_title = pygame.font.SysFont('arial', 32, bold=True)
    title_text = font_title.render("HUGO STRANGE: CREATION SELECTION", True, Colors.GOLD_COLOR)
    title_rect = title_text.get_rect(centerx=panel_x + panel_width // 2, y=panel_y + 30)
    screen.blit(title_text, title_rect)

    # Description
    font_desc = pygame.font.SysFont('arial', 18)
    desc_lines = [
        "Hugo Strange has discovered how to create powerful beings.",
        "Choose one creation to replace Hugo Strange and appear in your shop:",
        "(This choice is permanent for the rest of the game)"
    ]

    for i, line in enumerate(desc_lines):
        desc_text = font_desc.render(line, True, Colors.BUTTON_TEXT)
        desc_rect = desc_text.get_rect(centerx=panel_x + panel_width // 2, y=panel_y + 90 + i * 30)
        screen.blit(desc_text, desc_rect)

    # Draw choice buttons
    for button in buttons:
        button.check_hover(mouse_pos)
        button.draw(screen)

    # Warning text at bottom
    font_warning = pygame.font.SysFont('arial', 14)
    warning_text = font_warning.render("All Hugo Strange units will be transformed into your selection", True,
                                       (255, 100, 100))
    warning_rect = warning_text.get_rect(centerx=panel_x + panel_width // 2, y=panel_y + panel_height - 40)
    screen.blit(warning_text, warning_rect)


def replace_hugo_strange_units(player, replacement_name):
    from unit import Unit
    import os

    png_files = []
    if os.path.exists("assets"):
        png_files = os.listdir("assets")

    for y in range(GameConstants.BOARD_HEIGHT):
        for x in range(GameConstants.BOARD_WIDTH):
            if player.board[y][x] and player.board[y][x].name == "Hugo Strange":
                old_unit = player.board[y][x]
                new_unit = Unit(
                    replacement_name,
                    3,  # Always 3 cost
                    ["Mind Games"],
                    old_unit.health,
                    old_unit.damage,
                    get_replacement_png_name(replacement_name, png_files)
                )
                new_unit.stars = old_unit.stars
                player.board[y][x] = new_unit

    for i in range(len(player.bench)):
        if player.bench[i] and player.bench[i].name == "Hugo Strange":
            old_unit = player.bench[i]
            new_unit = Unit(
                replacement_name,
                3,  # Always 3 cost
                ["Mind Games"],
                old_unit.health,
                old_unit.damage,
                get_replacement_png_name(replacement_name, png_files)
            )
            new_unit.stars = old_unit.stars
            player.bench[i] = new_unit

    player.calculate_traits()


def get_replacement_traits(name):
    # All replacements now just have Mind Games
    return ["Mind Games"]


def get_replacement_png_name(name, png_files):
    name_mapping = {
        "Mr. Freeze": "Mr._Freeze.png",
        "Poison Ivy": "Poison_Ivy.png",
        "Two Face": "Two_Face.png"
    }
    png_name = name_mapping.get(name)
    if png_name and png_name in png_files:
        return png_name
    return None


# [Keep all your existing drawing functions like draw_main_menu, draw_play_menu, etc.]
# Drawing functions (these remain the same as before)
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


def draw_single_player_game(screen, player, opponent, buttons, mouse_pos, fonts, screen_width, screen_height,
                            drag_state,
                            drag_unit, drag_pos, drag_source_type):
    screen.fill(Colors.BACKGROUND)

    # Draw opponent's hex board at the top
    draw_opponent_square_board(screen, opponent, screen_width, screen_height)

    # Draw sell zone ONLY when dragging a unit (but not from shop)
    is_dragging_to_sell = (drag_state != DragState.NONE and
                           drag_source_type != 'shop' and
                           mouse_pos[1] > screen_height - 100)

    if drag_state != DragState.NONE and drag_source_type != 'shop':
        draw_sell_zone(screen, screen_width, screen_height, is_dragging_to_sell)

    # Draw game layout with hex board
    draw_board(screen, player, screen_width, screen_height, drag_state, drag_unit, drag_pos, mouse_pos)
    draw_bench(screen, player, screen_width, screen_height, drag_state, drag_unit, drag_pos, mouse_pos)
    draw_shop(screen, player, screen_width, screen_height, drag_state, drag_source_type, mouse_pos)
    draw_ui_elements(screen, player, buttons, mouse_pos, fonts, screen_width, screen_height)
    draw_traits_panel(screen, player, screen_width, screen_height, fonts, mouse_pos)
    draw_info_panel(screen, player, screen_width, screen_height, fonts)

    # Draw drag unit if dragging
    if drag_state != DragState.NONE and drag_unit:
        unit_rect = pygame.Rect(drag_pos[0] - UNIT_WIDTH // 2,
                                drag_pos[1] - UNIT_HEIGHT // 2,
                                UNIT_WIDTH, UNIT_HEIGHT)

        # Special visual for shop drag (green semi-transparent with BUY text)
        if drag_source_type == 'shop':
            unit_surface = pygame.Surface((UNIT_WIDTH, UNIT_HEIGHT), pygame.SRCALPHA)
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
                unit_surface = pygame.Surface((UNIT_WIDTH, UNIT_HEIGHT), pygame.SRCALPHA)
                pygame.draw.rect(unit_surface, (255, 100, 100, 200), unit_surface.get_rect(), border_radius=8)
                pygame.draw.rect(unit_surface, (255, 200, 200, 200), unit_surface.get_rect(), 3, border_radius=8)
                screen.blit(unit_surface, unit_rect)
            else:
                draw_unit_card(screen, drag_unit, unit_rect, show_details=True)


def draw_board(screen, player, screen_width, screen_height, drag_state, drag_unit, drag_pos, mouse_pos):
    board_width = 7 * UNIT_WIDTH
    board_height = 3 * UNIT_HEIGHT
    board_x = (screen_width - board_width) // 2
    board_y = screen_height - 650  # RAISED by 50 pixels to fill gap and avoid bench



    for y in range(3):  # 3 rows
        for x in range(7):  # 7 columns
            rect = pygame.Rect(board_x + x * UNIT_WIDTH,
                               board_y + y * UNIT_HEIGHT,
                               UNIT_WIDTH - 4, UNIT_HEIGHT - 4)

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


def draw_opponent_square_board(screen, opponent, screen_width, screen_height):
    """Draw the opponent's horizontal rectangular board at the top"""
    board_width = 7 * UNIT_WIDTH  # 7 columns - much wider
    board_height = 3 * UNIT_HEIGHT  # 3 rows
    board_x = (screen_width - board_width) // 2
    board_y = 90  # Position at top



    for y in range(3):  # 3 rows
        for x in range(7):  # 7 columns
            rect = pygame.Rect(board_x + x * UNIT_WIDTH,
                               board_y + y * UNIT_HEIGHT,
                               UNIT_WIDTH - 4, UNIT_HEIGHT - 4)

            # Draw opponent board slot
            pygame.draw.rect(screen, (70, 40, 40), rect, border_radius=8)
            pygame.draw.rect(screen, (255, 150, 100), rect, 1, border_radius=8)

            # Draw opponent unit if present
            if (hasattr(opponent, 'board') and opponent.board and
                    y < len(opponent.board) and x < len(opponent.board[y]) and
                    opponent.board[y][x] is not None):
                unit = opponent.board[y][x]
                draw_unit_card(screen, unit, rect)


def draw_bench(screen, player, screen_width, screen_height, drag_state, drag_unit, drag_pos, mouse_pos):
    bench_slots = GameConstants.BENCH_SLOTS
    shop_slots = GameConstants.SHOP_SLOTS
    shop_card_size = LARGE_SHOP_UNIT_SIZE
    card_gap = 20

    # Calculate the total width of the shop row
    shop_width = shop_slots * shop_card_size + (shop_slots - 1) * card_gap

    # Calculate the size of each bench square so that 9 + 8 gaps fits in shop_width
    bench_card_size = (shop_width - (bench_slots - 1) * card_gap) // bench_slots

    bench_width = bench_slots * bench_card_size + (bench_slots - 1) * card_gap
    bench_x = (screen_width - bench_width) // 2
    # Place the bench above shop row, tweak - bench_card_size - XX for vertical alignment
    bench_y = screen_height - shop_card_size - 90  # 80px gap, tweak as needed

    pygame.draw.rect(screen, Colors.BENCH_BG, (bench_x - 10, bench_y - 10,
                                               bench_width + 20, bench_card_size + 20), border_radius=8)

    for i in range(bench_slots):
        rect = pygame.Rect(
            bench_x + i * (bench_card_size + card_gap),
            bench_y,
            bench_card_size,
            bench_card_size
        )

        can_drop_here = (player.bench[i] is None or
                         (drag_state != DragState.NONE and drag_unit != player.bench[i]))

        is_highlighted = (drag_state != DragState.NONE and
                          rect.collidepoint(mouse_pos) and
                          can_drop_here)

        slot_color = Colors.BUTTON_HOVER if is_highlighted else Colors.UNIT_BG
        pygame.draw.rect(screen, slot_color, rect, border_radius=6)
        pygame.draw.rect(screen, Colors.BUTTON_TEXT, rect, 1, border_radius=6)

        if i < len(player.bench) and player.bench[i]:
            unit = player.bench[i]
            draw_unit_card(screen, unit, rect)


def draw_shop(screen, player, screen_width, screen_height, drag_state, drag_source_type, mouse_pos):
    shop_slots = GameConstants.SHOP_SLOTS
    shop_card_size = LARGE_SHOP_UNIT_SIZE
    card_gap = 20
    shop_width = shop_slots * shop_card_size + (shop_slots - 1) * card_gap
    shop_x = (screen_width - shop_width) // 2
    shop_y = screen_height - 150 # 60px above bottom

    pygame.draw.rect(
        screen, Colors.SHOP_BG,
        (shop_x - 15, shop_y - 15, shop_width + 30, shop_card_size + 30), border_radius=10
    )

    for i in range(shop_slots):
        rect = pygame.Rect(
            shop_x + i * (shop_card_size + card_gap),
            shop_y,
            shop_card_size,
            shop_card_size
        )

        is_highlighted = (
            drag_state == DragState.NONE
            and rect.collidepoint(mouse_pos)
            and player.shop[i] is not None
        )

        slot_color = Colors.BUTTON_HOVER if is_highlighted else Colors.UNIT_BG
        pygame.draw.rect(screen, slot_color, rect, border_radius=8)
        pygame.draw.rect(screen, Colors.BUTTON_TEXT, rect, 2, border_radius=8)

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
        f"XP: {player.xp}/{player.xp_to_level[player.level - 1] if player.level < 10 else 'MAX'}", True,
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
    panel_width = 300  # Increased width
    panel_x = 10
    panel_y = 180
    panel_height = int(screen_height * 0.75)  # Much taller to fit all traits

    # Draw background
    pygame.draw.rect(screen, Colors.TRAIT_BG, (panel_x, panel_y, panel_width, panel_height), border_radius=8)
    pygame.draw.rect(screen, Colors.BUTTON_TEXT, (panel_x, panel_y, panel_width, panel_height), 2, border_radius=8)

    # Title
    font_title = pygame.font.SysFont('arial', 20, bold=True)
    trait_title = font_title.render("Active Traits", True, Colors.BUTTON_TEXT)
    screen.blit(trait_title, (panel_x + 15, panel_y + 12))

    # Traits with proper formatting
    font_trait = pygame.font.SysFont('arial', 16)
    y_offset = 50
    hovered_trait = None

    if player.traits:
        for trait, count in player.traits.items():
            if trait == "N/A":  # Skip N/A traits
                continue

            trait_rect = pygame.Rect(panel_x + 10, panel_y + y_offset, panel_width - 20, 28)

            # Check if mouse is hovering
            if trait_rect.collidepoint(mouse_pos):
                hovered_trait = trait
                pygame.draw.rect(screen, (100, 100, 140), trait_rect, border_radius=6)

            trait_display = get_trait_display(trait, count)
            trait_text = font_trait.render(trait_display, True, Colors.BUTTON_TEXT)
            screen.blit(trait_text, (panel_x + 15, panel_y + y_offset + 6))
            y_offset += 32

            # Break if we're running out of space
            if y_offset > panel_height - 40:
                break
    else:
        no_traits = font_trait.render("No active traits", True, Colors.BUTTON_TEXT)
        screen.blit(no_traits, (panel_x + 20, panel_y + 55))

    # Draw tooltip if hovering over a trait
    if hovered_trait:
        draw_trait_tooltip(screen, hovered_trait, mouse_pos, screen_width, screen_height)


def draw_info_panel(screen, player, screen_width, screen_height, fonts):
    panel_width = 280  # Increased width
    panel_x = screen_width - panel_width - 10
    panel_y = 180
    panel_height = int(screen_height * 0.75)  # Much taller

    # Draw background
    pygame.draw.rect(screen, Colors.INFO_BG, (panel_x, panel_y, panel_width, panel_height), border_radius=8)
    pygame.draw.rect(screen, Colors.BUTTON_TEXT, (panel_x, panel_y, panel_width, panel_height), 2, border_radius=8)

    # Title
    font_title = pygame.font.SysFont('arial', 20, bold=True)
    info_title = font_title.render("Game Info", True, Colors.BUTTON_TEXT)
    screen.blit(info_title, (panel_x + 15, panel_y + 12))

    # Info lines with larger font
    font_info = pygame.font.SysFont('arial', 16)

    income = player.calculate_income()
    board_units = sum(1 for row in player.board for unit in row if unit is not None)
    max_units = GameConstants.MAX_BOARD_UNITS[player.level - 1] if player.level <= len(
        GameConstants.MAX_BOARD_UNITS) else 10
    bench_units = sum(1 for u in player.bench if u is not None)

    info_lines = [
        f"Income: +{income}g",
        f"Board: {board_units}/{max_units}",
        f"Bench: {bench_units}/9",
        f"Level: {player.level}",
        f"Round: {player.round}",
        f"Gold: {player.gold}",
        f"XP: {player.xp}/{player.xp_to_level[player.level - 1] if player.level < 10 else 'MAX'}"
    ]

    y_offset = 50
    for line in info_lines:
        info_text = font_info.render(line, True, Colors.BUTTON_TEXT)
        screen.blit(info_text, (panel_x + 20, panel_y + y_offset))
        y_offset += 30



def main():
    display_manager = DisplayManager()
    clock = pygame.time.Clock()
    game_state = GameState.MAIN_MENU

    # Initialize player for single player game
    player = Player()

    # Create opponent (temporary placeholder)
    opponent = Player()
    opponent.name = "Opponent"
    # Initialize empty board for opponent
    opponent.board = [[None for _ in range(GameConstants.BOARD_WIDTH)] for _ in range(GameConstants.BOARD_HEIGHT)]

    # Drag state
    drag_state = DragState.NONE
    drag_unit = None
    drag_pos = (0, 0)
    drag_source_index = None
    drag_source_type = None  # 'bench', 'board', or 'shop'
    drag_start_pos = (0, 0)  # Track where drag started
    click_threshold = 5  # Minimum pixels to consider it a drag vs click

    # Hugo Strange special ability state
    hugo_strange_choice_active = False
    hugo_strange_choices = ["Mr. Freeze", "Poison Ivy", "Two Face"]
    hugo_strange_choice_buttons = []
    hugo_strange_selected_option = None

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
                        # BLOCK DRAGGING DURING HUGO STRANGE UI
                        if hugo_strange_choice_active:
                            break  # Skip all drag handling if UI is active

                        # Check bench for drag start
                        bench_slots = GameConstants.BENCH_SLOTS
                        shop_slots = GameConstants.SHOP_SLOTS
                        shop_card_size = LARGE_SHOP_UNIT_SIZE
                        card_gap = 20
                        shop_width = shop_slots * shop_card_size + (shop_slots - 1) * card_gap
                        bench_card_size = (shop_width - (bench_slots - 1) * card_gap) // bench_slots
                        bench_width = bench_slots * bench_card_size + (bench_slots - 1) * card_gap
                        bench_x = (screen_width - bench_width) // 2
                        bench_y = screen_height - shop_card_size - 90  # match draw_bench

                        for i in range(bench_slots):
                            bench_rect = pygame.Rect(
                                bench_x + i * (bench_card_size + card_gap),
                                bench_y,
                                bench_card_size,
                                bench_card_size
                            )
                            if bench_rect.collidepoint(mouse_pos) and player.bench[i]:
                                drag_state = DragState.FROM_BENCH
                                drag_unit = player.bench[i]
                                drag_source_index = i
                                drag_source_type = 'bench'
                                break

                        # Check board for drag start
                        if drag_state == DragState.NONE:
                            # Use the new rectangular dimensions
                            board_width = 7 * UNIT_WIDTH
                            board_x = (screen_width - board_width) // 2
                            board_y = screen_height - 650  # Match your current board position

                            for y in range(3):  # 3 rows
                                for x in range(7):  # 7 columns
                                    # Create the rectangle for this board position
                                    board_rect = pygame.Rect(
                                        board_x + x * UNIT_WIDTH,
                                        board_y + y * UNIT_HEIGHT,
                                        UNIT_WIDTH - 4,
                                        UNIT_HEIGHT - 4
                                    )

                                    # Check if mouse is over this rectangle AND there's a unit there
                                    if (board_rect.collidepoint(mouse_pos) and
                                            y < len(player.board) and
                                            x < len(player.board[y]) and
                                            player.board[y][x] is not None):
                                        drag_state = DragState.FROM_BOARD
                                        drag_unit = player.board[y][x]
                                        drag_source_index = (x, y)
                                        drag_source_type = 'board'
                                        break
                                if drag_state != DragState.NONE:
                                    break
                        # Check shop for drag start (AFTER bench/board checks)
                        if drag_state == DragState.NONE:
                            shop_slots = GameConstants.SHOP_SLOTS
                            shop_card_size = LARGE_SHOP_UNIT_SIZE
                            card_gap = 20
                            shop_width = shop_slots * shop_card_size + (shop_slots - 1) * card_gap
                            shop_x = (screen_width - shop_width) // 2
                            shop_y = screen_height - 150  # Match your new position!

                            for i in range(shop_slots):
                                shop_rect = pygame.Rect(
                                    shop_x + i * (shop_card_size + card_gap),
                                    shop_y,
                                    shop_card_size,
                                    shop_card_size
                                )
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
                            shop_slots = GameConstants.SHOP_SLOTS
                            shop_card_size = LARGE_SHOP_UNIT_SIZE
                            card_gap = 20
                            shop_width = shop_slots * shop_card_size + (shop_slots - 1) * card_gap
                            shop_x = (screen_width - shop_width) // 2
                            shop_y = screen_height - 150  # Match your new position!

                            # Check if mouse is outside shop area (actually dragged away)
                            bg_padding = 50
                            shop_area = pygame.Rect(shop_x - bg_padding, shop_y - bg_padding,
                                                    shop_width + (bg_padding * 2), shop_card_size + (bg_padding * 2))
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
                            board_width = 7 * UNIT_WIDTH
                            board_x = (screen_width - board_width) // 2
                            board_y = screen_height - 650

                            bench_slots = GameConstants.BENCH_SLOTS
                            shop_slots = GameConstants.SHOP_SLOTS
                            shop_card_size = LARGE_SHOP_UNIT_SIZE
                            card_gap = 20
                            shop_width = shop_slots * shop_card_size + (shop_slots - 1) * card_gap
                            bench_card_size = (shop_width - (bench_slots - 1) * card_gap) // bench_slots
                            bench_width = bench_slots * bench_card_size + (bench_slots - 1) * card_gap
                            bench_x = (screen_width - bench_width) // 2
                            bench_y = screen_height - shop_card_size - 90  # match draw_bench

                            # Check if dropped on board
                            board_dropped = False
                            board_width = 7 * UNIT_WIDTH
                            board_x = (screen_width - board_width) // 2
                            board_y = screen_height - 650  # Match the new rectangular board position

                            for y in range(3):  # 3 rows for rectangular board
                                for x in range(7):  # 7 columns for rectangular board
                                    board_rect = pygame.Rect(board_x + x * UNIT_WIDTH,
                                                             board_y + y * UNIT_HEIGHT,
                                                             UNIT_WIDTH - 4, UNIT_HEIGHT - 4)
                                    if board_rect.collidepoint(mouse_pos):
                                        if drag_source_type == 'bench':
                                            # Move from bench to board (swap if occupied)
                                            target_unit = player.board[y][x]
                                            if target_unit is None:
                                                # Empty spot - just move
                                                if player.move_unit_to_board(drag_source_index, x, y):
                                                    player.bench[drag_source_index] = None
                                                    # Auto-trigger Hugo UI if Hugo Strange was just placed
                                                    if (player.board[y][x] and player.board[y][x].name == "Hugo Strange"
                                                            and not hugo_strange_choice_active
                                                            and not hasattr(player, 'hugo_strange_activated')):
                                                        hugo_strange_choice_active = True
                                                        button_width = 550
                                                        button_height = 70
                                                        start_y = (screen_height - 500) // 2 + 150
                                                        hugo_strange_choice_buttons.clear()
                                                        for i, choice in enumerate(hugo_strange_choices):
                                                            button_y = start_y + i * 90
                                                            button = Button(
                                                                (screen_width - button_width) // 2,
                                                                button_y,
                                                                button_width,
                                                                button_height,
                                                                f"SELECT: {choice}",
                                                                pygame.font.SysFont('arial', 20, bold=True)
                                                            )
                                                            hugo_strange_choice_buttons.append(button)
                                            else:
                                                # Swap bench unit with board unit
                                                player.board[y][x] = drag_unit
                                                player.bench[drag_source_index] = target_unit
                                                player.calculate_traits()
                                                # Auto-trigger Hugo UI if Hugo Strange was just placed
                                                if (player.board[y][x] and player.board[y][x].name == "Hugo Strange"
                                                        and not hugo_strange_choice_active
                                                        and not hasattr(player, 'hugo_strange_activated')):
                                                    hugo_strange_choice_active = True
                                                    button_width = 550
                                                    button_height = 70
                                                    start_y = (screen_height - 500) // 2 + 150
                                                    hugo_strange_choice_buttons.clear()
                                                    for i, choice in enumerate(hugo_strange_choices):
                                                        button_y = start_y + i * 90
                                                        button = Button(
                                                            (screen_width - button_width) // 2,
                                                            button_y,
                                                            button_width,
                                                            button_height,
                                                            f"SELECT: {choice}",
                                                            pygame.font.SysFont('arial', 20, bold=True)
                                                        )
                                                        hugo_strange_choice_buttons.append(button)
                                        elif drag_source_type == 'board':
                                            # Move from board to different board position (swap)
                                            source_x, source_y = drag_source_index
                                            target_unit = player.board[y][x]

                                            # Swap the units
                                            player.board[y][x] = drag_unit
                                            player.board[source_y][source_x] = target_unit
                                            player.calculate_traits()
                                            # Auto-trigger Hugo UI if Hugo Strange was just placed
                                            if (player.board[y][x] and player.board[y][x].name == "Hugo Strange"
                                                    and not hugo_strange_choice_active
                                                    and not hasattr(player, 'hugo_strange_activated')):
                                                hugo_strange_choice_active = True
                                                button_width = 550
                                                button_height = 70
                                                start_y = (screen_height - 500) // 2 + 150
                                                hugo_strange_choice_buttons.clear()
                                                for i, choice in enumerate(hugo_strange_choices):
                                                    button_y = start_y + i * 90
                                                    button = Button(
                                                        (screen_width - button_width) // 2,
                                                        button_y,
                                                        button_width,
                                                        button_height,
                                                        f"SELECT: {choice}",
                                                        pygame.font.SysFont('arial', 20, bold=True)
                                                    )
                                                    hugo_strange_choice_buttons.append(button)
                                        board_dropped = True
                                        break
                                if board_dropped:
                                    break

                            if not board_dropped:
                                # Check if dropped on bench
                                for i in range(bench_slots):
                                    bench_rect = pygame.Rect(
                                        bench_x + i * (bench_card_size + card_gap),
                                        bench_y,
                                        bench_card_size,
                                        bench_card_size
                                    )
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
                    if not hugo_strange_choice_active:  # Add this check
                        player.buy_xp()
                elif event.key == pygame.K_d and game_state == GameState.SINGLE_PLAYER:
                    if not hugo_strange_choice_active:  # Add this check
                        player.refresh_shop()
                elif event.key == pygame.K_s and game_state == GameState.SINGLE_PLAYER and drag_state == DragState.NONE:
                    # Sell unit under mouse (bench only for now)
                    bench_slots = GameConstants.BENCH_SLOTS
                    shop_slots = GameConstants.SHOP_SLOTS
                    shop_card_size = LARGE_SHOP_UNIT_SIZE
                    card_gap = 20
                    shop_width = shop_slots * shop_card_size + (shop_slots - 1) * card_gap
                    bench_card_size = (shop_width - (bench_slots - 1) * card_gap) // bench_slots
                    bench_width = bench_slots * bench_card_size + (bench_slots - 1) * card_gap
                    bench_x = (screen_width - bench_width) // 2
                    bench_y = screen_height - shop_card_size - 90  # match draw_bench

                    for i in range(bench_slots):
                        bench_rect = pygame.Rect(
                            bench_x + i * (bench_card_size + card_gap),
                            bench_y,
                            bench_card_size,
                            bench_card_size
                        )
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
                    # Reset Hugo Strange state for new game
                    hugo_strange_choice_active = False
                    hugo_strange_choice_buttons.clear()
                    hugo_strange_selected_option = None
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
                if hugo_strange_choice_active:
                    # Handle Hugo Strange choice UI - BLOCK ALL OTHER ACTIONS
                    for i, button in enumerate(hugo_strange_choice_buttons):
                        if button.is_clicked(mouse_pos, True):
                            hugo_strange_selected_option = hugo_strange_choices[i]
                            print(f"Hugo Strange selected: {hugo_strange_selected_option}")

                            replace_hugo_strange_units(player, hugo_strange_selected_option)
                            player.hugo_strange_activated = True
                            player.hugo_replacement_choice = hugo_strange_selected_option
                            hugo_strange_choice_active = False
                            hugo_strange_choice_buttons.clear()
                            break
                else:
                    # Normal game logic - only run if Hugo Strange UI is NOT active
                    shop_clicked = False
                    shop_slots = GameConstants.SHOP_SLOTS
                    shop_card_size = LARGE_SHOP_UNIT_SIZE
                    card_gap = 20
                    shop_width = shop_slots * shop_card_size + (shop_slots - 1) * card_gap
                    shop_x = (screen_width - shop_width) // 2
                    shop_y = screen_height - 150

                    for i in range(shop_slots):
                        shop_rect = pygame.Rect(
                            shop_x + i * (shop_card_size + card_gap),
                            shop_y,
                            shop_card_size,
                            shop_card_size
                        )
                        if shop_rect.collidepoint(mouse_pos) and player.shop[i] is not None:
                            # Check if this purchase would cause a combination
                            unit_to_buy = player.shop[i]
                            if unit_to_buy and player.gold >= unit_to_buy.cost:
                                if player.can_combine_anywhere(unit_to_buy):
                                    player.buy_and_combine(i)
                                else:
                                    player.buy_unit(i)
                            shop_clicked = True
                            break

                    # Check for Hugo Strange placement (only if not already activated)
                    if not shop_clicked and not hasattr(player, 'hugo_strange_activated'):
                        hugo_placed = False
                        # Check board for Hugo Strange
                        for y in range(GameConstants.BOARD_HEIGHT):
                            for x in range(GameConstants.BOARD_WIDTH):
                                if player.board[y][x] and player.board[y][x].name == "Hugo Strange":
                                    hugo_placed = True
                                    break
                            if hugo_placed:
                                break

                        # Check bench for Hugo Strange
                        if not hugo_placed:
                            for unit in player.bench:
                                if unit and unit.name == "Hugo Strange":
                                    hugo_placed = True
                                    break

                        if hugo_placed and not hugo_strange_choice_active:
                            # Activate Hugo Strange choice
                            hugo_strange_choice_active = True
                            # Create choice buttons
                            button_width = 550
                            button_height = 70
                            start_y = (screen_height - 500) // 2 + 150

                            hugo_strange_choice_buttons.clear()
                            for i, choice in enumerate(hugo_strange_choices):
                                button_y = start_y + i * 90
                                button = Button(
                                    (screen_width - button_width) // 2,
                                    button_y,
                                    button_width,
                                    button_height,
                                    f"SELECT: {choice}",
                                    pygame.font.SysFont('arial', 20, bold=True)
                                )
                                hugo_strange_choice_buttons.append(button)

                    # Only check other buttons if no shop unit was clicked AND Hugo UI is not active
                    if not shop_clicked and not hugo_strange_choice_active:
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
            draw_single_player_game(screen, player, opponent, game_buttons, mouse_pos, fonts, screen_width, screen_height,
                                    drag_state, drag_unit, drag_pos, drag_source_type)

            # Draw Hugo Strange choice UI on top if active
            if hugo_strange_choice_active:
                draw_hugo_strange_choice(screen, hugo_strange_choices, hugo_strange_choice_buttons, mouse_pos,
                                         screen_width, screen_height)
        elif game_state == GameState.MULTIPLAYER_SCREEN:
            draw_coming_soon(screen, back_button, mouse_pos, "Multiplayer", fonts, screen_width, screen_height)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()