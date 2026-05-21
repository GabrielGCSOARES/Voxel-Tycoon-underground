"""ui.py — Fontes, botões, painel lateral, modal de upgrade e fundo animado."""
from __future__ import annotations

import math

import pygame

from config import (
    BRANCO, CINZA, CUSTOS, DEFENSORES_COMPRA, DOURADO, HEIGHT,
    ITENS, ITENS_CAVERNA, MAP_WIDTH, PANEL_WIDTH,
    VERDE, WIDTH, calcular_renda_construcao, screen,
)

# ── Constantes de layout ─────────────────────────────────
BTN_W, BTN_H   = 300, 60
Y_CONSTRUIR    = 180
ITEM_H         = 20
PANEL_X        = MAP_WIDTH + 20
OVERLAY_ALPHA  = 128
ONDA_ESPC_X    = 60
ONDA_ESPC_Y    = 40


# ── Fontes ───────────────────────────────────────────────
def carregar_fontes() -> tuple[pygame.font.Font | None, pygame.font.Font | None, pygame.font.Font | None]:
    try:
        return (
            pygame.font.SysFont("arial", 22),
            pygame.font.SysFont("arial", 45, bold=True),
            pygame.font.SysFont("arial", 13, bold=True),
        )
    except NotImplementedError:
        return (None, None, None)  # Fonts não disponíveis


# ── Fundo ────────────────────────────────────────────────
def desenhar_fundo_superficie(tempo: float, camera) -> None:
    screen.fill((20, 100, 150))
    sy0 = int(camera.offset_y) % ONDA_ESPC_Y
    sx0 = int(camera.offset_x) % ONDA_ESPC_X
    for y in range(sy0 - ONDA_ESPC_Y, HEIGHT + ONDA_ESPC_Y, ONDA_ESPC_Y):
        wy = y - camera.offset_y
        for x in range(sx0 - ONDA_ESPC_X, MAP_WIDTH + ONDA_ESPC_X, ONDA_ESPC_X):
            wx = x - camera.offset_x
            ox = math.sin(tempo * 1.5 + wy * 0.05) * 15
            oy = math.cos(tempo * 2.0 + wx * 0.05) * 8
            px, py = x + ox, y + oy
            pygame.draw.line(screen, (40, 140, 190), (px, py),        (px+20, py),      3)
            pygame.draw.line(screen, (60, 160, 210), (px+5, py+3),    (px+15, py+3),    2)


