import pygame
import sys
import os

# Inicialização
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("VOLTEX-TYCON  UNDERGROUND")

# Caminho do som
base_path = os.path.dirname(__file__)
click_sound_path = os.path.join(base_path, "assets", "ClickSound.wav")
click_sound = pygame.mixer.Sound(click_sound_path)
click_sound.set_volume(0.5)

# Cores
WHITE = (255, 255, 255)
BLUE = (50, 100, 255)
GREEN = (50, 200, 50)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)

# Fonte
font = pygame.font.SysFont(None, 36)

# Variáveis do jogo
score = 0
points_per_click = 1

# Botão principal
button_width, button_height = 150, 100
button_x = WIDTH // 2 - button_width // 2
button_y = HEIGHT // 2 - button_height // 2

# Botão de upgrade
upgrade_width, upgrade_height = 180, 50
upgrade_x = WIDTH - upgrade_width - 20
upgrade_y = 20
upgrade_cost = 10
upgrade_multiplier = 2
upgrade_purchased = False

clock = pygame.time.Clock()
FPS = 60

def draw_button():
    pygame.draw.rect(screen, BLUE, (button_x, button_y, button_width, button_height))
    text = font.render("CLIQUE!", True, WHITE)
    text_rect = text.get_rect(center=(button_x + button_width//2, button_y + button_height//2))
    screen.blit(text, text_rect)

def draw_score():
    text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(text, (10, 10))

def draw_upgrade():
    color = GREEN if score >= upgrade_cost and not upgrade_purchased else GRAY
    pygame.draw.rect(screen, color, (upgrade_x, upgrade_y, upgrade_width, upgrade_height))
    if upgrade_purchased:
        text = font.render("Multiplicador x2 (Comprado)", True, BLACK)
    else:
        text = font.render(f"Comprar x2 ({upgrade_cost} clicks)", True, BLACK)
    text_rect = text.get_rect(center=(upgrade_x + upgrade_width//2, upgrade_y + upgrade_height//2))
    screen.blit(text, text_rect)

# Loop principal
while True:
    clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Clique no botão principal
            if button_x <= mouse_pos[0] <= button_x + button_width and \
               button_y <= mouse_pos[1] <= button_y + button_height:
                score += points_per_click
                click_sound.play()
            
            # Clique no botão de upgrade
            if upgrade_x <= mouse_pos[0] <= upgrade_x + upgrade_width and \
               upgrade_y <= mouse_pos[1] <= upgrade_y + upgrade_height:
                if score >= upgrade_cost and not upgrade_purchased:
                    score -= upgrade_cost
                    points_per_click *= upgrade_multiplier
                    upgrade_purchased = True

    screen.fill(WHITE)
    draw_button()
    draw_score()
    draw_upgrade()
    pygame.display.flip()