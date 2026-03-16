import pygame, sys
import os
# O 'from config import *' já traz a 'screen', as 'IMAGENS' e o 'CLICK_SOUND'
from config import *
from mundo import GerenciadorMundo

pygame.display.set_caption("Voxel Tycoon Underground")
clock = pygame.time.Clock()

# Fontes
font = pygame.font.SysFont("arial", 22)
font_menu = pygame.font.SysFont("arial", 40)

# Iniciar música se não estiver tocando
if not pygame.mixer.music.get_busy():
    try:
        pygame.mixer.music.play(-1)
    except:
        pass

# Objetos e Estado do Jogo
mundo = GerenciadorMundo()
estado = "menu"
dinheiro, populacao, nivel, xp, xp_max = 500, 0, 1, 0, 100 
selected_index = 0
contagem_global = {item: 0 for item in ITENS}

def construir(gx, gy):
    global dinheiro, xp, populacao
    grid = mundo.get_grid_ativo()
    base = mundo.get_base_tile()
    item = ITENS[selected_index]

    if dinheiro >= CUSTOS[item]:
        # LÓGICA ESPECIAL DO ELEVADOR: Ele precisa aparecer nos dois mundos
        if item == "elevador":
            # Só constrói se o espaço estiver livre em cima E embaixo
            if mundo.superficie[gy][gx] == "grama" and mundo.caverna[gy][gx] == "pedra":
                mundo.superficie[gy][gx] = "elevador"
                mundo.caverna[gy][gx] = "elevador"
            else:
                return # Espaço ocupado
        else:
            # Construção comum
            if grid[gy][gx] == base:
                grid[gy][gx] = item
            else:
                return # Já tem algo construído aqui

        # Se chegou aqui, a construção foi um sucesso!
        dinheiro -= CUSTOS[item]
        contagem_global[item] += 1
        xp += XP_ITENS[item]
        if item == "casa": populacao += 5
        if CLICK_SOUND: CLICK_SOUND.play()

def desenhar_painel():
    # Fundo do Painel
    pygame.draw.rect(screen, (30, 34, 40), (MAP_WIDTH, 0, PANEL_WIDTH, HEIGHT))
    
    # Texto da Camada Atual
    cor_camada = VERDE if mundo.camada_atual == "superficie" else DOURADO
    camada_txt = font.render(f"MAPA: {mundo.camada_atual.upper()}", True, cor_camada)
    screen.blit(camada_txt, (MAP_WIDTH + 20, 20))
    
    # Status Financeiro e Social
    status = [
        f"Dinheiro: ${int(dinheiro)}", 
        f"População: {populacao}", 
        f"Nível: {nivel}",
        f"XP: {xp}/{xp_max}"
    ]
    for i, txt in enumerate(status):
        render = font.render(txt, True, BRANCO)
        screen.blit(render, (MAP_WIDTH + 20, 70 + i*30))
    
    # Menu de Construção
    titulo_itens = font.render("CONSTRUIR (Teclas 1-6):", True, (150, 150, 150))
    screen.blit(titulo_itens, (MAP_WIDTH + 20, 220))
    
    for i, item in enumerate(ITENS):
        cor = DOURADO if i == selected_index else BRANCO
        txt = font.render(f"{i+1}-{item.upper()} (${CUSTOS[item]})", True, cor)
        screen.blit(txt, (MAP_WIDTH + 20, 250 + i*35))

# ---------------- LOOP PRINCIPAL ----------------
while True:
    mouse = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
            
        if event.type == pygame.KEYDOWN:
            if pygame.K_1 <= event.key <= pygame.K_6:
                selected_index = event.key - pygame.K_1
            # ESC para voltar ao menu
            if event.key == pygame.K_ESCAPE:
                estado = "menu"

        if event.type == pygame.MOUSEBUTTONDOWN and estado == "jogo":
            # Clique no Mapa (Lado esquerdo)
            if mouse[0] < MAP_WIDTH and event.button == 1:
                gx, gy = mouse[0] // GRID_SIZE, mouse[1] // GRID_SIZE
                grid_atual = mundo.get_grid_ativo()

                # INTERAÇÃO: Se clicar em um elevador JÁ EXISTENTE, ele troca de mapa
                if grid_atual[gy][gx] == "elevador":
                    mundo.alternar_camada()
                    if CLICK_SOUND: CLICK_SOUND.play()
                else:
                    # Se não for um elevador, tenta construir o item selecionado
                    construir(gx, gy)
        
        if event.type == pygame.MOUSEBUTTONDOWN and estado == "menu":
            # Botão Iniciar no Menu
            if WIDTH//2 - 150 < mouse[0] < WIDTH//2 + 150 and 350 < mouse[1] < 420:
                estado = "jogo"

    # --- LÓGICA DE ATUALIZAÇÃO ---
    if estado == "menu":
        screen.fill((20, 20, 30))
        txt = font_menu.render("VOXEL TYCOON: UNDERGROUND", True, DOURADO)
        screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 200))
        
        pygame.draw.rect(screen, CINZA, (WIDTH//2-150, 350, 300, 70), border_radius=8)
        btn_txt = font_menu.render("INICIAR", True, BRANCO)
        screen.blit(btn_txt, (WIDTH//2 - btn_txt.get_width()//2, 365))
        
    elif estado == "jogo":
        # Renda Passiva baseada nas construções
        renda = (contagem_global["casa"]*2 + contagem_global["fazenda"]*10 + contagem_global["silo"]*25) / 60
        dinheiro += renda
        
        # Subir de Nível (Exemplo básico)
        if xp >= xp_max:
            nivel += 1
            xp = 0
            xp_max = int(xp_max * 1.5)
            dinheiro += 500 # Bônus de nível

        # --- DESENHO ---
        mundo.desenhar(screen)
        desenhar_painel()

    pygame.display.flip()
    clock.tick(60)