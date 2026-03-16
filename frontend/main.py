import pygame, sys
import os
from config import *
from mundo import GerenciadorMundo
from camera import Camera

pygame.display.set_caption("Voxel Tycoon Underground")
clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 22)
font_menu = pygame.font.SysFont("arial", 40)

if not pygame.mixer.music.get_busy():
    try:
        pygame.mixer.music.play(-1)
    except:
        pass

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
    pygame.draw.rect(screen, (30, 34, 40), (MAP_WIDTH, 0, PANEL_WIDTH, HEIGHT))

    cor_camada = VERDE if mundo.camada_atual == "superficie" else DOURADO
    screen.blit(font.render(f"MAPA: {mundo.camada_atual.upper()}", True, cor_camada), (MAP_WIDTH + 20, 20))

    for i, txt in enumerate([
        f"Dinheiro: ${int(dinheiro)}",
        f"População: {populacao}",
        f"Nível: {nivel}",
        f"XP: {xp}/{xp_max}"
    ]):
        screen.blit(font.render(txt, True, BRANCO), (MAP_WIDTH + 20, 70 + i*30))

    screen.blit(font.render("CONSTRUIR (Teclas 1-6):", True, (150, 150, 150)), (MAP_WIDTH + 20, 220))

    for i, item in enumerate(ITENS):
        cor = DOURADO if i == selected_index else BRANCO
        screen.blit(font.render(f"{i+1}-{item.upper()} (${CUSTOS[item]})", True, cor), (MAP_WIDTH + 20, 250 + i*35))

# ---------------- LOOP PRINCIPAL ----------------
while True:
    mouse = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        if event.type == pygame.KEYDOWN:
            if pygame.K_1 <= event.key <= pygame.K_6:
                selected_index = event.key - pygame.K_1
            if event.key == pygame.K_ESCAPE:
                estado = "menu"
            if event.key == pygame.K_r and estado == "jogo":
                camera.resetar()

        # Iniciar arrasto com botão direito
        if event.type == pygame.MOUSEBUTTONDOWN and estado == "jogo":
            if mouse[0] < MAP_WIDTH and event.button == 3:
                arrastando = True
                drag_start = mouse
                drag_offset_start = (camera.offset_x, camera.offset_y)

        # Soltar arrasto
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 3:
                arrastando = False

        # Mover câmera enquanto arrasta
        if event.type == pygame.MOUSEMOTION and arrastando:
            dx = mouse[0] - drag_start[0]
            dy = mouse[1] - drag_start[1]
            camera.offset_x = drag_offset_start[0] + dx
            camera.offset_y = drag_offset_start[1] + dy
            # Aplica limites
            camera.offset_x = max(-(COLS * GRID_SIZE - MAP_WIDTH), min(0, camera.offset_x))
            camera.offset_y = max(-(ROWS * GRID_SIZE - HEIGHT),    min(0, camera.offset_y))

        # Clique esquerdo: construir
        if event.type == pygame.MOUSEBUTTONDOWN and estado == "jogo":
            if mouse[0] < MAP_WIDTH and event.button == 1:
                gx, gy = camera.tela_para_mundo(mouse[0], mouse[1])
                grid_atual = mundo.get_grid_ativo()
                if 0 <= gx < COLS and 0 <= gy < ROWS:
                    if grid_atual[gy][gx] == "elevador":
                        mundo.alternar_camada()
                        if CLICK_SOUND: CLICK_SOUND.play()
                    else:
                        construir(gx, gy)

        if event.type == pygame.MOUSEBUTTONDOWN and estado == "menu":
            if WIDTH//2 - 150 < mouse[0] < WIDTH//2 + 150 and 350 < mouse[1] < 420:
                estado = "jogo"

    if estado == "menu":
        screen.fill((20, 20, 30))
        txt = font_menu.render("VOXEL TYCOON: UNDERGROUND", True, DOURADO)
        screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 200))
        pygame.draw.rect(screen, CINZA, (WIDTH//2-150, 350, 300, 70), border_radius=8)
        screen.blit(font_menu.render("INICIAR", True, BRANCO), (WIDTH//2 - font_menu.size("INICIAR")[0]//2, 365))

    elif estado == "jogo":
        renda = (contagem_global["casa"]*2 + contagem_global["fazenda"]*10 + contagem_global["silo"]*25) / 60
        dinheiro += renda

        if xp >= xp_max:
            nivel += 1
            xp = 0
            xp_max = int(xp_max * 1.5)
            dinheiro += 500

        mundo.desenhar(screen, camera)
        desenhar_painel()

    pygame.display.flip()
    clock.tick(60)