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
        self.cavernas = {
            1: [["pedra" for _ in range(COLS)] for _ in range(ROWS)],
            2: [["pedra" for _ in range(COLS)] for _ in range(ROWS)],
            3: [["pedra" for _ in range(COLS)] for _ in range(ROWS)],
            4: [["pedra" for _ in range(COLS)] for _ in range(ROWS)]
        }
        self.upgrades_superficie = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.upgrades_cavernas = {
            1: [[0 for _ in range(COLS)] for _ in range(ROWS)],
            2: [[0 for _ in range(COLS)] for _ in range(ROWS)],
            3: [[0 for _ in range(COLS)] for _ in range(ROWS)],
            4: [[0 for _ in range(COLS)] for _ in range(ROWS)]
        }
        self.camada_atual = "superficie"
        self.elevadores_cantos = {
            (0, 0): {"id": 1, "nivel_req": 5},
            (COLS - 1, 0): {"id": 2, "nivel_req": 10},
            (0, ROWS - 1): {"id": 3, "nivel_req": 15},
            (COLS - 1, ROWS - 1): {"id": 4, "nivel_req": 20}
        }
        self._colocar_elevadores_iniciais()

    def _colocar_elevadores_iniciais(self):
        for (gx, gy), info in self.elevadores_cantos.items():
            self.superficie[gy][gx] = "elevador"
            cid = info["id"]
            self.cavernas[cid][gy][gx] = "elevador"

    def alternar_camada(self, caverna_id=1):
        if self.camada_atual == "superficie":
            self.camada_atual = f"caverna_{caverna_id}"
        else:
            self.camada_atual = "superficie"

    def get_grid_ativo(self):
        if self.camada_atual == "superficie":
            return self.superficie
        else:
            cid = int(self.camada_atual.split("_")[1])
            return self.cavernas[cid]

    def get_upgrades_ativo(self):
        if self.camada_atual == "superficie":
            return self.upgrades_superficie
        else:
            cid = int(self.camada_atual.split("_")[1])
            return self.upgrades_cavernas[cid]

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
        eh_caverna = self.camada_atual != "superficie"

        for y in range(ROWS):
            for x in range(COLS):
                sx, sy = camera.aplicar(x * GRID_SIZE, y * GRID_SIZE)

                if sx + GRID_SIZE < 0 or sx > MAP_WIDTH or sy + GRID_SIZE < 0 or sy > HEIGHT:
                    continue

                # Fundo
                screen.blit(IMAGENS[base], (sx, sy))

                # Construções
                item_no_grid = grid[y][x]
                if item_no_grid != base and item_no_grid in IMAGENS:
                    screen.blit(IMAGENS[item_no_grid], (sx, sy))

                    nivel = upgrades[y][x]
                    if nivel > 0 and item_no_grid != "elevador":
                        txt_nivel = self.font_nivel.render(f"Lv.{nivel}", True, (255, 255, 255))
                        screen.blit(txt_nivel, (sx + 2, sy + 2))