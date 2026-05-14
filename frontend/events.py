"""events.py — Processamento de eventos de input e câmera."""
from __future__ import annotations

import sys

import pygame

from config import CLICK_SOUND, COLS, CUSTOS, ITENS, ITENS_CAVERNA, MAP_WIDTH, RENDA_BASE, ROWS, WIDTH, XP_ITENS
from ui import desenhar_modal_upgrade
from interface_vila import InterfaceVila
from batalha import gerenciador_batalha


interface_vila = InterfaceVila()


def processar_eventos(font, font_menu, estado, mundo, npcs, camera, interface_ui) -> None:
    mouse = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        if event.type == pygame.KEYDOWN:
            if pygame.K_1 <= event.key <= pygame.K_6:
                estado.selected_index = event.key - pygame.K_1
            elif event.key == pygame.K_ESCAPE:
                if estado.construcao_selecionada:
                    estado.construcao_selecionada = None
                elif estado.modo_ataque:
                    estado.modo_ataque = False
                    estado.alvo_ataque_selecionado = False
                elif interface_vila.mostrando_vila:
                    interface_vila.mostrando_vila = False
                else:
                    estado.estado = "menu"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if estado.estado == "menu":
                if WIDTH//2 - 150 < mouse[0] < WIDTH//2 + 150:
                    if 300 < mouse[1] < 360:
                        estado.estado = "jogo"
                        estado.vila_rival.gerar_vila_rival()
                        if CLICK_SOUND: CLICK_SOUND.play()
                    elif 380 < mouse[1] < 440:
                        pygame.quit(); sys.exit()
            elif estado.estado == "jogo":
                # Verificar clique no botão batalhar quando na borda
                if camera.na_borda_mar() and mundo.camada_atual == "superficie" and interface_vila.btn_batalha_rect and interface_vila.btn_batalha_rect.collidepoint(mouse):
                    # Iniciar batalha
                    try:
                        invasao = gerenciador_batalha.iniciar_invasao(estado.vila_rival, "Jogador", 1)
                        estado.exibir_mensagem("Batalha iniciada contra vila rival!")
                        if CLICK_SOUND: CLICK_SOUND.play()
                    except ValueError as e:
                        estado.exibir_mensagem(str(e))
                elif interface_vila.mostrando_vila:
                    _handle_modal_vila(mouse, estado, interface_ui)
                elif estado.modo_ataque:
                    _handle_ataque(mouse, estado, interface_ui)
                elif estado.construcao_selecionada:
                    _handle_modal(font, font_menu, mouse, estado, mundo)
                elif mouse[0] < MAP_WIDTH:
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


# ── Handlers internos ────────────────────────────────────
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
        estado.renda_passiva += (RENDA_BASE[botoes["item"]] *
                                  (1.5**n - 1.5**(n-1)))
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
    elif tile != mundo.get_base_tile():
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
        grid[gy][gx] = item;  grid_up[gy][gx] = 1
        mundo.get_owner_ativo()[gy][gx] = "player"
        estado.renda_passiva += RENDA_BASE[item]
        npcs.adicionar_npc(mundo.camada_atual, gx, gy)
    estado.dinheiro -= CUSTOS[item]
    estado.ganhar_xp(XP_ITENS[item])
    if CLICK_SOUND: CLICK_SOUND.play()