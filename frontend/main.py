import pygame, sys, os, math
from config import *
from mundo import GerenciadorMundo
from camera import Camera
from npcs import GerenciadorNPCs

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
gerenciador_npcs = GerenciadorNPCs()
estado = "menu"
dinheiro, populacao, nivel, xp, xp_max = 500, 0, 1, 0, 100
renda_passiva = 0.0

selected_index = 0
arrastando = False
drag_start = (0, 0)
drag_offset_start = (0, 0)

construcao_selecionada = None
mensagem_tela = ""
tempo_mensagem = 0

# ---------------- AUXILIARES DE UI ----------------
def desenhar_botao_menu(texto, y_pos, mouse_pos):
    largura_btn, altura_btn = 300, 60
    x_pos = WIDTH // 2 - largura_btn // 2

    sobre_botao = x_pos < mouse_pos[0] < x_pos + largura_btn and y_pos < mouse_pos[1] < y_pos + altura_btn
    cor_fundo = (60, 170, 60) if sobre_botao else (40, 40, 50)

    pygame.draw.rect(screen, cor_fundo, (x_pos, y_pos, largura_btn, altura_btn), border_radius=10)
    pygame.draw.rect(screen, BRANCO, (x_pos, y_pos, largura_btn, altura_btn), 2, border_radius=10)

    txt_surf = font.render(texto, True, BRANCO)
    screen.blit(txt_surf, (WIDTH // 2 - txt_surf.get_width() // 2, y_pos + altura_btn // 2 - txt_surf.get_height() // 2))

    return sobre_botao

def desenhar_painel():
    pygame.draw.rect(screen, (30, 34, 40), (MAP_WIDTH, 0, PANEL_WIDTH, HEIGHT))
    cor_camada = VERDE if mundo.camada_atual == "superficie" else DOURADO
    screen.blit(font.render(f"MAPA: {mundo.camada_atual.upper()}", True, cor_camada), (MAP_WIDTH + 20, 65))

    ganho_segundo = renda_passiva * 60
    recursos = [
        f"Dinheiro: ${int(dinheiro)}",
        f"Ganho: ${ganho_segundo:.1f}/s",
        f"Nível: {nivel}",
        f"XP: {xp}/{xp_max}",
        f"População: {populacao}"
    ]
    for i, txt in enumerate(recursos):
        screen.blit(font.render(txt, True, BRANCO), (MAP_WIDTH + 20, 105 + i * 30))

    lista_ativa = ITENS_CAVERNA if mundo.camada_atual != "superficie" else ITENS
    screen.blit(font.render("CONSTRUIR (1-6):", True, (150, 150, 150)), (MAP_WIDTH + 20, 270))
    for i, item in enumerate(lista_ativa):
        custo = CUSTOS[item]
        if i == selected_index:
            cor = DOURADO
        elif dinheiro < custo:
            cor = (180, 60, 60)
        else:
            cor = BRANCO
        screen.blit(font.render(f"{i+1}-{item.upper()}  ${custo:,}", True, cor), (MAP_WIDTH + 20, 305 + i * 35))

def desenhar_modal_upgrade():
    if not construcao_selecionada:
        return None

    gx, gy, item, nivel_atual = construcao_selecionada
    largura, altura = 350, 250
    cx, cy = WIDTH // 2 - largura // 2, HEIGHT // 2 - altura // 2

    pygame.draw.rect(screen, (20, 25, 30), (cx, cy, largura, altura), border_radius=15)
    pygame.draw.rect(screen, DOURADO, (cx, cy, largura, altura), 3, border_radius=15)

    screen.blit(font_menu.render(item.upper(), True, BRANCO), (cx + 20, cy + 20))
    screen.blit(font.render(f"Nível Atual: {nivel_atual}", True, (200, 200, 200)), (cx + 20, cy + 70))

    multiplicador_atual = 1.5 ** (nivel_atual - 1)
    multiplicador_prox  = 1.5 ** nivel_atual
    renda_atual   = RENDA_BASE.get(item, 0) * multiplicador_atual * 60
    renda_prox    = RENDA_BASE.get(item, 0) * multiplicador_prox  * 60
    custo_upgrade = CUSTOS[item] * (2 ** nivel_atual)

    screen.blit(font.render(f"Renda: ${renda_atual:.1f}/s -> ${renda_prox:.1f}/s", True, VERDE), (cx + 20, cy + 100))
    screen.blit(font.render(f"Custo Upgrade: ${custo_upgrade:,}", True, DOURADO), (cx + 20, cy + 130))

    btn_upgrade = pygame.Rect(cx + 20,  cy + 180, 140, 40)
    btn_fechar  = pygame.Rect(cx + 190, cy + 180, 140, 40)

    cor_up = VERDE if dinheiro >= custo_upgrade else CINZA
    pygame.draw.rect(screen, cor_up,          btn_upgrade, border_radius=5)
    pygame.draw.rect(screen, (200, 50, 50),   btn_fechar,  border_radius=5)

    screen.blit(font.render("Evoluir", True, BRANCO), (btn_upgrade.x + 35, btn_upgrade.y + 10))
    screen.blit(font.render("Fechar",  True, BRANCO), (btn_fechar.x  + 40, btn_fechar.y  + 10))

    return {
        "upgrade": btn_upgrade, "fechar": btn_fechar,
        "custo": custo_upgrade, "gx": gx, "gy": gy,
        "item": item, "nivel": nivel_atual
    }

# ---------------- LOOP PRINCIPAL ----------------
while True:
    mouse_pos = pygame.mouse.get_pos()

    tempo = pygame.time.get_ticks() / 1000.0
    if estado == "jogo" and mundo.camada_atual == "superficie":
        screen.fill((20, 100, 150))
        espacamento_y, espacamento_x = 40, 60
        start_y = int(camera.offset_y) % espacamento_y
        start_x = int(camera.offset_x) % espacamento_x
        for y in range(start_y - espacamento_y, HEIGHT + espacamento_y, espacamento_y):
            mundo_y = y - camera.offset_y
            for x in range(start_x - espacamento_x, MAP_WIDTH + espacamento_x, espacamento_x):
                mundo_x = x - camera.offset_x
                deslocamento_x = math.sin(tempo * 1.5 + mundo_y * 0.05) * 15
                deslocamento_y = math.cos(tempo * 2.0 + mundo_x * 0.05) * 8
                onda_x = x + deslocamento_x
                onda_y = y + deslocamento_y
                pygame.draw.line(screen, (40, 140, 190), (onda_x, onda_y), (onda_x + 20, onda_y), 3)
                pygame.draw.line(screen, (60, 160, 210), (onda_x + 5, onda_y + 3), (onda_x + 15, onda_y + 3), 2)
    else:
        screen.fill((15, 15, 20))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        if event.type == pygame.KEYDOWN:
            if pygame.K_1 <= event.key <= pygame.K_6:
                selected_index = event.key - pygame.K_1
            if event.key == pygame.K_ESCAPE:
                if construcao_selecionada:
                    construcao_selecionada = None
                else:
                    estado = "menu"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if estado == "menu":
                if WIDTH // 2 - 150 < mouse_pos[0] < WIDTH // 2 + 150:
                    if 300 < mouse_pos[1] < 360:
                        estado = "jogo"
                        if CLICK_SOUND: CLICK_SOUND.play()
                    elif 380 < mouse_pos[1] < 440:
                        pygame.quit(); sys.exit()

            elif estado == "jogo":
                if construcao_selecionada:
                    botoes = desenhar_modal_upgrade()
                    if botoes:
                        if botoes["fechar"].collidepoint(mouse_pos):
                            construcao_selecionada = None
                            if CLICK_SOUND: CLICK_SOUND.play()
                        elif botoes["upgrade"].collidepoint(mouse_pos) and dinheiro >= botoes["custo"]:
                            dinheiro -= botoes["custo"]
                            grid_up = mundo.get_upgrades_ativo()
                            grid_up[botoes["gy"]][botoes["gx"]] += 1

                            renda_velha = RENDA_BASE[botoes["item"]] * (1.5 ** (botoes["nivel"] - 1))
                            renda_nova  = RENDA_BASE[botoes["item"]] * (1.5 ** botoes["nivel"])
                            renda_passiva += (renda_nova - renda_velha)

                            construcao_selecionada = None
                            if CLICK_SOUND: CLICK_SOUND.play()
                    continue

                if mouse_pos[0] < MAP_WIDTH:
                    gx, gy  = camera.tela_para_mundo(mouse_pos[0], mouse_pos[1])
                    grid    = mundo.get_grid_ativo()
                    grid_up = mundo.get_upgrades_ativo()

                    if 0 <= gx < COLS and 0 <= gy < ROWS:
                        item_clicado = grid[gy][gx]

                        if item_clicado == "elevador":
                            if mundo.camada_atual == "superficie":
                                if (gx, gy) in mundo.elevadores_cantos:
                                    elev_info = mundo.elevadores_cantos[(gx, gy)]
                                    if nivel >= elev_info["nivel_req"]:
                                        mundo.alternar_camada(elev_info["id"])
                                    else:
                                        mensagem_tela = f"Nível {elev_info['nivel_req']} necessário!"
                                        tempo_mensagem = 120
                                        if CLICK_SOUND: CLICK_SOUND.play()
                                else:
                                    mundo.alternar_camada(1)
                            else:
                                mundo.alternar_camada()
                        elif item_clicado != mundo.get_base_tile():
                            construcao_selecionada = (gx, gy, item_clicado, grid_up[gy][gx])
                            if CLICK_SOUND: CLICK_SOUND.play()
                        else:
                            lista_ativa = ITENS_CAVERNA if mundo.camada_atual != "superficie" else ITENS
                            item = lista_ativa[selected_index]
                            if dinheiro >= CUSTOS[item]:
                                if item == "elevador":
                                    mundo.superficie[gy][gx] = "elevador"
                                    if mundo.camada_atual == "superficie":
                                        mundo.cavernas[1][gy][gx] = "elevador"
                                    else:
                                        cid = int(mundo.camada_atual.split("_")[1])
                                        mundo.cavernas[cid][gy][gx] = "elevador"
                                else:
                                    grid[gy][gx]    = item
                                    grid_up[gy][gx] = 1
                                    renda_passiva  += RENDA_BASE[item]
                                    gerenciador_npcs.adicionar_npc(mundo.camada_atual, gx, gy)

                                dinheiro -= CUSTOS[item]
                                xp       += XP_ITENS[item]
                                if CLICK_SOUND: CLICK_SOUND.play()

        # Câmera (Botão Direito)
        if estado == "jogo" and not construcao_selecionada:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                arrastando = True
                drag_start = mouse_pos
                drag_offset_start = (camera.offset_x, camera.offset_y)
            if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                arrastando = False

    if arrastando and not construcao_selecionada:
        camera.offset_x = drag_offset_start[0] + (mouse_pos[0] - drag_start[0])
        camera.offset_y = drag_offset_start[1] + (mouse_pos[1] - drag_start[1])
        camera.limitar()

    # ---------------- RENDERIZAÇÃO ----------------
    if estado == "menu":
        titulo = font_menu.render("VOXEL TYCOON", True, DOURADO)
        screen.blit(titulo, (WIDTH // 2 - titulo.get_width() // 2, 150))

        desenhar_botao_menu("INICIAR JOGO", 300, mouse_pos)
        desenhar_botao_menu("SAIR PARA DESKTOP", 380, mouse_pos)

    elif estado == "jogo":
        dinheiro += renda_passiva
        
        if xp >= xp_max:
            xp -= xp_max
            nivel += 1
            xp_max = int(xp_max * 1.5)

        mundo.desenhar(screen, camera)
        gerenciador_npcs.atualizar(mundo.camada_atual, mundo.get_grid_ativo())
        gerenciador_npcs.desenhar(screen, camera, mundo.camada_atual)
        desenhar_painel()

        if tempo_mensagem > 0:
            txt = font_menu.render(mensagem_tela, True, (255, 50, 50))
            screen.blit(txt, (MAP_WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - txt.get_height() // 2))
            tempo_mensagem -= 1

        if construcao_selecionada:
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 128))
            screen.blit(s, (0, 0))
            desenhar_modal_upgrade()

    pygame.display.flip()
    clock.tick(60)