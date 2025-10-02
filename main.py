# main.py - SIMPLE PYGAME TEST
import pygame
import os

print("=== STARTING PYGAME TEST ===")

# Try different display drivers
for driver in ['x11', 'dummy', 'framebuffer']:
    try:
        os.environ['SDL_VIDEODRIVER'] = driver
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption(f"Test with {driver}")
        print(f"✅ Success with {driver} driver!")
        break
    except Exception as e:
        print(f"❌ Failed with {driver}: {e}")

print("PyGame initialized. Creating window...")

# Simple game loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    screen.fill((30, 30, 50))
    font = pygame.font.SysFont('arial', 36)
    text = font.render("DC Auto Battler - WORKING!", True, (255, 215, 0))
    screen.blit(text, (150, 280))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
print("=== TEST COMPLETE ===")