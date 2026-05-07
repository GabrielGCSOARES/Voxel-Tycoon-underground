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
from interface_vila import InterfaceVila
from batalha import gerenciador_batalha
from ui import (
    carregar_fontes, desenhar_fundo_superficie,
    desenhar_modal_upgrade, desenhar_painel, render_menu,
)


def render_jogo(font, font_menu, font_small, estado, mundo, npcs, camera, interface_vila) -> None:
    estado.dinheiro += estado.renda_passiva
    estado.vila_jogador.dinheiro += estado.renda_passiva * 2
    
    mundo.desenhar(screen, camera)
    npcs.atualizar(mundo)
    npcs.desenhar(screen, camera, mundo.camada_atual)
    desenhar_painel(font, font_small, estado, mundo, npcs)
    
    # Atualizar vilas
    estado.vila_jogador.atualizar()
    estado.vila_rival.atualizar()
    
    # Processar invasão em andamento
    if estado.vila_rival.invasao_ativa:
        resultado = gerenciador_batalha.processar_invasao(estado.vila_rival)
        if resultado:
            gerenciador_batalha.finalizador_invasao(estado.vila_rival, estado.vila_jogador)
            estado.exibir_mensagem(f"Batalha terminada! {'Vitória!' if resultado['vitoria'] else 'Derrota!'}")
    
    # Desenhar botão de vila
    if interface_vila.desenhar_botao_vila(screen, font_small, pygame.mouse.get_pos()):
        pass  # Será clicado via eventos
    
    # Renderizar modais
    if interface_vila.mostrando_vila:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        interface_vila.modal_vila_botoes = interface_vila.desenhar_modal_vila(
            screen, font_small, font, estado.vila_jogador, estado.vila_rival
        )
    
    if interface_vila.mostrando_ataque:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        interface_vila.modal_ataque_botoes = interface_vila.desenhar_selecao_ataque(
            screen, font_small, font, estado.vila_rival
        )

    if estado.tempo_mensagem > 0:
        txt = font_menu.render(estado.mensagem_tela, True, (255, 50, 50))
        screen.blit(txt, (MAP_WIDTH//2 - txt.get_width()//2,
                          HEIGHT//2   - txt.get_height()//2))
        estado.tempo_mensagem -= 1

    if estado.construcao_selecionada:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        desenhar_modal_upgrade(font, font_menu, estado)


def main() -> None:
    clock  = pygame.time.Clock()
    camera = Camera()
    mundo  = GerenciadorMundo()
    npcs   = GerenciadorNPCs()
    estado = EstadoJogo()
    interface_vila = InterfaceVila()
    font, font_menu, font_small = carregar_fontes()

    while True:
        tempo     = pygame.time.get_ticks() / 1000.0
        mouse_pos = pygame.mouse.get_pos()

        if estado.estado == "jogo" and mundo.camada_atual == "superficie":
            desenhar_fundo_superficie(tempo, camera)
        else:
            screen.fill((15, 15, 20))

        processar_eventos(font, font_menu, estado, mundo, npcs, camera, interface_vila)

        if estado.estado == "menu":
            render_menu(font, font_menu, mouse_pos)
        elif estado.estado == "jogo":
            render_jogo(font, font_menu, font_small, estado, mundo, npcs, camera, interface_vila)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()