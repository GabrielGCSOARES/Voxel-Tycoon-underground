from config import *

class GerenciadorMundo:
    def __init__(self):
        self.superficie = [["grama" for _ in range(COLS)] for _ in range(ROWS)]
        self.caverna = [["pedra" for _ in range(COLS)] for _ in range(ROWS)]
        self.camada_atual = "superficie"

    def reset(self):
        self.superficie = [["grama" for _ in range(COLS)] for _ in range(ROWS)]
        self.caverna = [["pedra" for _ in range(COLS)] for _ in range(ROWS)]
        self.camada_atual = "superficie"

    def alternar_camada(self):
        self.camada_atual = "caverna" if self.camada_atual == "superficie" else "superficie"

    def get_grid_ativo(self):
        return self.superficie if self.camada_atual == "superficie" else self.caverna

    def get_base_tile(self):
        return "grama" if self.camada_atual == "superficie" else "pedra"

    def desenhar(self, screen):
        grid = self.get_grid_ativo()
        base = self.get_base_tile()
        
        for y in range(ROWS):
            for x in range(COLS):
                pos = (x * GRID_SIZE, y * GRID_SIZE)
                screen.blit(IMAGENS[base], pos)
                if grid[y][x] != base:
                    screen.blit(IMAGENS[grid[y][x]], pos)