"""events.py — Processamento de eventos de input e câmera."""
from __future__ import annotations
import sys
import pygame
from config import (
    CLICK_SOUND, COLS, CUSTOS, DEFENSORES_COMPRA, ITENS, ITENS_CAVERNA,
    MAP_WIDTH, ROWS, WIDTH, XP_ITENS, calcular_renda_construcao,
)
from ui import desenhar_modal_upgrade


def processar_eventos(font, font_menu, estado, mundo, npcs, camera) -> None:
    mouse = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        if event.type == pygame.KEYDOWN:
            if pygame.K_1 <= event.key <= pygame.K_6:
                lista = ITENS_CAVERNA if mundo.camada_atual != "superficie" else ITENS
                indice = event.key - pygame.K_1
                if indice < len(lista):
                    estado.selected_index = indice
            elif event.key == pygame.K_ESCAPE:
                if estado.construcao_selecionada:
                    estado.construcao_selecionada = None
                else:
                    estado.estado = "menu"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if estado.estado == "menu":
                if WIDTH//2 - 150 < mouse[0] < WIDTH//2 + 150:
                    if 300 < mouse[1] < 360:
                        estado.estado = "jogo"
                        estado.vila_rival.gerar_rival()
                        if CLICK_SOUND: CLICK_SOUND.play()
                    elif 380 < mouse[1] < 440:
                        pygame.quit(); sys.exit()
            elif estado.estado == "jogo":
                if estado.construcao_selecionada:
                    _handle_modal(font, font_menu, mouse, estado, mundo)
                elif mouse[0] >= MAP_WIDTH:
                    _handle_painel(mouse, estado, mundo)
                else:
                    _handle_mapa(mouse, estado, mundo, npcs, camera)

        if estado.estado == "jogo" and not estado.construcao_selecionada:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                estado.arrastando        = True
                estado.drag_start        = mouse
                estado.drag_offset_start = (camera.offset_x, camera.offset_y)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                estado.arrastando = False

    if estado.arrastando and not estado.construcao_selecionada:
        m = pygame.mouse.get_pos()
        camera.offset_x = estado.drag_offset_start[0] + (m[0] - estado.drag_start[0])
        camera.offset_y = estado.drag_offset_start[1] + (m[1] - estado.drag_start[1])
        camera.limitar()


def _handle_modal(font, font_menu, pos, estado, mundo) -> None:
    botoes = desenhar_modal_upgrade(font, font_menu, estado)
    if not botoes:
        return
    if botoes["fechar"].collidepoint(pos):
        estado.construcao_selecionada = None
        if CLICK_SOUND: CLICK_SOUND.play()
        return
    if botoes["upgrade"].collidepoint(pos) and estado.dinheiro >= botoes["custo"]:
        estado.dinheiro -= botoes["custo"]
        grid_up = mundo.get_upgrades_ativo()
        grid_up[botoes["gy"]][botoes["gx"]] += 1
        n = botoes["nivel"]
        estado.renda_passiva += (
            calcular_renda_construcao(botoes["item"], n + 1)
            - calcular_renda_construcao(botoes["item"], n)
        )
        c = estado.vila_jogador.get_construcao(botoes["gx"], botoes["gy"], mundo.camada_atual)
        if c:
            c.nivel = n + 1
            pct_hp = c.pct_hp
            c.hp_max *= 1.35
            c.hp = max(c.hp, c.hp_max * pct_hp)
        estado.construcao_selecionada = None
        if CLICK_SOUND: CLICK_SOUND.play()


