import pygame, sys
import os
from config import *
from mundo import GerenciadorMundo
from camera import Camera

# Inicialização do Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Voxel Tycoon Underground")
clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 22)
font_menu = pygame.font.SysFont("arial", 40)

# Música de fundo
if not pygame.mixer.music.get_busy():
    try:
        pygame.mixer.music.play(-1)
    except:
        pass

# Instâncias e Variáveis Globais
mundo = GerenciadorMundo()
camera = Camera()
arrastando = False
drag_start = (0, 0)
drag_offset_start = (0, 0)

estado = "menu"
dinheiro, populacao, nivel, xp, xp_max = 500, 0, 1, 0, 100
selected_index = 0
contagem_global = {item: 0 for item in ITENS}

def construir(gx, gy):
    global dinheiro, xp, populacao
    grid = mundo.get_grid_ativo()
    base = mundo.get_base_tile()
    item = ITENS[selected_index]

    if not (0 <= gx < COLS and 0 <= gy < ROWS):
        return

    if dinheiro >= CUSTOS[item]:
        if item == "elevador":
            if mundo.superficie[gy][gx] == "grama" and mundo.caverna[gy][gx] == "pedra":
                mundo.superficie[gy][gx] = "elevador"
                mundo.caverna[gy][gx] = "elevador"
            else:
                return
        else:
            if grid[gy][gx] == base:
                grid[gy][gx] = item
            else:
                return

        dinheiro -= CUSTOS[item]
        contagem_global[item] += 1
        xp += XP_ITENS[item]
        if item == "casa": populacao += 5
        if CLICK_SOUND: CLICK_SOUND.play()

def desenhar_painel():
    # Fundo do painel
    pygame.draw.rect(screen, (30, 34, 40), (MAP_WIDTH, 0, PANEL_WIDTH, HEIGHT))

    # --- Título do Jogo no Painel ---
    titulo_painel = font.render("V.T. UNDERGROUND", True, DOURADO)
    screen.blit(titulo_painel, (MAP_WIDTH + (PANEL_WIDTH // 2 - titulo_painel.get_width() // 2), 15))
    pygame.draw.line(screen, (70, 70, 80), (MAP_WIDTH + 15, 45), (WIDTH - 15, 45), 2)

    # Informação da Camada
    cor_camada = VERDE if mundo.camada_atual == "superficie" else DOURADO
    screen.blit(font.render(f"MAPA: {mundo.camada_atual.upper()}", True, cor_camada), (MAP_WIDTH + 20, 65))

    # Recursos
    recursos = [
        f"Dinheiro: ${int(dinheiro)}",
        f"População: {populacao}",
        f"Nível: {nivel}",
        f"XP: {xp}/{xp_max}"
    ]
    for i, txt in enumerate(recursos):
        screen.blit(font.render(txt, True, BRANCO), (MAP_WIDTH + 20, 105 + i*30))

    # Menu de Construção
    screen.blit(font.render("CONSTRUIR (1-6):", True, (150, 150, 150)), (MAP_WIDTH + 20, 250))
    for i, item in enumerate(ITENS):
        cor = DOURADO if i == selected_index else BRANCO
        screen.blit(font.render(f"{i+1}-{item.upper()} (${CUSTOS[item]})", True, cor), (MAP_WIDTH + 20, 285 + i*35))

# ---------------- LOOP PRINCIPAL ----------------
while True:
    mouse = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        # Comandos de Teclado
        if event.type == pygame.KEYDOWN:
            if pygame.K_1 <= event.key <= pygame.K_6:
                selected_index = event.key - pygame.K_1
            if event.key == pygame.K_ESCAPE:
                estado = "menu"
            if event.key == pygame.K_r and estado == "jogo":
                camera.resetar()

        # --- Lógica de Mouse: MENU ---
        if event.type == pygame.MOUSEBUTTONDOWN and estado == "menu":
            # Botão INICIAR (Centralizado)
            if WIDTH//2 - 150 < mouse[0] < WIDTH//2 + 150 and 330 < mouse[1] < 390:
                estado = "jogo"
            # Botão SAIR
            elif WIDTH//2 - 150 < mouse[0] < WIDTH//2 + 150 and 410 < mouse[1] < 470:
                pygame.quit(); sys.exit()

        # --- Lógica de Mouse: JOGO ---
        if estado == "jogo":
            # Arrastar câmera (Botão Direito)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if mouse[0] < MAP_WIDTH and event.button == 3:
                    arrastando = True
                    drag_start = mouse
                    drag_offset_start = (camera.offset_x, camera.offset_y)

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3:
                    arrastando = False

            if event.type == pygame.MOUSEMOTION and arrastando:
                dx = mouse[0] - drag_start[0]
                dy = mouse[1] - drag_start[1]
                camera.offset_x = drag_offset_start[0] + dx
                camera.offset_y = drag_offset_start[1] + dy
                camera.offset_x = max(-(COLS * GRID_SIZE - MAP_WIDTH), min(0, camera.offset_x))
                camera.offset_y = max(-(ROWS * GRID_SIZE - HEIGHT), min(0, camera.offset_y))

            # Construir ou Alternar Camada (Botão Esquerdo)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if mouse[0] < MAP_WIDTH:
                    gx, gy = camera.tela_para_mundo(mouse[0], mouse[1])
                    grid_atual = mundo.get_grid_ativo()
                    if 0 <= gx < COLS and 0 <= gy < ROWS:
                        if grid_atual[gy][gx] == "elevador":
                            mundo.alternar_camada()
                            if CLICK_SOUND: CLICK_SOUND.play()
                        else:
                            construir(gx, gy)

    # --- RENDERIZAÇÃO ---
    if estado == "menu":
        screen.fill((20, 20, 30))
        
        # Título Principal
        txt_titulo = font_menu.render("VOXEL TYCOON: UNDERGROUND", True, DOURADO)
        screen.blit(txt_titulo, (WIDTH//2 - txt_titulo.get_width()//2, 200))
        
        # Desenho Botão INICIAR
        pygame.draw.rect(screen, (50, 120, 50), (WIDTH//2-150, 330, 300, 60), border_radius=8)
        txt_iniciar = font_menu.render("INICIAR", True, BRANCO)
        screen.blit(txt_iniciar, (WIDTH//2 - txt_iniciar.get_width()//2, 335))

        # Desenho Botão SAIR
        pygame.draw.rect(screen, (150, 50, 50), (WIDTH//2-150, 410, 300, 60), border_radius=8)
        txt_sair = font_menu.render("SAIR", True, BRANCO)
        screen.blit(txt_sair, (WIDTH//2 - txt_sair.get_width()//2, 415))

    elif estado == "jogo":
        # Lógica de Economia (Renda por frame aproximada a 60 FPS)
        renda = (contagem_global["casa"]*2 + contagem_global["fazenda"]*10 + contagem_global["silo"]*25) / 60
        dinheiro += renda

        # Lógica de Level Up
        if xp >= xp_max:
            nivel += 1
            xp = 0
            xp_max = int(xp_max * 1.5)
            dinheiro += 500

        mundo.desenhar(screen, camera)
        desenhar_painel()

    pygame.display.flip()
    clock.tick(60)