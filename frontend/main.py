import pygame, sys, os
from config import *
from mundo import GerenciadorMundo
from camera import Camera

# ---------------- CONFIGURAÇÕES INICIAIS ----------------
clock = pygame.time.Clock()

try:
    font = pygame.font.SysFont("arial", 22)
    font_menu = pygame.font.SysFont("arial", 45, bold=True)
except:
    font = pygame.font.Font(None, 24)
    font_menu = pygame.font.Font(None, 45)

# ---------------- ESTADO DO JOGO ----------------
mundo = GerenciadorMundo()
camera = Camera()
estado = "menu"
dinheiro, populacao, nivel, xp, xp_max = 500, 0, 1, 0, 100
selected_index = 0
arrastando = False
drag_start = (0, 0)
drag_offset_start = (0, 0)

# ---------------- AUXILIARES DE UI ----------------
def desenhar_botao_menu(texto, y_pos, mouse_pos):
    largura_btn, altura_btn = 300, 60
    x_pos = WIDTH // 2 - largura_btn // 2
    
    # Detecção de Hover (mouse em cima)
    sobre_botao = x_pos < mouse_pos[0] < x_pos + largura_btn and y_pos < mouse_pos[1] < y_pos + altura_btn
    cor_fundo = (60, 170, 60) if sobre_botao else (40, 40, 50)
    
    # Desenho
    pygame.draw.rect(screen, cor_fundo, (x_pos, y_pos, largura_btn, altura_btn), border_radius=10)
    pygame.draw.rect(screen, BRANCO, (x_pos, y_pos, largura_btn, altura_btn), 2, border_radius=10)
    
    txt_surf = font.render(texto, True, BRANCO)
    screen.blit(txt_surf, (WIDTH // 2 - txt_surf.get_width() // 2, y_pos + altura_btn // 2 - txt_surf.get_height() // 2))
    
    return sobre_botao

def desenhar_painel():
    pygame.draw.rect(screen, (30, 34, 40), (MAP_WIDTH, 0, PANEL_WIDTH, HEIGHT))
    cor_camada = VERDE if mundo.camada_atual == "superficie" else DOURADO
    screen.blit(font.render(f"MAPA: {mundo.camada_atual.upper()}", True, cor_camada), (MAP_WIDTH + 20, 65))
    
    recursos = [f"Dinheiro: ${int(dinheiro)}", f"População: {populacao}", f"XP: {xp}/{xp_max}"]
    for i, txt in enumerate(recursos):
        screen.blit(font.render(txt, True, BRANCO), (MAP_WIDTH + 20, 105 + i * 30))
    
    screen.blit(font.render("CONSTRUIR (1-6):", True, (150, 150, 150)), (MAP_WIDTH + 20, 250))
    for i, item in enumerate(ITENS):
        cor = DOURADO if i == selected_index else BRANCO
        screen.blit(font.render(f"{i+1}-{item.upper()}", True, cor), (MAP_WIDTH + 20, 285 + i * 35))

# ---------------- LOOP PRINCIPAL ----------------
while True:
    mouse_pos = pygame.mouse.get_pos()
    screen.fill((15, 15, 20)) # Limpa a tela a cada frame

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
            
        if event.type == pygame.KEYDOWN:
            if pygame.K_1 <= event.key <= pygame.K_6: selected_index = event.key - pygame.K_1
            if event.key == pygame.K_ESCAPE: estado = "menu"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if estado == "menu":
                # Lógica de clique nos botões do menu
                if WIDTH // 2 - 150 < mouse_pos[0] < WIDTH // 2 + 150:
                    if 300 < mouse_pos[1] < 360: # Botão Iniciar
                        estado = "jogo"
                        if CLICK_SOUND: CLICK_SOUND.play()
                    elif 380 < mouse_pos[1] < 440: # Botão Sair
                        pygame.quit(); sys.exit()

            elif estado == "jogo" and mouse_pos[0] < MAP_WIDTH:
                gx, gy = camera.tela_para_mundo(mouse_pos[0], mouse_pos[1])
                grid = mundo.get_grid_ativo()
                
                if grid[gy][gx] == "elevador":
                    mundo.alternar_camada()
                else:
                    # Função construir simplificada
                    item = ITENS[selected_index]
                    if dinheiro >= CUSTOS[item] and grid[gy][gx] == mundo.get_base_tile():
                        if item == "elevador":
                            mundo.superficie[gy][gx] = "elevador"
                            mundo.caverna[gy][gx] = "elevador"
                        else:
                            grid[gy][gx] = item
                        dinheiro -= CUSTOS[item]
                        xp += XP_ITENS[item]
                        if CLICK_SOUND: CLICK_SOUND.play()

        # Câmera (Botão Direito)
        if estado == "jogo":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                arrastando = True
                drag_start = mouse_pos
                drag_offset_start = (camera.offset_x, camera.offset_y)
            if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                arrastando = False

    if arrastando:
        camera.offset_x = drag_offset_start[0] + (mouse_pos[0] - drag_start[0])
        camera.offset_y = drag_offset_start[1] + (mouse_pos[1] - drag_start[1])

    # ---------------- RENDERIZAÇÃO ----------------
    if estado == "menu":
        titulo = font_menu.render("VOXEL TYCOON", True, DOURADO)
        screen.blit(titulo, (WIDTH // 2 - titulo.get_width() // 2, 150))
        
        desenhar_botao_menu("INICIAR JOGO", 300, mouse_pos)
        desenhar_botao_menu("SAIR PARA DESKTOP", 380, mouse_pos)
    
    elif estado == "jogo":
        dinheiro += 0.02 # Renda passiva
        mundo.desenhar(screen, camera)
        desenhar_painel()

    pygame.display.flip()
    clock.tick(60)