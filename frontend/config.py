import pygame, os

pygame.init()
pygame.mixer.init()

# ---------------- TELA E GRID ----------------
info = pygame.display.Info()
WIDTH = info.current_w if info.current_w > 0 else 1280
HEIGHT = info.current_h if info.current_h > 0 else 720
PANEL_WIDTH = int(WIDTH * 0.20)
GRID_SIZE = 48
COLS, ROWS = 50, 50
MAP_WIDTH = WIDTH - PANEL_WIDTH

# ---------------- CORES ----------------
BRANCO, PRETO, CINZA = (255, 255, 255), (0, 0, 0), (40, 40, 40)
DOURADO, VERDE = (255, 215, 0), (50, 200, 80)

# ---------------- TELA ----------------
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("V.T. Underground")

# ---------------- RESOLUÇÃO DE CAMINHOS ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# ---------------- ÁUDIO ----------------
CLICK_SOUND = None
try:
    musica_path = os.path.join(ASSETS_DIR, "musicatema.wav")
    if os.path.exists(musica_path):
        pygame.mixer.music.load(musica_path)
        pygame.mixer.music.set_volume(0.4)
    
    click_path = os.path.join(ASSETS_DIR, "click.wav")
    if os.path.exists(click_path):
        CLICK_SOUND = pygame.mixer.Sound(click_path)
except Exception as e:
    print(f"⚠️ Aviso sobre áudio: {e}")

# ---------------- IMAGENS ----------------
def carregar_imagens():
    def escalar(img): return pygame.transform.scale(img, (GRID_SIZE, GRID_SIZE))
    IMAGENS = {}
    
    # Fallbacks iniciais
    for k in ["grama","pedra","casa","fazenda","silo","cachoeira","palacio","elevador"]:
        surf = pygame.Surface((GRID_SIZE, GRID_SIZE))
        if k == "grama": surf.fill((34, 139, 34))
        elif k == "pedra": surf.fill((100, 100, 100))
        elif k == "elevador": surf.fill((255, 215, 0))
        else: surf.fill((255, 0, 255)) 
        IMAGENS[k] = surf

    arquivos = {
        "grama": "grama.png",
        "pedra": "pedra.png",
        "casa": "casa.png",
        "fazenda": "fazenda.png",
        "silo": "silo.png",
        "cachoeira": "cachoeira.png",
        "palacio": "palacio.png",
        "elevador": "entrace cave.png"
    }

    print(f"\n--- 🔎 BUSCANDO ASSETS EM: {ASSETS_DIR} ---\n")

    for chave, nome_arquivo in arquivos.items():
        caminho_completo = os.path.join(ASSETS_DIR, nome_arquivo)

        try:
            if os.path.exists(caminho_completo):
                img = pygame.image.load(caminho_completo).convert_alpha()
                IMAGENS[chave] = escalar(img)
                print(f"✅ {nome_arquivo} carregado.")
            else:
                print(f"❌ NÃO ENCONTRADO: {caminho_completo}")
        except Exception as e:
            print(f"❌ ERRO AO ABRIR {nome_arquivo}: {e}")

    return IMAGENS

IMAGENS = carregar_imagens()

# ---------------- DADOS ----------------
ITENS   = ["casa", "fazenda", "elevador", "silo", "cachoeira", "palacio"]
CUSTOS  = {"casa":100, "fazenda":150, "elevador":250, "silo":200, "cachoeira":300, "palacio":1000}
XP_ITENS= {"casa":20, "fazenda":40, "elevador":50, "silo":80, "cachoeira":120, "palacio":500}
RENDA_BASE = {"casa": 0.02, "fazenda": 0.05, "elevador": 0.0, "silo": 0.1, "cachoeira": 0.2, "palacio": 1.0}

ITENS_CAVERNA = ["mineracao", "cristal", "forja", "laboratorio", "reator", "cripto"]

CUSTOS.update({
    "mineracao":   2_000,
    "cristal":     5_000,
    "forja":       8_000,
    "laboratorio": 15_000,
    "reator":      40_000,
    "cripto":      100_000,
})

XP_ITENS.update({
    "mineracao":   200,
    "cristal":     500,
    "forja":       800,
    "laboratorio": 1_500,
    "reator":      4_000,
    "cripto":      10_000,
})

RENDA_BASE.update({
    "mineracao":   0.5,    
    "cristal":     1.5,    
    "forja":       3.0,    
    "laboratorio": 7.0,    
    "reator":      20.0,   
    "cripto":      60.0,   
})