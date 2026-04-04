import pygame
from config import COLS, ROWS, IMAGENS, MAP_WIDTH, HEIGHT, GRID_SIZE

class GerenciadorMundo:
    def __init__(self):
        self.font_nivel = pygame.font.SysFont("arial", 14, bold=True)
        self.reset()

    def reset(self):
        self.superficie = [["grama" for _ in range(COLS)] for _ in range(ROWS)]
        self.caverna = [["pedra" for _ in range(COLS)] for _ in range(ROWS)]
        self.upgrades_superficie = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.upgrades_caverna = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.camada_atual = "superficie"

    def alternar_camada(self):
        self.camada_atual = "caverna" if self.camada_atual == "superficie" else "superficie"

    def get_grid_ativo(self):
        return self.superficie if self.camada_atual == "superficie" else self.caverna

    def get_upgrades_ativo(self):
        return self.upgrades_superficie if self.camada_atual == "superficie" else self.upgrades_caverna

    def get_base_tile(self):
        return "grama" if self.camada_atual == "superficie" else "pedra"

    def desenhar(self, screen, camera):
        grid = self.get_grid_ativo()
        upgrades = self.get_upgrades_ativo()
        base = self.get_base_tile()
        
        for y in range(ROWS):
            for x in range(COLS):
                sx, sy = camera.aplicar(x * GRID_SIZE, y * GRID_SIZE)
                
                if sx + GRID_SIZE < 0 or sx > MAP_WIDTH or sy + GRID_SIZE < 0 or sy > HEIGHT:
                    continue
                
                # Desenha o chão da camada atual
                screen.blit(IMAGENS[base], (sx, sy))
                
                # Desenha construções e níveis
                item_no_grid = grid[y][x]
                if item_no_grid != base:
                    screen.blit(IMAGENS[item_no_grid], (sx, sy))
                    
                    nivel = upgrades[y][x]
                    if nivel > 0 and item_no_grid != "elevador":
                        txt_nivel = self.font_nivel.render(f"Lv.{nivel}", True, (255, 255, 255))
                        screen.blit(txt_nivel, (sx + 2, sy + 2))