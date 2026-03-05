import pygame
import sys

pygame.init()
pygame.mixer.init()

# ---------------- CONFIG ----------------
WIDTH, HEIGHT = 1200, 640
PANEL_WIDTH = 260
MAP_WIDTH = WIDTH - PANEL_WIDTH

GRID_SIZE = 64
COLS = MAP_WIDTH // GRID_SIZE
ROWS = HEIGHT // GRID_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini Tropico - Versão com Sprites")

clock = pygame.time.Clock()
FPS = 60

# ---------------- AUDIO ----------------
pygame.mixer.music.load("assets/musicatema.wav")
pygame.mixer.music.set_volume(0.4)
pygame.mixer.music.play(-1)

click_sound = pygame.mixer.Sound("assets/click.wav")

# ---------------- IMAGENS ----------------
grama_img = pygame.image.load("assets/grama.png").convert_alpha()
casa_img = pygame.image.load("assets/casa.png").convert_alpha()
fazenda_img = pygame.image.load("assets/fazenda.png").convert_alpha()
silo_img = pygame.image.load("assets/silo.png").convert_alpha()
cachoeira_img = pygame.image.load("assets/cachoeira.png").convert_alpha()
palacio_img = pygame.image.load("assets/palacio.png").convert_alpha()

imagens = {
    "grama": grama_img,
    "casa": casa_img,
    "fazenda": fazenda_img,
    "silo": silo_img,
    "cachoeira": cachoeira_img,
    "palacio": palacio_img
}

# ---------------- CORES ----------------
COR_PAINEL = (30, 34, 40)
COR_TEXTO = (255, 255, 255)
COR_SELECIONADO = (255, 215, 0)

# ---------------- DADOS ----------------
grid = [["grama" for _ in range(COLS)] for _ in range(ROWS)]

itens = ["casa", "fazenda", "silo", "cachoeira", "palacio"]
selected_index = 0

dinheiro = 1000
populacao = 0
felicidade = 50

font = pygame.font.SysFont("arial", 20)
font_titulo = pygame.font.SysFont("arial", 26, bold=True)

custos = {
    "casa": 100,
    "fazenda": 150,
    "silo": 200,
    "cachoeira": 300,
    "palacio": 1000
}

# ---------------- FUNÇÕES ----------------
def desenhar_mapa():
    for y in range(ROWS):
        for x in range(COLS):

            tile = grid[y][x]
            pos = (x * GRID_SIZE, y * GRID_SIZE)

            screen.blit(imagens["grama"], pos)

            if tile != "grama":
                screen.blit(imagens[tile], pos)


def desenhar_painel():
    pygame.draw.rect(screen, COR_PAINEL, (MAP_WIDTH, 0, PANEL_WIDTH, HEIGHT))

    titulo = font_titulo.render("Painel de Gestão", True, COR_TEXTO)
    screen.blit(titulo, (MAP_WIDTH + 20, 20))

    y = 80

    dinheiro_txt = font.render(f"Dinheiro: ${int(dinheiro)}", True, COR_TEXTO)
    screen.blit(dinheiro_txt, (MAP_WIDTH + 20, y))
    y += 30

    pop_txt = font.render(f"População: {populacao}", True, COR_TEXTO)
    screen.blit(pop_txt, (MAP_WIDTH + 20, y))
    y += 40

    # -------- BARRA DE FELICIDADE --------
    felicidade_txt = font.render("Felicidade:", True, COR_TEXTO)
    screen.blit(felicidade_txt, (MAP_WIDTH + 20, y))
    y += 25

    barra_x = MAP_WIDTH + 20
    barra_y = y
    barra_largura = 200
    barra_altura = 25

    pygame.draw.rect(screen, (70,70,70),
                     (barra_x, barra_y, barra_largura, barra_altura),
                     border_radius=6)

    if felicidade < 30:
        cor_barra = (200,50,50)
    elif felicidade < 70:
        cor_barra = (220,180,0)
    else:
        cor_barra = (0,200,100)

    largura = int((felicidade/100)*barra_largura)

    pygame.draw.rect(screen, cor_barra,
                     (barra_x, barra_y, largura, barra_altura),
                     border_radius=6)

    pygame.draw.rect(screen, (0,0,0),
                     (barra_x, barra_y, barra_largura, barra_altura),
                     2, border_radius=6)

    porcentagem = font.render(f"{int(felicidade)}%", True, COR_TEXTO)
    screen.blit(porcentagem, (barra_x+75, barra_y+3))

    y += 60
    # -------------------------------------

    for i,item in enumerate(itens):

        texto = f"{i+1} - {item.capitalize()} (${custos[item]})"

        if i == selected_index:
            render = font.render(texto, True, COR_SELECIONADO)
        else:
            render = font.render(texto, True, COR_TEXTO)

        screen.blit(render,(MAP_WIDTH+20,y))
        y += 35


def construir(x,y):

    global dinheiro,populacao,felicidade

    if x < 0 or y < 0 or x >= COLS or y >= ROWS:
        return

    if grid[y][x] != "grama":
        return

    item = itens[selected_index]
    custo = custos[item]

    if dinheiro >= custo:

        dinheiro -= custo
        grid[y][x] = item
        click_sound.play()

        if item == "casa":
            populacao += 5
            felicidade += 2

        elif item == "fazenda":
            dinheiro += 50
            felicidade += 1

        elif item == "silo":
            dinheiro += 100

        elif item == "cachoeira":
            felicidade += 10

        elif item == "palacio":
            felicidade += 20


def atualizar_economia():

    global dinheiro,felicidade

    dinheiro += populacao * 0.1
    felicidade -= populacao * 0.01

    felicidade = max(0,min(100,felicidade))


# ---------------- LOOP PRINCIPAL ----------------
while True:

    clock.tick(FPS)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:

            mx,my = pygame.mouse.get_pos()

            if mx < MAP_WIDTH:

                grid_x = mx // GRID_SIZE
                grid_y = my // GRID_SIZE

                construir(grid_x,grid_y)

        if event.type == pygame.KEYDOWN:

            if pygame.K_1 <= event.key <= pygame.K_5:
                selected_index = event.key - pygame.K_1

    atualizar_economia()

    desenhar_mapa()
    desenhar_painel()

    pygame.display.flip()