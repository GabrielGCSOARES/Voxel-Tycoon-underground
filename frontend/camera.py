from config import GRID_SIZE, COLS, ROWS, MAP_WIDTH, HEIGHT

class Camera:
    def __init__(self):
        self.offset_x = 0
        self.offset_y = 0

    def mover(self, dx, dy):
        self.offset_x += dx
        self.offset_y += dy
        self.limitar()

    def limitar(self):
        mapa_pixel_w = COLS * GRID_SIZE
        mapa_pixel_h = ROWS * GRID_SIZE
        padding_x = MAP_WIDTH // 2
        padding_y = HEIGHT // 2
        self.offset_x = max(MAP_WIDTH - mapa_pixel_w - padding_x, min(padding_x, self.offset_x))
        self.offset_y = max(HEIGHT - mapa_pixel_h - padding_y, min(padding_y, self.offset_y))

    def aplicar(self, x, y):
        return (x + self.offset_x, y + self.offset_y)

    def tela_para_mundo(self, sx, sy):
        wx = (sx - self.offset_x) // GRID_SIZE
        wy = (sy - self.offset_y) // GRID_SIZE
        return int(wx), int(wy)

    def resetar(self):
        self.offset_x = 0
        self.offset_y = 0

    def na_borda_mar(self):
        mapa_pixel_w = COLS * GRID_SIZE
        mapa_pixel_h = ROWS * GRID_SIZE
        padding_x = MAP_WIDTH // 2
        padding_y = HEIGHT // 2
        min_x = MAP_WIDTH - mapa_pixel_w - padding_x
        max_x = padding_x
        min_y = HEIGHT - mapa_pixel_h - padding_y
        max_y = padding_y
        
        # Verificar se está na borda (simplificado para ser mais permissivo)
        # Se o offset está próximo dos limites que a câmera pode alcançar
        na_borda_x = (self.offset_x <= min_x + 50) or (self.offset_x >= max_x - 50)
        na_borda_y = (self.offset_y <= min_y + 50) or (self.offset_y >= max_y - 50)
        
        return na_borda_x or na_borda_y