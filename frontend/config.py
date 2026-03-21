import pygame, os

pygame.init()
pygame.mixer.init()

# ---------------- TELA E GRID ----------------
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
PANEL_WIDTH = int(WIDTH * 0.20)
GRID_SIZE = 48
COLS, ROWS = 50, 50
MAP_WIDTH = WIDTH - PANEL_WIDTH

# ---------------- CORES ----------------
BRANCO, PRETO, CINZA = (255, 255, 255), (0, 0, 0), (40, 40, 40)
DOURADO, VERDE = (255, 215, 0), (50, 200, 80)

# ---------------- TELA ----------------
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# ---------------- ÁUDIO ----------------
try:
    if os.path.exists("assets/musicatema.wav"):
        pygame.mixer.music.load("assets/musicatema.wav")
        pygame.mixer.music.set_volume(0.4)
    if os.path.exists("assets/click.wav"):
        CLICK_SOUND = pygame.mixer.Sound("assets/click.wav")
    else:
        CLICK_SOUND = None
except:
    CLICK_SOUND = None

# ---------------- IMAGENS ----------------
def carregar_imagens():
    def escalar(img): return pygame.transform.scale(img, (GRID_SIZE, GRID_SIZE))
    IMAGENS = {}
    try:
        img_grama = pygame.image.load("assets/grama.png").convert_alpha()
        IMAGENS["grama"] = escalar(img_grama)
        IMAGENS["pedra"] = escalar(pygame.image.load("assets/pedra.png").convert_alpha()) if os.path.exists("assets/pedra.png") else escalar(img_grama)
        IMAGENS["casa"] = escalar(pygame.image.load("assets/casa.png").convert_alpha())
        IMAGENS["fazenda"] = escalar(pygame.image.load("assets/fazenda.png").convert_alpha())
        IMAGENS["silo"] = escalar(pygame.image.load("assets/silo.png").convert_alpha())
        IMAGENS["cachoeira"] = escalar(pygame.image.load("assets/cachoeira.png").convert_alpha())
        IMAGENS["palacio"] = escalar(pygame.image.load("assets/palacio.png").convert_alpha())
        IMAGENS["elevador"] = escalar(pygame.image.load("assets/entrace cave.png").convert_alpha())
    except:
        for k in ["grama","pedra","casa","fazenda","silo","cachoeira","palacio","elevador"]:
            IMAGENS[k] = pygame.Surface((GRID_SIZE, GRID_SIZE))
        IMAGENS["grama"].fill((34,139,34))
        IMAGENS["pedra"].fill((100,100,100))
        IMAGENS["elevador"].fill((255,215,0))
    return IMAGENS

IMAGENS = carregar_imagens()

# ---------------- DADOS ----------------
ITENS   = ["casa", "fazenda", "elevador", "silo", "cachoeira", "palacio"]
CUSTOS  = {"casa":100, "fazenda":150, "elevador":250, "silo":200, "cachoeira":300, "palacio":1000}
XP_ITENS= {"casa":20, "fazenda":40, "elevador":50, "silo":80, "cachoeira":120, "palacio":500}