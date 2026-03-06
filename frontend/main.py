import pygame
import sys

pygame.init()
pygame.mixer.init()

# ---------------- TELA ----------------
info = pygame.display.Info()
WIDTH = info.current_w
HEIGHT = info.current_h

PANEL_WIDTH = int(WIDTH * 0.20)
MAP_WIDTH = WIDTH - PANEL_WIDTH

GRID_SIZE = int(HEIGHT / 10)

COLS = MAP_WIDTH // GRID_SIZE
ROWS = HEIGHT // GRID_SIZE

MAP_WIDTH = COLS * GRID_SIZE

screen = pygame.display.set_mode((MAP_WIDTH + PANEL_WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Voxel-Tycoon-Underground")

clock = pygame.time.Clock()
FPS = 60

# ---------------- AUDIO ----------------
pygame.mixer.music.load("assets/musicatema.wav")
pygame.mixer.music.set_volume(0.4)
pygame.mixer.music.play(-1)

click_sound = pygame.mixer.Sound("assets/click.wav")

# ---------------- IMAGENS ----------------
def escalar(img):
    return pygame.transform.scale(img,(GRID_SIZE,GRID_SIZE))

grama_img = escalar(pygame.image.load("assets/grama.png").convert_alpha())
casa_img = escalar(pygame.image.load("assets/casa.png").convert_alpha())
fazenda_img = escalar(pygame.image.load("assets/fazenda.png").convert_alpha())
silo_img = escalar(pygame.image.load("assets/silo.png").convert_alpha())
cachoeira_img = escalar(pygame.image.load("assets/cachoeira.png").convert_alpha())
palacio_img = escalar(pygame.image.load("assets/palacio.png").convert_alpha())

imagens = {
    "grama": grama_img,
    "casa": casa_img,
    "fazenda": fazenda_img,
    "silo": silo_img,
    "cachoeira": cachoeira_img,
    "palacio": palacio_img
}

# ---------------- CORES ----------------
BRANCO = (255,255,255)
PRETO = (0,0,0)
CINZA = (40,40,40)
DOURADO = (255,215,0)
VERDE = (50,200,80)

# ---------------- FONTES ----------------
font = pygame.font.SysFont("arial",24)
font_big = pygame.font.SysFont("arial",60)
font_menu = pygame.font.SysFont("arial",40)

# ---------------- RESETAR JOGO ----------------
def resetar_jogo():

    global grid,dinheiro,populacao,felicidade,selected_index
    global nivel,xp,xp_max
    global contagem

    grid = [["grama" for _ in range(COLS)] for _ in range(ROWS)]

    dinheiro = 150
    populacao = 0
    felicidade = 50
    selected_index = 0

    nivel = 1
    xp = 0
    xp_max = 100

    contagem = {
        "casa":0,
        "fazenda":0,
        "silo":0,
        "cachoeira":0,
        "palacio":0
    }

resetar_jogo()

# ---------------- XP POR ITEM (ajustado) ----------------
xp_itens = {
    "casa":20,
    "fazenda":40,
    "silo":80,
    "cachoeira":120,
    "palacio":500
}

# ---------------- DADOS ----------------
itens = ["casa","fazenda","silo","cachoeira","palacio"]

custos = {
    "casa":100,
    "fazenda":150,
    "silo":200,
    "cachoeira":300,
    "palacio":1000
}

# ---------------- ESTADOS ----------------
MENU = "menu"
JOGO = "jogo"
PAUSE = "pause"

estado = MENU

# ---------------- BOTÃO ----------------
def desenhar_botao(texto,x,y,w,h):

    pygame.draw.rect(screen,CINZA,(x,y,w,h),border_radius=8)

    txt = font_menu.render(texto,True,BRANCO)
    screen.blit(txt,(x+w/2-txt.get_width()/2,y+h/2-txt.get_height()/2))

    return pygame.Rect(x,y,w,h)

# ---------------- MENU INICIAL ----------------
def tela_menu():

    screen.fill((20,20,30))

    titulo = font_big.render("Voxel-Tycoon",True,BRANCO)
    screen.blit(titulo,(WIDTH/2-titulo.get_width()/2,150))

    subtitulo = font_menu.render("Underground",True,DOURADO)
    screen.blit(subtitulo,(WIDTH/2-subtitulo.get_width()/2,230))

    iniciar = desenhar_botao("Iniciar",WIDTH/2-150,350,300,70)
    sair = desenhar_botao("Sair",WIDTH/2-150,450,300,70)

    return iniciar,sair

# ---------------- MENU PAUSE ----------------
def tela_pause():

    overlay = pygame.Surface((WIDTH,HEIGHT))
    overlay.set_alpha(180)
    overlay.fill(PRETO)

    screen.blit(overlay,(0,0))

    titulo = font_big.render("Menu",True,BRANCO)
    screen.blit(titulo,(WIDTH/2-titulo.get_width()/2,150))

    continuar = desenhar_botao("Continuar",WIDTH/2-150,320,300,70)
    reiniciar = desenhar_botao("Reiniciar",WIDTH/2-150,420,300,70)
    sair = desenhar_botao("Sair",WIDTH/2-150,520,300,70)

    return continuar,reiniciar,sair

# ---------------- MAPA ----------------
def desenhar_mapa():

    for y in range(ROWS):
        for x in range(COLS):

            tile = grid[y][x]
            pos = (x*GRID_SIZE,y*GRID_SIZE)

            screen.blit(imagens["grama"],pos)

            if tile != "grama":
                screen.blit(imagens[tile],pos)

# ---------------- PAINEL ----------------
def desenhar_painel():

    pygame.draw.rect(screen,(30,34,40),(MAP_WIDTH,0,PANEL_WIDTH,HEIGHT))

    titulo = font_menu.render("Voxel Tycoon",True,DOURADO)
    screen.blit(titulo,(MAP_WIDTH + PANEL_WIDTH/2 - titulo.get_width()/2,20))

    subtitulo = font.render("Underground",True,BRANCO)
    screen.blit(subtitulo,(MAP_WIDTH + PANEL_WIDTH/2 - subtitulo.get_width()/2,60))

    y = 120

    dinheiro_txt = font.render(f"Dinheiro: ${int(dinheiro)}",True,BRANCO)
    screen.blit(dinheiro_txt,(MAP_WIDTH+20,y))
    y += 40

    pop_txt = font.render(f"População: {populacao}",True,BRANCO)
    screen.blit(pop_txt,(MAP_WIDTH+20,y))
    y += 40

    nivel_txt = font.render(f"Nível: {nivel}",True,DOURADO)
    screen.blit(nivel_txt,(MAP_WIDTH+20,y))
    y += 30

    barra_x = MAP_WIDTH+20
    barra_y = y
    barra_w = PANEL_WIDTH-40
    barra_h = 20

    pygame.draw.rect(screen,(70,70,70),(barra_x,barra_y,barra_w,barra_h),border_radius=6)

    progresso = xp/xp_max
    pygame.draw.rect(screen,VERDE,(barra_x,barra_y,barra_w*progresso,barra_h),border_radius=6)

    xp_txt = font.render(f"{int(xp)}/{xp_max} XP",True,BRANCO)
    screen.blit(xp_txt,(barra_x+barra_w/2-xp_txt.get_width()/2,barra_y-2))

    y += 60

    for i,item in enumerate(itens):

        texto = f"{i+1} - {item} (${custos[item]})"

        if i == selected_index:
            render = font.render(texto,True,DOURADO)
        else:
            render = font.render(texto,True,BRANCO)

        screen.blit(render,(MAP_WIDTH+20,y))
        y += 35

# ---------------- NIVEL ----------------
def ganhar_xp(valor):

    global xp,nivel,xp_max,grid,contagem,populacao,felicidade

    xp += valor

    while xp >= xp_max:
        xp -= xp_max
        nivel += 1
        xp_max = int(xp_max * 1.5)

        if nivel >= 10:
            xp *= 2
            grid = [["grama" for _ in range(COLS)] for _ in range(ROWS)]
            contagem = {key:0 for key in contagem}
            populacao = 0
            felicidade = 50
            nivel = 1
            xp_max = 100
            click_sound.play()

# ---------------- CONSTRUIR ----------------
def construir(x,y):

    global dinheiro,populacao,felicidade

    if grid[y][x] != "grama":
        return

    item = itens[selected_index]
    custo = custos[item]

    if dinheiro >= custo:

        dinheiro -= custo
        grid[y][x] = item
        contagem[item] += 1

        click_sound.play()

        ganhar_xp(xp_itens[item])

        if item == "casa":
            populacao += 5
        if item == "cachoeira":
            felicidade += 10

# ---------------- ECONOMIA ----------------
def atualizar():

    global dinheiro

    renda = (
        contagem["casa"] * 5 +
        contagem["fazenda"] * 20 +
        contagem["silo"] * 50 +
        contagem["cachoeira"] * 75 +
        contagem["palacio"] * 500
    )

    dinheiro += renda / FPS

# ---------------- LOOP PRINCIPAL ----------------
while True:

    clock.tick(FPS)

    mouse = pygame.mouse.get_pos()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:

                if estado == JOGO:
                    estado = PAUSE
                elif estado == PAUSE:
                    estado = JOGO

            if pygame.K_1 <= event.key <= pygame.K_5:
                selected_index = event.key - pygame.K_1

        if event.type == pygame.MOUSEBUTTONDOWN:

            if estado == JOGO:

                mx,my = mouse

                if mx < MAP_WIDTH:

                    grid_x = mx // GRID_SIZE
                    grid_y = my // GRID_SIZE

                    construir(grid_x,grid_y)

    if estado == MENU:

        iniciar,sair = tela_menu()

        if pygame.mouse.get_pressed()[0]:

            if iniciar.collidepoint(mouse):
                estado = JOGO

            if sair.collidepoint(mouse):
                pygame.quit()
                sys.exit()

    elif estado == JOGO:

        atualizar()
        desenhar_mapa()
        desenhar_painel()

    elif estado == PAUSE:

        desenhar_mapa()
        desenhar_painel()

        continuar,reiniciar,sair = tela_pause()

        if pygame.mouse.get_pressed()[0]:

            if continuar.collidepoint(mouse):
                estado = JOGO

            if reiniciar.collidepoint(mouse):
                resetar_jogo()
                estado = JOGO

            if sair.collidepoint(mouse):
                pygame.quit()
                sys.exit()

    pygame.display.flip()