"""interface_vila.py — Interface de vilas, ataque e defesa."""
from __future__ import annotations

import pygame
from vila import Vila, Tropa
from config import WIDTH, HEIGHT, BRANCO, DOURADO, VERDE, CINZA, MAP_WIDTH


class InterfaceVila:
    """Renderiza a interface de vilas e combate."""

    def __init__(self) -> None:
        self.mostrando_vila = False
        self.mostrando_ataque = False
        self.modal_confirmacao = False
        self.btn_batalha_rect = None

    def desenhar_botao_vila(
        self,
        screen: pygame.Surface | None,
        font: pygame.font.Font | None,
        mouse_pos: tuple[int, int],
    ) -> bool:
        """Desenha botão para acessar a vila. Retorna True se clicado."""
        x, y = WIDTH - 120, 50
        w, h = 100, 40
        rect = pygame.Rect(x, y, w, h)
        hover = rect.collidepoint(mouse_pos)

        if screen:
            cor = (60, 170, 60) if hover else (40, 40, 50)
            pygame.draw.rect(screen, cor, rect, border_radius=8)
            pygame.draw.rect(screen, BRANCO, rect, 2, border_radius=8)
            if font:
                txt = font.render("VILA", True, BRANCO)
                screen.blit(txt, (x + w // 2 - txt.get_width() // 2, y + h // 2 - txt.get_height() // 2))

        return hover

    def desenhar_modal_vila(
        self,
        screen: pygame.Surface,
        font: pygame.font.Font,
        font_small: pygame.font.Font,
        vila_jogador: Vila,
        vila_rival: Vila,
    ) -> dict | None:
        """Renderiza modal da vila com opções de ataque/defesa. Retorna ação do usuário."""
        W, H = 500, 400
        cx, cy = WIDTH // 2 - W // 2, HEIGHT // 2 - H // 2

        pygame.draw.rect(screen, (20, 25, 30), (cx, cy, W, H), border_radius=15)
        pygame.draw.rect(screen, DOURADO, (cx, cy, W, H), 3, border_radius=15)

        # Título
        if font:
            screen.blit(font.render("SUAS VILA", True, BRANCO), (cx + 20, cy + 15))

        # Info da vila
        y_info = cy + 60
        nome, nivel, saude, dinheiro = vila_jogador.resumo()
        if font_small:
            screen.blit(font_small.render(f"Nível: {nivel}", True, BRANCO), (cx + 20, y_info))
            screen.blit(font_small.render(f"Saúde: {saude}/{int(vila_jogador.saude_total)}", True, VERDE), (cx + 20, y_info + 28))
            screen.blit(font_small.render(f"Dinheiro: ${dinheiro:,}", True, DOURADO), (cx + 20, y_info + 56))

        # Construções
        y_const = y_info + 100
        if font_small:
            screen.blit(font_small.render("Construções:", True, (200, 200, 200)), (cx + 20, y_const))
        for i, (tipo, qtd) in enumerate(vila_jogador.construcoes.items()):
            if font_small:
                screen.blit(font_small.render(f"  {tipo.upper()}: {qtd}", True, BRANCO), (cx + 40, y_const + 25 + i * 20))

        # Botões de ação
        btn_ataque = pygame.Rect(cx + 20, cy + H - 60, 200, 40)
        btn_fechar = pygame.Rect(cx + 280, cy + H - 60, 200, 40)

        pygame.draw.rect(screen, (220, 80, 80), btn_ataque, border_radius=5)
        pygame.draw.rect(screen, (50, 50, 100), btn_fechar, border_radius=5)

        screen.blit(font_small.render("ATACAR RIVAL", True, BRANCO), (btn_ataque.x + 20, btn_ataque.y + 8))
        screen.blit(font_small.render("FECHAR", True, BRANCO), (btn_fechar.x + 60, btn_fechar.y + 8))

        return {"atacar": btn_ataque, "fechar": btn_fechar}

    def desenhar_selecao_ataque(
        self,
        screen: pygame.Surface,
        font: pygame.font.Font,
        font_small: pygame.font.Font,
        vila_rival: Vila,
    ) -> dict | None:
        """Renderiza modal de seleção de alvo de ataque."""
        W, H = 450, 350
        cx, cy = WIDTH // 2 - W // 2, HEIGHT // 2 - H // 2

        pygame.draw.rect(screen, (30, 20, 20), (cx, cy, W, H), border_radius=15)
        pygame.draw.rect(screen, (220, 80, 80), (cx, cy, W, H), 3, border_radius=15)

        # Título
        screen.blit(font.render("ATACAR RIVAL", True, (220, 80, 80)), (cx + 20, cy + 15))

        # Info do rival
        y_info = cy + 60
        nome, nivel, saude, dinheiro = vila_rival.resumo()
        screen.blit(font_small.render(f"Vila: {nome}", True, BRANCO), (cx + 20, y_info))
        screen.blit(font_small.render(f"Nível: {nivel}", True, BRANCO), (cx + 20, y_info + 25))
        screen.blit(font_small.render(f"Saúde: {saude}/{int(vila_rival.saude_total)}", True, VERDE), (cx + 20, y_info + 50))
        screen.blit(font_small.render(f"Dinheiro Disponível: ${dinheiro:,}", True, DOURADO), (cx + 20, y_info + 75))

        # Descrição
        y_desc = y_info + 120
        screen.blit(font_small.render("Enviar 5 tropas para atacar", True, (200, 200, 200)), (cx + 20, y_desc))
        screen.blit(font_small.render("Ganhe recursos se vencer!", True, VERDE), (cx + 20, y_desc + 25))

        # Botões
        btn_atacar = pygame.Rect(cx + 20, cy + H - 60, 180, 40)
        btn_cancelar = pygame.Rect(cx + 250, cy + H - 60, 180, 40)

        pygame.draw.rect(screen, (220, 80, 80), btn_atacar, border_radius=5)
        pygame.draw.rect(screen, CINZA, btn_cancelar, border_radius=5)

        screen.blit(font_small.render("CONFIRMAR ATAQUE", True, BRANCO), (btn_atacar.x + 10, btn_atacar.y + 8))
        screen.blit(font_small.render("CANCELAR", True, BRANCO), (btn_cancelar.x + 30, btn_cancelar.y + 8))

        return {"atacar": btn_atacar, "cancelar": btn_cancelar}

    def desenhar_resultado_batalha(
        self,
        screen: pygame.Surface,
        font: pygame.font.Font,
        font_small: pygame.font.Font,
        resultado: dict,
    ) -> bool:
        """Renderiza resultado da batalha. Retorna True se clicado para fechar."""
        W, H = 400, 300
        cx, cy = WIDTH // 2 - W // 2, HEIGHT // 2 - H // 2

        cor_bg = (30, 30, 20) if resultado.get("vitoria") else (30, 20, 20)
        cor_titulo = VERDE if resultado.get("vitoria") else (220, 80, 80)

        pygame.draw.rect(screen, cor_bg, (cx, cy, W, H), border_radius=15)
        pygame.draw.rect(screen, cor_titulo, (cx, cy, W, H), 3, border_radius=15)

        titulo = "VITÓRIA!" if resultado.get("vitoria") else "DERROTA!"
        screen.blit(font.render(titulo, True, cor_titulo), (cx + 20, cy + 15))

        y = cy + 70
        for chave, valor in resultado.items():
            if chave not in ("vitoria", "atacante"):
                txt = f"{chave.replace('_', ' ').upper()}: {valor}"
                screen.blit(font_small.render(txt, True, BRANCO), (cx + 20, y))
                y += 30

        btn_fechar = pygame.Rect(cx + W // 2 - 70, cy + H - 50, 140, 40)
        pygame.draw.rect(screen, BRANCO, btn_fechar, border_radius=5)
        screen.blit(font_small.render("FECHAR", True, (0, 0, 0)), (btn_fechar.x + 30, btn_fechar.y + 8))

        return btn_fechar.collidepoint(pygame.mouse.get_pos())

    def desenhar_vila_rival_mapa(self, screen: pygame.Surface, camera, vila_rival: Vila, font_small: pygame.font.Font | None) -> None:
        """Desenha a vila rival visualmente no mapa quando na borda."""
        # Verificar se a vila rival tem construções
        if not vila_rival.construcoes:
            print(f"DEBUG: Vila rival sem construções. Construções: {vila_rival.construcoes}")
            return
        
        # Posição da vila rival no mapa (bordas) - fixa no centro da tela
        vila_x = 50  # Posição fixa na tela
        vila_y = 50  # Posição fixa na tela
        
        print(f"DEBUG: Exibindo vila rival em ({vila_x}, {vila_y}). Construções: {len(vila_rival.construcoes)}")
        
        # Fundo da vila
        pygame.draw.rect(screen, (50, 50, 60), (vila_x, vila_y, 200, 180), border_radius=10)
        pygame.draw.rect(screen, DOURADO, (vila_x, vila_y, 200, 180), 2, border_radius=10)
        
        # Título
        if font_small:
            txt = font_small.render("Vila Rival", True, BRANCO)
            screen.blit(txt, (vila_x + 10, vila_y + 10))
        
        # Construções como ícones no mapa
        y_offset = vila_y + 40
        icon_size = 24
        spacing = 35
        
        for i, (tipo, qtd) in enumerate(vila_rival.construcoes.items()):
            if i >= 4:  # Limitar a 4 construções visíveis
                break
            # Desenhar ícone da construção
            icon_x = vila_x + 15 + (i % 2) * spacing
            icon_y = y_offset + (i // 2) * spacing
            
            # Cor baseada no tipo
            if tipo == "palacio":
                cor = (255, 215, 0)  # Dourado
            elif tipo == "cachoeira":
                cor = (100, 200, 255)  # Azul
            elif tipo == "silo":
                cor = (150, 100, 50)  # Marrom
            elif tipo == "fazenda":
                cor = (50, 150, 50)  # Verde
            else:
                cor = (100, 100, 100)  # Cinza
            
            pygame.draw.rect(screen, cor, (icon_x, icon_y, icon_size, icon_size), border_radius=3)
            pygame.draw.rect(screen, BRANCO, (icon_x, icon_y, icon_size, icon_size), 1, border_radius=3)
            
            # Quantidade
            if font_small:
                qty_txt = font_small.render(f"x{qtd}", True, BRANCO)
                screen.blit(qty_txt, (icon_x + icon_size + 5, icon_y + 5))
        
        # Botão Batalhar
        btn_x, btn_y = vila_x + 50, vila_y + 145
        btn_w, btn_h = 100, 25
        btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        hover = btn_rect.collidepoint(pygame.mouse.get_pos())
        cor = (200, 50, 50) if hover else (150, 50, 50)
        pygame.draw.rect(screen, cor, btn_rect, border_radius=5)
        pygame.draw.rect(screen, BRANCO, btn_rect, 2, border_radius=5)
        if font_small:
            txt = font_small.render("Batalhar", True, BRANCO)
            screen.blit(txt, (btn_x + btn_w // 2 - txt.get_width() // 2, btn_y + btn_h // 2 - txt.get_height() // 2))
        
        self.btn_batalha_rect = btn_rect
