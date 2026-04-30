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
from ui import (
    carregar_fontes, desenhar_fundo_superficie,
    desenhar_modal_upgrade, desenhar_painel, render_menu,
)


def render_jogo(font, font_menu, font_small, estado, mundo, npcs, camera) -> None:
    estado.dinheiro += estado.renda_passiva
    mundo.desenhar(screen, camera)
    npcs.atualizar(mundo.camada_atual, mundo.get_grid_ativo())
    npcs.desenhar(screen, camera, mundo.camada_atual)
    desenhar_painel(font, font_small, estado, mundo, npcs)

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
            render_jogo(font, font_menu, font_small, estado, mundo, npcs, camera)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()