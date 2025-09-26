import pygame
import sys
import json
import os
import random

# Import game modules (we'll create these next)
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
                            drag_unit, drag_pos):
    screen.fill(Colors.BACKGROUND)

    # Draw sell zone first (so it's behind other elements)
    is_dragging_to_sell = (drag_state != DragState.NONE and
                           mouse_pos[1] > screen_height - 100)
    sell_zone = draw_sell_zone(screen, screen_width, screen_height, is_dragging_to_sell)

    # Draw game layout
    draw_board(screen, player, screen_width, screen_height, drag_state, drag_unit, drag_pos, mouse_pos)
    draw_bench(screen, player, screen_width, screen_height, drag_state, drag_unit, drag_pos, mouse_pos)
    draw_shop(screen, player, screen_width, screen_height)
    draw_ui_elements(screen, player, buttons, mouse_pos, fonts, screen_width, screen_height)
    draw_traits_panel(screen, player, screen_width, screen_height, fonts)
    draw_info_panel(screen, player, screen_width, screen_height, fonts)

    # Draw drag unit if dragging
    if drag_state != DragState.NONE and drag_unit:
        unit_rect = pygame.Rect(drag_pos[0] - GameConstants.UNIT_SIZE // 2,
                                drag_pos[1] - GameConstants.UNIT_SIZE // 2,
                                GameConstants.UNIT_SIZE, GameConstants.UNIT_SIZE)

        # Make unit semi-transparent red if over sell zone
        if is_dragging_to_sell:
            # Create a semi-transparent surface
            unit_surface = pygame.Surface((GameConstants.UNIT_SIZE, GameConstants.UNIT_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(unit_surface, (255, 100, 100, 200), unit_surface.get_rect(), border_radius=5)
            pygame.draw.rect(unit_surface, (255, 200, 200, 200), unit_surface.get_rect(), 2, border_radius=5)
            screen.blit(unit_surface, unit_rect)
        else:
            pygame.draw.rect(screen, Colors.UNIT_BG, unit_rect, border_radius=5)
            pygame.draw.rect(screen, Colors.BUTTON_TEXT, unit_rect, 2, border_radius=5)

        font = pygame.font.SysFont('arial', 14)
        name_text = font.render(drag_unit.name[:8], True, Colors.BUTTON_TEXT)
        name_rect = name_text.get_rect(center=unit_rect.center)
        screen.blit(name_text, name_rect)


def draw_board(screen, player, screen_width, screen_height, drag_state, drag_unit, drag_pos, mouse_pos):
    board_width = GameConstants.BOARD_WIDTH * GameConstants.UNIT_SIZE
    board_height = GameConstants.BOARD_HEIGHT * GameConstants.UNIT_SIZE
    board_x = (screen_width - board_width) // 2
    board_y = screen_height // 4

    pygame.draw.rect(screen, Colors.BOARD_BG, (board_x - 10, board_y - 10,
                                               board_width + 20, board_height + 20), border_radius=10)

    for y in range(GameConstants.BOARD_HEIGHT):
        for x in range(GameConstants.BOARD_WIDTH):
            rect = pygame.Rect(board_x + x * GameConstants.UNIT_SIZE,
                               board_y + y * GameConstants.UNIT_SIZE,
                               GameConstants.UNIT_SIZE - 4, GameConstants.UNIT_SIZE - 4)

            is_highlighted = (drag_state != DragState.NONE and
                              rect.collidepoint(mouse_pos) and
                              player.board[y][x] is None)

            color = Colors.BUTTON_HOVER if is_highlighted else Colors.UNIT_BG
            pygame.draw.rect(screen, color, rect, border_radius=5)
            pygame.draw.rect(screen, Colors.BUTTON_TEXT, rect, 1, border_radius=5)

            if player.board[y][x]:
                unit = player.board[y][x]
                font = pygame.font.SysFont('arial', 12)
                name_text = font.render(unit.name[:8], True, Colors.BUTTON_TEXT)
                star_text = font.render("★" * unit.stars, True, (255, 215, 0))
                screen.blit(name_text, (rect.x + 5, rect.y + 5))
                screen.blit(star_text, (rect.x + 5, rect.y + 25))


def draw_bench(screen, player, screen_width, screen_height, drag_state, drag_unit, drag_pos, mouse_pos):
    bench_width = GameConstants.BENCH_SLOTS * GameConstants.BENCH_UNIT_SIZE
    bench_x = (screen_width - bench_width) // 2
    bench_y = screen_height - 260  # Moved up to make room for sell zone

    pygame.draw.rect(screen, Colors.BENCH_BG, (bench_x - 10, bench_y - 10,
                                               bench_width + 20, GameConstants.BENCH_UNIT_SIZE + 20), border_radius=8)

    for i in range(GameConstants.BENCH_SLOTS):
        rect = pygame.Rect(bench_x + i * GameConstants.BENCH_UNIT_SIZE, bench_y,
                           GameConstants.BENCH_UNIT_SIZE - 4, GameConstants.BENCH_UNIT_SIZE - 4)

        is_highlighted = (drag_state == DragState.FROM_BOARD and
                          rect.collidepoint(mouse_pos) and
                          player.bench[i] is None)

        color = Colors.BUTTON_HOVER if is_highlighted else Colors.UNIT_BG
        pygame.draw.rect(screen, color, rect, border_radius=4)
        pygame.draw.rect(screen, Colors.BUTTON_TEXT, rect, 1, border_radius=4)

        if i < len(player.bench) and player.bench[i]:
            unit = player.bench[i]
            font = pygame.font.SysFont('arial', 10)
            name_text = font.render(unit.name[:6], True, Colors.BUTTON_TEXT)
            star_text = font.render("★" * unit.stars, True, (255, 215, 0))
            cost_text = font.render(f"{unit.cost}g", True, Colors.GOLD_COLOR)
            screen.blit(name_text, (rect.x + 5, rect.y + 5))
            screen.blit(star_text, (rect.x + 5, rect.y + 20))
            screen.blit(cost_text, (rect.x + rect.width - 25, rect.y + 5))


def draw_shop(screen, player, screen_width, screen_height):
    shop_width = GameConstants.SHOP_SLOTS * GameConstants.SHOP_UNIT_SIZE
    shop_x = (screen_width - shop_width) // 2
    shop_y = screen_height - 160  # Moved up to make room for sell zone

    pygame.draw.rect(screen, Colors.SHOP_BG, (shop_x - 10, shop_y - 10,
                                              shop_width + 20, GameConstants.SHOP_UNIT_SIZE + 20), border_radius=8)

    for i in range(GameConstants.SHOP_SLOTS):
        rect = pygame.Rect(shop_x + i * GameConstants.SHOP_UNIT_SIZE, shop_y,
                           GameConstants.SHOP_UNIT_SIZE - 4, GameConstants.SHOP_UNIT_SIZE - 4)
        pygame.draw.rect(screen, Colors.UNIT_BG, rect, border_radius=4)
        pygame.draw.rect(screen, Colors.BUTTON_TEXT, rect, 1, border_radius=4)

        if i < len(player.shop) and player.shop[i]:
            unit = player.shop[i]
            font = pygame.font.SysFont('arial', 10)
            name_text = font.render(unit.name[:6], True, Colors.BUTTON_TEXT)
            cost_text = font.render(str(unit.cost), True, Colors.GOLD_COLOR)
            screen.blit(name_text, (rect.x + 5, rect.y + 5))
            screen.blit(cost_text, (rect.x + rect.width - 20, rect.y + 5))


def draw_ui_elements(screen, player, buttons, mouse_pos, fonts, screen_width, screen_height):
    gold_text = fonts['button'].render(f"Gold: {player.gold}", True, Colors.GOLD_COLOR)
    screen.blit(gold_text, (screen_width - 150, 20))

    level_text = fonts['button'].render(
        f"Level: {player.level} (XP: {player.xp}/{player.xp_to_level[player.level - 1] if player.level < 9 else 'MAX'})",
        True, Colors.BUTTON_TEXT)
    screen.blit(level_text, (screen_width - 300, 60))

    round_text = fonts['button'].render(f"Round: {player.round}", True, Colors.BUTTON_TEXT)
    screen.blit(round_text, (screen_width - 150, 100))

    # Draw buttons (including Buy XP and Reroll buttons)
    buy_xp_button = Button(50, screen_height - 50, 120, 40, "Buy XP (F)", fonts['button'])
    reroll_button = Button(180, screen_height - 50, 120, 40, "Reroll (D)", fonts['button'])

    # Check hover for all buttons
    for button in buttons + [buy_xp_button, reroll_button]:
        button.check_hover(mouse_pos)
        button.draw(screen)


def draw_traits_panel(screen, player, screen_width, screen_height, fonts):
    panel_width = 200
    panel_x = 20
    panel_y = 100

    pygame.draw.rect(screen, Colors.TRAIT_BG, (panel_x, panel_y, panel_width, 200), border_radius=8)

    trait_title = fonts['button'].render("Active Traits", True, Colors.BUTTON_TEXT)
    screen.blit(trait_title, (panel_x + 10, panel_y + 10))

    y_offset = 50
    for trait, count in player.traits.items():
        trait_text = fonts['button'].render(f"{trait} ({count})", True, Colors.BUTTON_TEXT)
        screen.blit(trait_text, (panel_x + 20, panel_y + y_offset))
        y_offset += 30


def draw_info_panel(screen, player, screen_width, screen_height, fonts):
    panel_width = 250
    panel_x = screen_width - panel_width - 20
    panel_y = 100

    pygame.draw.rect(screen, Colors.INFO_BG, (panel_x, panel_y, panel_width, 200), border_radius=8)

    info_title = fonts['button'].render("Game Info", True, Colors.BUTTON_TEXT)
    screen.blit(info_title, (panel_x + 10, panel_y + 10))

    income = player.calculate_income()
    board_units = sum(1 for row in player.board for unit in row if unit is not None)
    max_units = GameConstants.MAX_BOARD_UNITS[player.level - 1]

    info_lines = [
        f"Next Income: +{income}g",
        f"Board: {board_units}/{max_units}",
        f"Bench: {sum(1 for u in player.bench if u is not None)}/9",
        "Sell: Drag to bottom",
        "Controls: F=XP, D=Reroll, S=Sell"
    ]

    for i, line in enumerate(info_lines):
        info_text = fonts['button'].render(line, True, Colors.BUTTON_TEXT)
        screen.blit(info_text, (panel_x + 20, panel_y + 50 + i * 25))


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

    # Initial UI setup
    screen_width, screen_height = display_manager.current_resolution
    base_size = screen_height / 20
    fonts = {
        'title': pygame.font.SysFont('arial', int(base_size * 1.4), bold=True),
        'button': pygame.font.SysFont('arial', int(base_size * 0.7))
    }

    # Create menu buttons
    center_x, center_y = screen_width // 2, screen_height // 2

    # Main menu buttons
    play_button = Button(center_x - 100, center_y - 50, 200, 60, "PLAY", fonts['button'])
    options_button = Button(center_x - 100, center_y + 30, 200, 60, "OPTIONS", fonts['button'])
    quit_button = Button(center_x - 100, center_y + 110, 200, 60, "QUIT", fonts['button'])
    main_menu_buttons = [play_button, options_button, quit_button]

    # Play menu buttons
    single_player_button = Button(center_x - 150, center_y - 50, 300, 60, "SINGLE PLAYER", fonts['button'])
    multiplayer_button = Button(center_x - 150, center_y + 30, 300, 60, "MULTIPLAYER", fonts['button'])
    play_menu_buttons = [single_player_button, multiplayer_button]

    # Options menu buttons
    resolution_button = Button(center_x - 150, center_y - 50, 300, 60, "CHANGE RESOLUTION", fonts['button'])
    fullscreen_button = Button(center_x - 150, center_y + 30, 300, 60, "TOGGLE FULLSCREEN", fonts['button'])
    borderless_button = Button(center_x - 150, center_y + 110, 300, 60, "TOGGLE BORDERLESS", fonts['button'])
    options_buttons = [resolution_button, fullscreen_button, borderless_button]

    # Back button
    back_button = Button(50, 50, 120, 40, "BACK", fonts['button'])

    # Game UI buttons
    end_turn_button = Button(screen_width // 2 - 60, 20, 120, 40, "End Turn", fonts['button'])
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
                    # Start dragging
                    if game_state == GameState.SINGLE_PLAYER:
                        # Check bench for drag start
                        bench_width = GameConstants.BENCH_SLOTS * GameConstants.BENCH_UNIT_SIZE
                        bench_x = (screen_width - bench_width) // 2
                        bench_y = screen_height - 260

                        for i in range(GameConstants.BENCH_SLOTS):
                            bench_rect = pygame.Rect(bench_x + i * GameConstants.BENCH_UNIT_SIZE, bench_y,
                                                     GameConstants.BENCH_UNIT_SIZE - 4,
                                                     GameConstants.BENCH_UNIT_SIZE - 4)
                            if bench_rect.collidepoint(mouse_pos) and player.bench[i]:
                                drag_state = DragState.FROM_BENCH
                                drag_unit = player.bench[i]
                                drag_source_index = i
                                break

                        # Check board for drag start
                        if drag_state == DragState.NONE:
                            board_width = GameConstants.BOARD_WIDTH * GameConstants.UNIT_SIZE
                            board_x = (screen_width - board_width) // 2
                            board_y = screen_height // 4

                            for y in range(GameConstants.BOARD_HEIGHT):
                                for x in range(GameConstants.BOARD_WIDTH):
                                    board_rect = pygame.Rect(board_x + x * GameConstants.UNIT_SIZE,
                                                             board_y + y * GameConstants.UNIT_SIZE,
                                                             GameConstants.UNIT_SIZE - 4, GameConstants.UNIT_SIZE - 4)
                                    if board_rect.collidepoint(mouse_pos) and player.board[y][x]:
                                        drag_state = DragState.FROM_BOARD
                                        drag_unit = player.board[y][x]
                                        drag_source_index = (x, y)
                                        break
                                if drag_state != DragState.NONE:
                                    break

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and drag_state != DragState.NONE:
                    mouse_released = True

                    # Check if dropped in sell zone (bottom of screen)
                    if mouse_pos[1] > screen_height - 100:
                        # Sell the unit
                        if drag_state == DragState.FROM_BENCH:
                            player.sell_unit(drag_source_index)
                        elif drag_state == DragState.FROM_BOARD:
                            x, y = drag_source_index
                            unit = player.board[y][x]
                            if unit:
                                player.gold += unit.cost
                                player.board[y][x] = None
                                player.calculate_traits()

                    else:
                        # Handle normal drag drop
                        if game_state == GameState.SINGLE_PLAYER:
                            board_width = GameConstants.BOARD_WIDTH * GameConstants.UNIT_SIZE
                            board_x = (screen_width - board_width) // 2
                            board_y = screen_height // 4

                            bench_width = GameConstants.BENCH_SLOTS * GameConstants.BENCH_UNIT_SIZE
                            bench_x = (screen_width - bench_width) // 2
                            bench_y = screen_height - 260

                            # Check if dropped on board
                            for y in range(GameConstants.BOARD_HEIGHT):
                                for x in range(GameConstants.BOARD_WIDTH):
                                    board_rect = pygame.Rect(board_x + x * GameConstants.UNIT_SIZE,
                                                             board_y + y * GameConstants.UNIT_SIZE,
                                                             GameConstants.UNIT_SIZE - 4, GameConstants.UNIT_SIZE - 4)
                                    if board_rect.collidepoint(mouse_pos):
                                        if drag_state == DragState.FROM_BENCH:
                                            if player.move_unit_to_board(drag_source_index, x, y):
                                                player.bench[drag_source_index] = None
                                        break
                                else:
                                    continue
                                break
                            else:
                                # Check if dropped on bench
                                for i in range(GameConstants.BENCH_SLOTS):
                                    bench_rect = pygame.Rect(bench_x + i * GameConstants.BENCH_UNIT_SIZE, bench_y,
                                                             GameConstants.BENCH_UNIT_SIZE - 4,
                                                             GameConstants.BENCH_UNIT_SIZE - 4)
                                    if bench_rect.collidepoint(mouse_pos):
                                        if drag_state == DragState.FROM_BOARD:
                                            x, y = drag_source_index
                                            if player.move_unit_to_bench(x, y, i):
                                                player.board[y][x] = None
                                        break

                    # Reset drag state
                    drag_state = DragState.NONE
                    drag_unit = None
                    drag_source_index = None

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
                    bench_width = GameConstants.BENCH_SLOTS * GameConstants.BENCH_UNIT_SIZE
                    bench_x = (screen_width - bench_width) // 2
                    bench_y = screen_height - 260

                    for i in range(GameConstants.BENCH_SLOTS):
                        bench_rect = pygame.Rect(bench_x + i * GameConstants.BENCH_UNIT_SIZE, bench_y,
                                                 GameConstants.BENCH_UNIT_SIZE - 4, GameConstants.BENCH_UNIT_SIZE - 4)
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
                        base_size = screen_height / 20
                        fonts = {
                            'title': pygame.font.SysFont('arial', int(base_size * 1.4), bold=True),
                            'button': pygame.font.SysFont('arial', int(base_size * 0.7))
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
                # Check if Buy XP or Reroll buttons were clicked
                buy_xp_button = Button(50, screen_height - 50, 120, 40, "Buy XP (F)", fonts['button'])
                reroll_button = Button(180, screen_height - 50, 120, 40, "Reroll (D)", fonts['button'])

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
                                    drag_state, drag_unit, drag_pos)
        elif game_state == GameState.MULTIPLAYER_SCREEN:
            draw_coming_soon(screen, back_button, mouse_pos, "Multiplayer", fonts, screen_width, screen_height)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()