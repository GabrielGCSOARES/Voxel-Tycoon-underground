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
    itens_completos = ["grama","pedra","casa","fazenda","silo","cachoeira","palacio","elevador",
                       "mineracao", "cristal", "forja", "laboratorio", "reator", "cripto"]
    for k in itens_completos:
        surf = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
        if k == "grama": surf.fill((34, 139, 34))
        elif k == "pedra": surf.fill((100, 100, 100))
        elif k == "elevador": surf.fill((255, 215, 0))
        elif k == "mineracao":
            surf.fill((0, 0, 0, 0))
            # Pilha de pedras
            pygame.draw.circle(surf, (80, 80, 80), (20, 35), 10)
            pygame.draw.circle(surf, (60, 50, 50), (32, 35), 12)
            pygame.draw.circle(surf, (100, 100, 100), (12, 25), 8)
            pygame.draw.circle(surf, (90, 80, 70), (35, 20), 9)
            pygame.draw.circle(surf, (70, 75, 80), (24, 15), 11)
            # Entrada da mina na pilha
            pygame.draw.rect(surf, (20, 15, 10), (18, 22, 12, 18), border_radius=3)
            # Picareta esquecida encostada
            pygame.draw.line(surf, (120, 80, 40), (10, 40), (15, 25), 2)
            pygame.draw.polygon(surf, (180, 180, 180), [(13, 24), (19, 26), (16, 21)])

        elif k == "cristal":
            surf.fill((0, 0, 0, 0))
            # Brilho de fundo
            pygame.draw.circle(surf, (50, 100, 150, 100), (24, 24), 20)
            # Cristais 
            pygame.draw.polygon(surf, (100, 200, 255), [(24,4), (32,24), (24,44), (16,24)]) # Central maior
            pygame.draw.polygon(surf, (150, 230, 255), [(24,8), (28,24), (24,40), (20,24)]) # Reflexo central
            
            pygame.draw.polygon(surf, (80, 150, 255), [(12,16), (20,28), (12,40), (4,28)]) # Esquerdo
            pygame.draw.polygon(surf, (60, 120, 220), [(36,18), (44,30), (36,42), (28,30)]) # Direito

        elif k == "forja":
            surf.fill((0, 0, 0, 0))
            # Forno principal
            pygame.draw.rect(surf, (60, 55, 55), (8, 15, 32, 25), border_radius=4)
            # Boca do forno com fogo
            pygame.draw.rect(surf, (20, 10, 10), (14, 25, 20, 12), border_radius=2)
            pygame.draw.circle(surf, (255, 80, 0), (20, 32), 5)
            pygame.draw.circle(surf, (255, 200, 0), (26, 32), 4)
            # Chaminé
            pygame.draw.rect(surf, (50, 45, 45), (18, 5, 12, 10))
            # Bigorna do lado de fora
            pygame.draw.rect(surf, (40, 40, 45), (32, 35, 12, 8), border_radius=1)
            pygame.draw.rect(surf, (40, 40, 45), (34, 32, 8, 3))
            pygame.draw.polygon(surf, (40, 40, 45), [(32,32), (30,35), (34,35)])

        elif k == "laboratorio":
            surf.fill((0, 0, 0, 0))
            # Mesa
            pygame.draw.rect(surf, (120, 100, 80), (6, 30, 36, 12), border_radius=2)
            # Microscópio
            pygame.draw.rect(surf, (200, 200, 200), (10, 20, 6, 10))
            pygame.draw.polygon(surf, (180, 180, 180), [(13,20), (18,12), (10,12)])
            # Frasco principal
            pygame.draw.rect(surf, (100, 180, 255), (24, 18, 14, 12), border_radius=6)
            pygame.draw.rect(surf, (200, 200, 200), (29, 10, 4, 8))
            pygame.draw.circle(surf, (100, 255, 255), (28, 8), 2)
            pygame.draw.circle(surf, (150, 255, 255), (32, 4), 3)

        elif k == "reator":
            surf.fill((0, 0, 0, 0))
            # Tanque
            pygame.draw.rect(surf, (80, 90, 80), (10, 8, 28, 32), border_radius=8)
            pygame.draw.rect(surf, (50, 60, 50), (6, 12, 36, 4))
            pygame.draw.rect(surf, (50, 60, 50), (6, 32, 36, 4))
            # Núcleo neon
            pygame.draw.circle(surf, (0, 255, 100), (24, 24), 10)
            pygame.draw.circle(surf, (200, 255, 200), (24, 24), 4)
            # Fio conectado
            pygame.draw.line(surf, (0, 0, 0), (24, 8), (24, 0), 2)

        elif k == "cripto":
            surf.fill((0, 0, 0, 0))
            # Servidores (racks)
            for rack_x in [6, 18, 30]:
                pygame.draw.rect(surf, (40, 40, 50), (rack_x, 8, 10, 32), border_radius=2)
                # Leds piscando
                for led_y in [12, 18, 24, 30, 36]:
                    cor = (0, 255, 0) if (rack_x + led_y) % 3 == 0 else (0, 150, 255)
                    if (rack_x + led_y) % 5 == 0: cor = (255, 0, 0)
                    pygame.draw.line(surf, cor, (rack_x + 2, led_y), (rack_x + 8, led_y), 2)
            # Cabo ligando racks
            pygame.draw.line(surf, (30, 30, 30), (16, 40), (30, 40), 3)

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
ITENS   = ["casa", "fazenda", "silo", "cachoeira", "palacio"]
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