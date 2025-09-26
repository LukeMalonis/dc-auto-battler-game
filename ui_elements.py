import pygame
from game_constants import Colors


class Button:
    def __init__(self, x, y, width, height, text, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.is_hovered = False

    def draw(self, surface):
        color = Colors.BUTTON_HOVER if self.is_hovered else Colors.BUTTON_NORMAL
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, Colors.BUTTON_TEXT, self.rect, 2, border_radius=8)

        text_surf = self.font.render(self.text, True, Colors.BUTTON_TEXT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def is_clicked(self, pos, click):
        return self.rect.collidepoint(pos) and click