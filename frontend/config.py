import pygame
import os # Necessário para checar se os arquivos existem

pygame.init()
pygame.mixer.init()

# ---------------- TELA E GRID ----------------
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
PANEL_WIDTH = int(WIDTH * 0.20)
GRID_SIZE = int(HEIGHT / 10)
MAP_WIDTH = ((WIDTH - PANEL_WIDTH) // GRID_SIZE) * GRID_SIZE
COLS, ROWS = MAP_WIDTH // GRID_SIZE, HEIGHT // GRID_SIZE

# Criar a tela (precisa vir antes de carregar as imagens)
screen = pygame.display.set_mode((MAP_WIDTH + PANEL_WIDTH, HEIGHT), pygame.FULLSCREEN)

# ---------------- CORES ----------------
BRANCO, PRETO, CINZA = (255, 255, 255), (0, 0, 0), (40, 40, 40)
DOURADO, VERDE = (255, 215, 0), (50, 200, 80)

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
def escalar(img): return pygame.transform.scale(img, (GRID_SIZE, GRID_SIZE))

try:
    # Carregamos a grama primeiro para ser nossa base de segurança
    img_grama = pygame.image.load("assets/grama.png").convert_alpha()
    
    IMAGENS = {
        "grama": escalar(img_grama),
        # Se não tiver pedra.png, usa a grama como reserva
        "pedra": escalar(pygame.image.load("assets/pedra.png").convert_alpha()) if os.path.exists("assets/pedra.png") else escalar(img_grama), 
        "casa": escalar(pygame.image.load("assets/casa.png").convert_alpha()),
        "fazenda": escalar(pygame.image.load("assets/fazenda.png").convert_alpha()),
        "silo": escalar(pygame.image.load("assets/silo.png").convert_alpha()),
        "cachoeira": escalar(pygame.image.load("assets/cachoeira.png").convert_alpha()),
        "palacio": escalar(pygame.image.load("assets/palacio.png").convert_alpha()),
        "elevador": escalar(pygame.image.load("assets/entrace cave.png").convert_alpha()), 
    }
except Exception as e:
    print(f"Aviso: Algumas imagens faltaram. Erro: {e}")
    # FALLBACK: Se tudo der errado, cria blocos coloridos para não ficar preto
    IMAGENS = {k: pygame.Surface((GRID_SIZE, GRID_SIZE)) for k in ["grama", "pedra", "casa", "fazenda", "silo", "cachoeira", "palacio", "elevador"]}
    IMAGENS["grama"].fill((34, 139, 34))
    IMAGENS["pedra"].fill((100, 100, 100))
    IMAGENS["elevador"].fill(DOURADO)

# ---------------- DADOS ----------------
ITENS = ["casa", "fazenda", "elevador", "silo", "cachoeira", "palacio"]
CUSTOS = {"casa": 100, "fazenda": 150, "elevador": 250, "silo": 200, "cachoeira": 300, "palacio": 1000}
XP_ITENS = {"casa": 20, "fazenda": 40, "elevador": 50, "silo": 80, "cachoeira": 120, "palacio": 500}