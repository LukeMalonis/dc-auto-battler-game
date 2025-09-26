import pygame
import sys
import json
import os

# Initialize Pygame
pygame.init()

# Configuration
CONFIG_FILE = "game_config.json"

# Default configuration - windowed mode, 1080p
default_config = {
    "resolution": [1920, 1080],
    "fullscreen": False,
    "borderless": False,
    "music_volume": 0.7,
    "sfx_volume": 0.8
}


def load_config():
    """Load configuration from file or create default"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            return default_config
    else:
        save_config(default_config)
        return default_config


def save_config(config):
    """Save configuration to file"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)


class DisplayManager:
    def __init__(self):
        self.config = load_config()

        # Proper resolution options
        self.resolutions = [
            {"name": "1280x720 (720p)", "size": (1280, 720)},
            {"name": "1920x1080 (1080p)", "size": (1920, 1080)},
            {"name": "2048x1080 (2K Cinema)", "size": (2048, 1080)},
            {"name": "2560x1440 (2K QHD)", "size": (2560, 1440)},
            {"name": "3840x2160 (4K UHD)", "size": (3840, 2160)}
        ]

        # Find current resolution index
        self.current_res_index = 1  # Default to 1080p (index 1)
        current_res = tuple(self.config["resolution"])
        for i, res in enumerate(self.resolutions):
            if res["size"] == current_res:
                self.current_res_index = i
                break

        self.current_resolution = self.resolutions[self.current_res_index]["size"]
        self.fullscreen = self.config["fullscreen"]
        self.borderless = self.config["borderless"]
        self.setup_display()

    def setup_display(self):
        """Setup the display based on current settings"""
        if self.borderless:
            self.screen = pygame.display.set_mode(self.current_resolution, pygame.NOFRAME)
        elif self.fullscreen:
            self.screen = pygame.display.set_mode(self.current_resolution, pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(self.current_resolution, pygame.RESIZABLE)

        pygame.display.set_caption("DC Auto Battler")

    def set_resolution(self, index):
        """Set specific resolution by index"""
        if 0 <= index < len(self.resolutions):
            self.current_res_index = index
            new_res = self.resolutions[index]["size"]
            self.current_resolution = new_res
            self.config["resolution"] = list(new_res)
            self.setup_display()
            save_config(self.config)
            return True
        return False

    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed"""
        self.fullscreen = not self.fullscreen
        self.config["fullscreen"] = self.fullscreen
        self.setup_display()
        save_config(self.config)

    def toggle_borderless(self):
        """Toggle borderless mode"""
        self.borderless = not self.borderless
        self.config["borderless"] = self.borderless
        self.setup_display()
        save_config(self.config)

    def get_current_resolution_name(self):
        """Get friendly name for current resolution"""
        return self.resolutions[self.current_res_index]["name"]


# Colors
BACKGROUND = (20, 20, 40)
BUTTON_NORMAL = (70, 70, 120)
BUTTON_HOVER = (90, 90, 150)
BUTTON_TEXT = (255, 255, 255)
TITLE_COLOR = (255, 215, 0)
COMING_SOON_COLOR = (200, 200, 200)
GAME_BG_COLOR = (255, 255, 255)  # White background for game screen
GAME_TEXT_COLOR = (0, 0, 0)  # Black text for game screen


class Button:
    def __init__(self, x, y, width, height, text, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.is_hovered = False

    def draw(self, surface):
        color = BUTTON_HOVER if self.is_hovered else BUTTON_NORMAL
        pygame.draw.rect(surface, color, self.rect, border_radius=12)
        pygame.draw.rect(surface, BUTTON_TEXT, self.rect, 3, border_radius=12)

        text_surf = self.font.render(self.text, True, BUTTON_TEXT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def is_clicked(self, pos, click):
        return self.rect.collidepoint(pos) and click


class GameState:
    MAIN_MENU = 0
    PLAY_MENU = 1
    OPTIONS_SCREEN = 2
    SINGLE_PLAYER = 3
    MULTIPLAYER_SCREEN = 4


def draw_main_menu(screen, buttons, mouse_pos, fonts, screen_width, screen_height):
    screen.fill(BACKGROUND)

    # Draw title
    title_text = fonts['title'].render("DC AUTO BATTLE", True, TITLE_COLOR)
    title_rect = title_text.get_rect(center=(screen_width // 2, screen_height // 4))
    screen.blit(title_text, title_rect)

    # Draw buttons
    for button in buttons:
        button.check_hover(mouse_pos)
        button.draw(screen)


def draw_play_menu(screen, buttons, back_button, mouse_pos, fonts, screen_width, screen_height):
    screen.fill(BACKGROUND)

    # Draw back button
    back_button.check_hover(mouse_pos)
    back_button.draw(screen)

    title_text = fonts['title'].render("SELECT MODE", True, TITLE_COLOR)
    title_rect = title_text.get_rect(center=(screen_width // 2, screen_height // 4))
    screen.blit(title_text, title_rect)

    for button in buttons:
        button.check_hover(mouse_pos)
        button.draw(screen)


def draw_options_menu(screen, buttons, back_button, mouse_pos, fonts, screen_width, screen_height, display_manager):
    screen.fill(BACKGROUND)

    # Draw back button
    back_button.check_hover(mouse_pos)
    back_button.draw(screen)

    title_text = fonts['title'].render("DISPLAY SETTINGS", True, TITLE_COLOR)
    title_rect = title_text.get_rect(center=(screen_width // 2, screen_height // 6))
    screen.blit(title_text, title_rect)

    # Draw current resolution info
    res_text = fonts['button'].render(f"Current: {display_manager.get_current_resolution_name()}", True, BUTTON_TEXT)
    res_rect = res_text.get_rect(center=(screen_width // 2, screen_height // 3))
    screen.blit(res_text, res_rect)

    for button in buttons:
        button.check_hover(mouse_pos)
        button.draw(screen)


def draw_coming_soon(screen, back_button, mouse_pos, screen_name, fonts, screen_width, screen_height):
    screen.fill(BACKGROUND)

    back_button.check_hover(mouse_pos)
    back_button.draw(screen)

    message_text = fonts['title'].render(f"{screen_name} - Coming Soon!", True, COMING_SOON_COLOR)
    message_rect = message_text.get_rect(center=(screen_width // 2, screen_height // 2))
    screen.blit(message_text, message_rect)


def draw_single_player_game(screen, back_button, mouse_pos, fonts, screen_width, screen_height):
    # White background for the game screen
    screen.fill(GAME_BG_COLOR)

    # Back button with dark colors to contrast white background
    back_button.check_hover(mouse_pos)
    # Temporarily change back button colors for white background
    original_colors = (BUTTON_NORMAL, BUTTON_HOVER, BUTTON_TEXT)
    back_button.is_hovered = back_button.rect.collidepoint(mouse_pos)
    back_color = (50, 50, 100) if back_button.is_hovered else (30, 30, 70)
    pygame.draw.rect(screen, back_color, back_button.rect, border_radius=12)
    pygame.draw.rect(screen, (0, 0, 0), back_button.rect, 3, border_radius=12)

    back_text = fonts['button'].render(back_button.text, True, (255, 255, 255))
    back_text_rect = back_text.get_rect(center=back_button.rect.center)
    screen.blit(back_text, back_text_rect)

    # Game title
    title_text = fonts['title'].render("DC AUTO BATTLE - SINGLE PLAYER", True, GAME_TEXT_COLOR)
    title_rect = title_text.get_rect(center=(screen_width // 2, screen_height // 4))
    screen.blit(title_text, title_rect)

    # Main game message
    game_text = fonts['title'].render("This is the game", True, GAME_TEXT_COLOR)
    game_rect = game_text.get_rect(center=(screen_width // 2, screen_height // 2))
    screen.blit(game_text, game_rect)

    # Subtitle instruction
    instruction_text = fonts['button'].render("Game development in progress...", True, (100, 100, 100))
    instruction_rect = instruction_text.get_rect(center=(screen_width // 2, screen_height // 2 + 80))
    screen.blit(instruction_text, instruction_rect)


def main():
    # Initialize display manager (starts in windowed 1080p)
    display_manager = DisplayManager()
    clock = pygame.time.Clock()
    game_state = GameState.MAIN_MENU

    # Initial UI setup with SMALLER fonts
    screen_width, screen_height = display_manager.current_resolution
    base_size = screen_height / 20  # Smaller base size for fonts
    fonts = {
        'title': pygame.font.SysFont('arial', int(base_size * 1.4), bold=True),  # Smaller title
        'button': pygame.font.SysFont('arial', int(base_size * 0.7))  # Smaller buttons
    }

    # Create buttons
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

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_clicked = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Handle back navigation with ESC
                    if game_state == GameState.SINGLE_PLAYER or game_state == GameState.MULTIPLAYER_SCREEN:
                        game_state = GameState.PLAY_MENU
                    elif game_state == GameState.PLAY_MENU or game_state == GameState.OPTIONS_SCREEN:
                        game_state = GameState.MAIN_MENU

        # Handle button clicks
        if mouse_clicked:
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
                elif multiplayer_button.is_clicked(mouse_pos, True):
                    game_state = GameState.MULTIPLAYER_SCREEN
                elif back_button.is_clicked(mouse_pos, True):
                    game_state = GameState.MAIN_MENU

            elif game_state == GameState.OPTIONS_SCREEN:
                if resolution_button.is_clicked(mouse_pos, True):
                    # Cycle through resolutions
                    new_index = (display_manager.current_res_index + 1) % len(display_manager.resolutions)
                    if display_manager.set_resolution(new_index):
                        # Update screen dimensions and recreate buttons with smaller fonts
                        screen_width, screen_height = display_manager.current_resolution
                        base_size = screen_height / 20  # Keep smaller font size
                        fonts = {
                            'title': pygame.font.SysFont('arial', int(base_size * 1.4), bold=True),
                            'button': pygame.font.SysFont('arial', int(base_size * 0.7))
                        }
                        center_x, center_y = screen_width // 2, screen_height // 2

                        # Recreate all buttons with new sizes and smaller fonts
                        play_button = Button(center_x - 100, center_y - 50, 200, 60, "PLAY", fonts['button'])
                        options_button = Button(center_x - 100, center_y + 30, 200, 60, "OPTIONS", fonts['button'])
                        quit_button = Button(center_x - 100, center_y + 110, 200, 60, "QUIT", fonts['button'])
                        main_menu_buttons = [play_button, options_button, quit_button]

                        single_player_button = Button(center_x - 150, center_y - 50, 300, 60, "SINGLE PLAYER",
                                                      fonts['button'])
                        multiplayer_button = Button(center_x - 150, center_y + 30, 300, 60, "MULTIPLAYER",
                                                    fonts['button'])
                        play_menu_buttons = [single_player_button, multiplayer_button]

                        resolution_button = Button(center_x - 150, center_y - 50, 300, 60, "CHANGE RESOLUTION",
                                                   fonts['button'])
                        fullscreen_button = Button(center_x - 150, center_y + 30, 300, 60, "TOGGLE FULLSCREEN",
                                                   fonts['button'])
                        borderless_button = Button(center_x - 150, center_y + 110, 300, 60, "TOGGLE BORDERLESS",
                                                   fonts['button'])
                        options_buttons = [resolution_button, fullscreen_button, borderless_button]

                        back_button = Button(50, 50, 120, 40, "BACK", fonts['button'])

                elif fullscreen_button.is_clicked(mouse_pos, True):
                    display_manager.toggle_fullscreen()
                    screen_width, screen_height = display_manager.current_resolution
                elif borderless_button.is_clicked(mouse_pos, True):
                    display_manager.toggle_borderless()
                    screen_width, screen_height = display_manager.current_resolution
                elif back_button.is_clicked(mouse_pos, True):
                    game_state = GameState.MAIN_MENU

            elif game_state == GameState.SINGLE_PLAYER or game_state == GameState.MULTIPLAYER_SCREEN:
                if back_button.is_clicked(mouse_pos, True):
                    game_state = GameState.PLAY_MENU

        # Draw appropriate screen
        if game_state == GameState.MAIN_MENU:
            draw_main_menu(display_manager.screen, main_menu_buttons, mouse_pos, fonts, screen_width, screen_height)
        elif game_state == GameState.PLAY_MENU:
            draw_play_menu(display_manager.screen, play_menu_buttons, back_button, mouse_pos, fonts, screen_width,
                           screen_height)
        elif game_state == GameState.OPTIONS_SCREEN:
            draw_options_menu(display_manager.screen, options_buttons, back_button, mouse_pos, fonts, screen_width,
                              screen_height, display_manager)
        elif game_state == GameState.SINGLE_PLAYER:
            draw_single_player_game(display_manager.screen, back_button, mouse_pos, fonts, screen_width, screen_height)
        elif game_state == GameState.MULTIPLAYER_SCREEN:
            draw_coming_soon(display_manager.screen, back_button, mouse_pos, "Multiplayer", fonts, screen_width,
                             screen_height)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()