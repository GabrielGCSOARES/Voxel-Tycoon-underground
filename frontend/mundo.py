from config import COLS, ROWS, IMAGENS, MAP_WIDTH, HEIGHT, GRID_SIZE

class GerenciadorMundo:
    def __init__(self):
        self.superficie = [["grama" for _ in range(COLS)] for _ in range(ROWS)]
        self.caverna = [["pedra" for _ in range(COLS)] for _ in range(ROWS)]
        self.camada_atual = "superficie"
        self.upgrades = [[None for _ in range(COLS)] for _ in range(ROWS)]

    def reset(self):
        self.superficie = [["grama" for _ in range(COLS)] for _ in range(ROWS)]
        self.caverna = [["pedra" for _ in range(COLS)] for _ in range(ROWS)]
        self.camada_atual = "superficie"
        self.upgrades = [[None for _ in range(COLS)] for _ in range(ROWS)]

    def alternar_camada(self):
        self.camada_atual = "caverna" if self.camada_atual == "superficie" else "superficie"

    def get_grid_ativo(self):
        return self.superficie if self.camada_atual == "superficie" else self.caverna

    def get_base_tile(self):
        return "grama" if self.camada_atual == "superficie" else "pedra"

    def desenhar(self, screen, camera):
        grid = self.get_grid_ativo()
        base = self.get_base_tile()
        for y in range(ROWS):
            for x in range(COLS):
                sx, sy = camera.aplicar(x*GRID_SIZE, y*GRID_SIZE)
                if sx+GRID_SIZE < 0 or sx > MAP_WIDTH:
                    continue
                if sy+GRID_SIZE < 0 or sy > HEIGHT:
                    continue
                screen.blit(IMAGENS[base], (sx, sy))
                if grid[y][x] != base:
                    screen.blit(IMAGENS[grid[y][x]], (sx, sy))