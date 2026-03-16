from config import GRID_SIZE, COLS, ROWS, MAP_WIDTH, HEIGHT

class Camera:
    def __init__(self):
        self.offset_x = 0
        self.offset_y = 0

    def mover(self, dx, dy):
        # Limita o arrasto para não sair fora do mapa
        mapa_pixel_w = COLS * GRID_SIZE
        mapa_pixel_h = ROWS * GRID_SIZE

        self.offset_x = max(-(mapa_pixel_w - MAP_WIDTH), min(0, self.offset_x + dx))
        self.offset_y = max(-(mapa_pixel_h - HEIGHT),    min(0, self.offset_y + dy))

    def aplicar(self, x, y):
        return (x + self.offset_x, y + self.offset_y)

    def tela_para_mundo(self, sx, sy):
        wx = (sx - self.offset_x) // GRID_SIZE
        wy = (sy - self.offset_y) // GRID_SIZE
        return int(wx), int(wy)

    def resetar(self):
        self.offset_x = 0
        self.offset_y = 0