# ── Menu ─────────────────────────────────────────────────
def desenhar_botao_menu(font, texto: str, y_pos: int, mouse_pos: tuple) -> bool:
    x     = WIDTH // 2 - BTN_W // 2
    hover = x < mouse_pos[0] < x + BTN_W and y_pos < mouse_pos[1] < y_pos + BTN_H
    cor   = (60, 170, 60) if hover else (40, 40, 50)
    pygame.draw.rect(screen, cor,    (x, y_pos, BTN_W, BTN_H), border_radius=10)
    pygame.draw.rect(screen, BRANCO, (x, y_pos, BTN_W, BTN_H), 2, border_radius=10)
    if font:
        txt = font.render(texto, True, BRANCO)
        screen.blit(txt, (WIDTH//2 - txt.get_width()//2,
                          y_pos + BTN_H//2 - txt.get_height()//2))
    return hover


def render_menu(font, font_menu, mouse_pos: tuple) -> None:
    if font_menu:
        titulo = font_menu.render("VOXEL TYCOON", True, DOURADO)
        screen.blit(titulo, (WIDTH//2 - titulo.get_width()//2, 150))
    desenhar_botao_menu(font, "INICIAR JOGO",      300, mouse_pos)
    desenhar_botao_menu(font, "SAIR PARA DESKTOP", 380, mouse_pos)


# ── Painel lateral ───────────────────────────────────────
def desenhar_painel(font, font_small, estado, mundo, npcs) -> int:
    pygame.draw.rect(screen, (30, 34, 40), (MAP_WIDTH, 0, PANEL_WIDTH, HEIGHT))
    cor_camada = VERDE if mundo.camada_atual == "superficie" else DOURADO
    if font:
        screen.blit(font.render(f"MAPA: {mundo.camada_atual.upper()}", True, cor_camada),
                    (PANEL_X, 20))
    ganho = estado.renda_passiva * 60
    for i, txt in enumerate((
        f"Dinheiro: ${int(estado.dinheiro):,}",
        f"Ganho: ${ganho:.1f}/s",
        f"Nivel: {estado.nivel}",
        f"XP: {estado.xp}/{estado.xp_max}",
        f"Populacao: {estado.populacao}",
    )):
        if font_small:
            screen.blit(font_small.render(txt, True, BRANCO), (PANEL_X, 55 + i * 20))

    lista = ITENS_CAVERNA if mundo.camada_atual != "superficie" else ITENS
    if font_small:
        screen.blit(font_small.render(f"CONSTRUIR (1-{len(lista)}):", True, (150, 150, 150)), (PANEL_X, Y_CONSTRUIR))
    for i, item in enumerate(lista):
        custo = CUSTOS[item]
        cor   = (DOURADO if i == estado.selected_index
                 else (180, 60, 60) if estado.dinheiro < custo else BRANCO)
        if font_small:
            screen.blit(font_small.render(f"{i+1}-{item.upper()}  ${custo:,}", True, cor),
                        (PANEL_X, Y_CONSTRUIR + 26 + i * ITEM_H))

    y = Y_CONSTRUIR + 26 + len(lista) * ITEM_H + 12
    if mundo.camada_atual == "superficie":
        y = desenhar_botoes_defesa(font_small, estado, mundo, y)

    return y


def rects_botoes_defesa(mundo) -> dict[str, pygame.Rect]:
    if mundo.camada_atual != "superficie":
        return {}
    y_base = Y_CONSTRUIR + 26 + len(ITENS) * ITEM_H + 34
    return {
        tipo: pygame.Rect(PANEL_X, y_base + i * 28, 155, 22)
        for i, tipo in enumerate(DEFENSORES_COMPRA)
    }


def desenhar_botoes_defesa(font_small, estado, mundo, y: int) -> int:
    if not font_small:
        return y
    screen.blit(font_small.render("DEFESA", True, (150, 150, 150)), (PANEL_X, y))
    y += 24
    for tipo, rect in rects_botoes_defesa(mundo).items():
        info = DEFENSORES_COMPRA[tipo]
        bloqueado = estado.nivel < info["nivel_req"]
        sem_dinheiro = estado.dinheiro < info["custo"]
        cor = CINZA if bloqueado or sem_dinheiro else (55, 120, 75)
        pygame.draw.rect(screen, cor, rect, border_radius=4)
        pygame.draw.rect(screen, (120, 150, 120), rect, 1, border_radius=4)
        texto = f"{tipo.upper()} ${info['custo']:,}"
        if bloqueado:
            texto = f"{tipo.upper()} NV.{info['nivel_req']}"
        screen.blit(font_small.render(texto, True, BRANCO), (rect.x + 6, rect.y + 4))
        y = rect.bottom + 6
    return y + 8


# ── Modal de upgrade ─────────────────────────────────────
def desenhar_modal_upgrade(font, font_menu, estado) -> dict | None:
    if not estado.construcao_selecionada:
        return None
    gx, gy, item, nivel_atual = estado.construcao_selecionada
    W, H = 350, 250
    cx   = WIDTH  // 2 - W // 2
    cy   = HEIGHT // 2 - H // 2

    pygame.draw.rect(screen, (20, 25, 30), (cx, cy, W, H), border_radius=15)
    pygame.draw.rect(screen, DOURADO,      (cx, cy, W, H), 3, border_radius=15)

    renda_at  = calcular_renda_construcao(item, nivel_atual) * 60
    renda_nx  = calcular_renda_construcao(item, nivel_atual + 1) * 60
    custo_up  = int(CUSTOS[item] * (2.2 ** nivel_atual))

    if font_menu:
        screen.blit(font_menu.render(item.upper(), True, BRANCO),                         (cx+20, cy+20))
    if font:
        screen.blit(font.render(f"Nivel Atual: {nivel_atual}", True, (200,200,200)),       (cx+20, cy+70))
        screen.blit(font.render(f"Renda: ${renda_at:.1f}/s -> ${renda_nx:.1f}/s", True, VERDE), (cx+20, cy+100))
        screen.blit(font.render(f"Custo Upgrade: ${custo_up:,}", True, DOURADO),           (cx+20, cy+130))

    btn_up  = pygame.Rect(cx+20,  cy+180, 140, 40)
    btn_fx  = pygame.Rect(cx+190, cy+180, 140, 40)
    pygame.draw.rect(screen, VERDE if estado.dinheiro >= custo_up else CINZA, btn_up,  border_radius=5)
    pygame.draw.rect(screen, (200, 50, 50),  btn_fx,  border_radius=5)
    screen.blit(font.render("Evoluir", True, BRANCO), (btn_up.x+35, btn_up.y+10))
    screen.blit(font.render("Fechar",  True, BRANCO), (btn_fx.x+40, btn_fx.y+10))

    return {"upgrade": btn_up, "fechar": btn_fx, "custo": custo_up,
            "gx": gx, "gy": gy, "item": item, "nivel": nivel_atual}