def _handle_mapa(pos, estado, mundo, npcs, camera) -> None:
    gx, gy = camera.tela_para_mundo(pos[0], pos[1])
    if not (0 <= gx < COLS and 0 <= gy < ROWS):
        return
    grid    = mundo.get_grid_ativo()
    grid_up = mundo.get_upgrades_ativo()
    tile    = grid[gy][gx]

    if tile == "elevador":
        _handle_elevador(gx, gy, estado, mundo)
    elif tile == "base_inimiga":
        estado.exibir_mensagem("Base inimiga gerando invasores!")
    elif tile != mundo.get_base_tile():
        # Clicou numa construção destruída? Tenta reconstruir
        c = estado.vila_jogador.get_construcao(gx, gy, mundo.camada_atual)
        if c and c.destruida and not c.reconstruindo:
            if estado.vila_jogador.gastar_reconstrucao(c):
                estado.quests.on_reconstrucao()
                estado.exibir_mensagem(f"Reconstruindo {c.tipo}...")
                if CLICK_SOUND: CLICK_SOUND.play()
            else:
                custo = c.custo_reconstrucao()
                estado.exibir_mensagem(
                    f"Sem recursos! Precisa: {custo['madeira']} madeira, {custo['pedra']} pedra"
                )
        else:
            estado.construcao_selecionada = (gx, gy, tile, grid_up[gy][gx])
            if CLICK_SOUND: CLICK_SOUND.play()
    else:
        _handle_construir(gx, gy, grid, grid_up, estado, mundo, npcs)


def _handle_elevador(gx, gy, estado, mundo) -> None:
    if mundo.camada_atual == "superficie":
        info = mundo.elevadores_cantos.get((gx, gy))
        if info:
            if estado.nivel >= info["nivel_req"]:
                mundo.alternar_camada(info["id"])
            else:
                estado.exibir_mensagem(f"Nivel {info['nivel_req']} necessario!")
                if CLICK_SOUND: CLICK_SOUND.play()
        else:
            mundo.alternar_camada(1)
    else:
        mundo.alternar_camada()


def _handle_construir(gx, gy, grid, grid_up, estado, mundo, npcs) -> None:
    lista = ITENS_CAVERNA if mundo.camada_atual != "superficie" else ITENS
    if estado.selected_index >= len(lista):
        estado.selected_index = len(lista) - 1
    item  = lista[estado.selected_index]
    if estado.dinheiro < CUSTOS[item]:
        return
    if item == "elevador":
        mundo.superficie[gy][gx] = "elevador"
        if mundo.camada_atual == "superficie":
            mundo.cavernas[1][gy][gx] = "elevador"
        else:
            mundo.cavernas[int(mundo.camada_atual.split("_")[1])][gy][gx] = "elevador"
    else:
        grid[gy][gx] = item
        grid_up[gy][gx] = 1
        estado.renda_passiva += calcular_renda_construcao(item, 1)
        npcs.adicionar_npc(mundo.camada_atual, gx, gy)
        # Registra na vila (para HP e recursos)
        estado.vila_jogador.registrar_construcao(item, gx, gy, mundo.camada_atual)
        # Notifica quests
        estado.quests.on_construir(item, mundo.camada_atual)

    estado.dinheiro -= CUSTOS[item]
    estado.ganhar_xp(XP_ITENS[item])
    if CLICK_SOUND: CLICK_SOUND.play()


def _handle_painel(pos, estado, mundo) -> None:
    if mundo.camada_atual != "superficie":
        return

    from ui import rects_botoes_defesa

    for tipo, rect in rects_botoes_defesa(mundo).items():
        if not rect.collidepoint(pos):
            continue

        info = DEFENSORES_COMPRA[tipo]
        if estado.nivel < info["nivel_req"]:
            estado.exibir_mensagem(f"Nivel {info['nivel_req']} necessario para {tipo}!")
            return
        if estado.dinheiro < info["custo"]:
            estado.exibir_mensagem(f"Dinheiro insuficiente para {tipo}!")
            return

        construcoes = estado.vila_jogador.construcoes_intactas("superficie")
        if construcoes:
            base = construcoes[-1]
            gx, gy = base.gx, base.gy
        else:
            gx, gy = COLS // 2, ROWS // 2
        estado.dinheiro -= info["custo"]
        estado.vila_jogador.comprar_defensor(tipo, gx, gy)
        estado.exibir_mensagem(f"{tipo.capitalize()} contratado!")
        if CLICK_SOUND: CLICK_SOUND.play()
        return
