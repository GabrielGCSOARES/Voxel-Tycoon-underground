import pygame
import random
from config import COLS, ROWS, IMAGENS, MAP_WIDTH, HEIGHT, GRID_SIZE

class GerenciadorMundo:
    def __init__(self):
        self.font_nivel = pygame.font.SysFont("arial", 14, bold=True)
        self._gerar_ruido_caverna()
        self.reset()

    def _gerar_ruido_caverna(self):
        """Gera variação sutil de cor para cada tile da caverna (só roda uma vez)"""
        random.seed(42)
        self.ruido = [
            [random.randint(-12, 12) for _ in range(COLS)]
            for _ in range(ROWS)
        ]

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

    def _desenhar_tile_caverna(self, screen, sx, sy, x, y):
        """Desenha tile de pedra sólido com variação sutil de cor"""
        v = self.ruido[y][x]
        base_r, base_g, base_b = 55, 55, 60
        cor = (
            max(0, min(255, base_r + v)),
            max(0, min(255, base_g + v)),
            max(0, min(255, base_b + v + 2)),
        )
        pygame.draw.rect(screen, cor, (sx, sy, GRID_SIZE, GRID_SIZE))

        # Linha sutil de borda para dar sensação de profundidade
        borda = (max(0, cor[0] - 18), max(0, cor[1] - 18), max(0, cor[2] - 18))
        pygame.draw.rect(screen, borda, (sx, sy, GRID_SIZE, GRID_SIZE), 1)

    def desenhar(self, screen, camera):
        grid = self.get_grid_ativo()
        upgrades = self.get_upgrades_ativo()
        base = self.get_base_tile()
        eh_caverna = self.camada_atual == "caverna"

        for y in range(ROWS):
            for x in range(COLS):
                sx, sy = camera.aplicar(x * GRID_SIZE, y * GRID_SIZE)

                if sx + GRID_SIZE < 0 or sx > MAP_WIDTH or sy + GRID_SIZE < 0 or sy > HEIGHT:
                    continue

                # Fundo
                if eh_caverna:
                    self._desenhar_tile_caverna(screen, sx, sy, x, y)
                else:
                    screen.blit(IMAGENS[base], (sx, sy))

                # Construções
                item_no_grid = grid[y][x]
                if item_no_grid != base and item_no_grid in IMAGENS:
                    screen.blit(IMAGENS[item_no_grid], (sx, sy))

                    nivel = upgrades[y][x]
                    if nivel > 0 and item_no_grid != "elevador":
                        txt_nivel = self.font_nivel.render(f"Lv.{nivel}", True, (255, 255, 255))
                        screen.blit(txt_nivel, (sx + 2, sy + 2))