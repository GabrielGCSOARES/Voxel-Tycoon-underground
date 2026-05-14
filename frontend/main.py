"""main.py — Loop principal do V.T. Underground."""
from __future__ import annotations
import sys
import pygame
from camera import Camera
from config import HEIGHT, MAP_WIDTH, WIDTH, screen
from estado import EstadoJogo
from events import processar_eventos
from mundo import GerenciadorMundo
from npcs import GerenciadorNPCs
from batalha import gerenciador_batalha
from hud_batalha import HUDBatalha
from ui import (
    carregar_fontes, desenhar_fundo_superficie,
    desenhar_modal_upgrade, desenhar_painel, render_menu,
)


def render_jogo(
    font, font_menu, font_small,
    estado, mundo, npcs, camera,
    hud_batalha: HUDBatalha,
) -> None:
    # Renda passiva
    estado.dinheiro += estado.renda_passiva
    estado.vila_jogador.atualizar()   # recursos + reconstruções

    # Tick de quests
    estado.quests.tick(estado)
    # Consome notificações de quests concluídas
    while True:
        notif = estado.quests.pop_notificacao()
        if not notif:
            break
        hud_batalha.adicionar_toast(notif[0], notif[1])

    # Batalha
    gerenciador_batalha.atualizar(estado, mundo)
    # Se a batalha gerou um resultado, processa
    if gerenciador_batalha.resultado_pendente:
        r = gerenciador_batalha.resultado_pendente
        gerenciador_batalha.resultado_pendente = None

    # Renderização do mapa
    mundo.desenhar(screen, camera)
    npcs.atualizar(mundo)
    npcs.desenhar(screen, camera, mundo.camada_atual)

    # NPCs de batalha
    gerenciador_batalha.desenhar(screen, camera, mundo.camada_atual)

    # Painel lateral
    y_hud = desenhar_painel(font, font_small, estado, mundo, npcs)

    # HUD lateral em ordem fixa para evitar sobreposição.
    y_hud = hud_batalha.desenhar(screen, font, font_small, estado, gerenciador_batalha, y_hud)
    y_hud = npcs.desenhar_status_oponente(screen, font_small, MAP_WIDTH, y_hud)
    npcs.desenhar_hud_mercado(screen, font_small, MAP_WIDTH, y_hud, HEIGHT - 8)

    # Mensagem central
    if estado.tempo_mensagem > 0 and font_menu:
        txt = font_menu.render(estado.mensagem_tela, True, (255, 50, 50))
        screen.blit(txt, (
            MAP_WIDTH // 2 - txt.get_width() // 2,
            HEIGHT    // 2 - txt.get_height() // 2,
        ))
        estado.tempo_mensagem -= 1

    # Modal de upgrade
    if estado.construcao_selecionada:
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 128))
        screen.blit(ov, (0, 0))
        desenhar_modal_upgrade(font, font_menu, estado)


def main() -> None:
    clock      = pygame.time.Clock()
    camera     = Camera()
    mundo      = GerenciadorMundo()
    npcs       = GerenciadorNPCs()
    estado     = EstadoJogo()
    hud_batalha = HUDBatalha()
    font, font_menu, font_small = carregar_fontes()

    while True:
        tempo     = pygame.time.get_ticks() / 1000.0
        mouse_pos = pygame.mouse.get_pos()

        if estado.estado == "jogo" and mundo.camada_atual == "superficie":
            desenhar_fundo_superficie(tempo, camera)
        else:
            screen.fill((15, 15, 20))

        processar_eventos(font, font_menu, estado, mundo, npcs, camera)

        if estado.estado == "menu":
            render_menu(font, font_menu, mouse_pos)
        elif estado.estado == "jogo":
            render_jogo(font, font_menu, font_small, estado, mundo, npcs, camera, hud_batalha)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
