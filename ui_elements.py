import pygame
from game_constants import Colors


class Button:
    def __init__(self, x, y, width, height, text, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.original_font = font
        self.is_hovered = False

    def draw(self, surface):
        color = Colors.BUTTON_HOVER if self.is_hovered else Colors.BUTTON_NORMAL
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        pygame.draw.rect(surface, Colors.BUTTON_TEXT, self.rect, 2, border_radius=6)

        # Auto-scale font to fit button
        font = self.original_font
        text_surf = font.render(self.text, True, Colors.BUTTON_TEXT)

        # Scale down font if text is too wide
        max_text_width = self.rect.width - 20  # Leave 10px padding on each side
        if text_surf.get_width() > max_text_width:
            # Calculate scale factor
            scale = max_text_width / text_surf.get_width()
            new_size = max(10, int(font.get_height() * scale * 0.9))  # Keep minimum size
            font = pygame.font.SysFont('arial', new_size)
            text_surf = font.render(self.text, True, Colors.BUTTON_TEXT)

        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def is_clicked(self, pos, click):
        return self.rect.collidepoint(pos) and click