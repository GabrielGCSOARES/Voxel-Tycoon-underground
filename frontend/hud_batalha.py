"""
hud_batalha.py — HUD de batalha, quests e recursos no painel lateral.

Renderiza:
  - Barra de madeira e pedra
  - Painel de quests ativas (4 por vez)
  - Notificações de quest concluida (toast flutuante)
  - Status de invasão (reutiliza GerenciadorBatalha.desenhar_hud)
"""
from __future__ import annotations
import pygame
from config import MAP_WIDTH, HEIGHT, WIDTH, BRANCO, DOURADO, VERDE


# ── Toast de quest concluida ─────────────────────────────
class ToastQuest:
    """Notificação flutuante que sobe e desaparece."""
    __slots__ = ("titulo","recompensa","timer","y","alpha")

    DURACAO = 240   # frames

    def __init__(self, titulo: str, recompensa: str) -> None:
        self.titulo     = titulo
        self.recompensa = recompensa
        self.timer      = self.DURACAO
        self.y          = float(HEIGHT - 80)
        self.alpha      = 255

    def atualizar(self) -> bool:
        """Retorna False quando expirou."""
        self.timer -= 1
        self.y     -= 0.4
        if self.timer < 60:
            self.alpha = int(255 * self.timer / 60)
        return self.timer > 0

    def desenhar(self, screen: pygame.Surface, font_small) -> None:
        if not font_small:
            return
        W, H = 280, 46
        x = WIDTH // 2 - W // 2
        y = int(self.y)
        surf = pygame.Surface((W, H), pygame.SRCALPHA)
        surf.fill((20, 30, 20, min(200, self.alpha)))
        pygame.draw.rect(surf, (60, 200, 80), (0, 0, W, H), 2, border_radius=8)
        tit  = font_small.render(f"Quest: {self.titulo}", True, (60,220,80))
        rec  = font_small.render(f"+ {self.recompensa}", True, DOURADO)
        surf.blit(tit, (10, 6))
        surf.blit(rec, (10, 24))
        screen.blit(surf, (x, y))


class HUDBatalha:
    """Renderiza todos os elementos de batalha, recursos e quests no HUD."""

    def __init__(self) -> None:
        self._toasts: list[ToastQuest] = []

    def adicionar_toast(self, titulo: str, recompensa: str) -> None:
        self._toasts.append(ToastQuest(titulo, recompensa))

    def atualizar(self) -> None:
        self._toasts = [t for t in self._toasts if t.atualizar()]

    def desenhar(
        self,
        screen: pygame.Surface,
        font,
        font_small,
        estado,
        gerenciador_batalha,
        y_inicio: int,
    ) -> int:
        self.atualizar()

        PAD     = MAP_WIDTH + 10
        LARGURA = 155
        y       = y_inicio

        # ── Quests ativas ────────────────────────────────
        pygame.draw.line(screen, (70,70,50), (PAD, y), (PAD+LARGURA, y), 1)
        y += 4
        if font_small:
            screen.blit(font_small.render("QUESTS", True, (180,160,80)), (PAD, y))
        y += 14

        for q in estado.quests.quests_ativas():
            if not font_small:
                break
            titulo_txt = self._cortar_texto(font_small, q.titulo, LARGURA)
            desc_txt = self._cortar_texto(font_small, q.descricao, LARGURA - 44)
            screen.blit(font_small.render(titulo_txt, True, (200,200,200)), (PAD, y))
            y += 13
            prog_txt = f"{min(q.progresso, q.meta)}/{q.meta}"
            ps = font_small.render(prog_txt, True, (140,140,180))
            screen.blit(font_small.render(desc_txt, True, (145,145,145)), (PAD, y))
            screen.blit(ps, (PAD + LARGURA - ps.get_width(), y))
            y += 12

            bw = LARGURA - 4
            prog = q.pct
            pygame.draw.rect(screen, (40,40,40),   (PAD, y, bw, 5))
            pygame.draw.rect(screen, (80,180,255), (PAD, y, int(prog*bw), 5))
            y += 10

        y += 4

        # ── Recursos ─────────────────────────────────────
        vila = estado.vila_jogador
        pygame.draw.line(screen, (70,70,50), (PAD, y), (PAD+LARGURA, y), 1)
        y += 4
        if font_small:
            screen.blit(font_small.render("RECURSOS", True, (180,160,80)), (PAD, y))
        y += 14

        self._barra_recurso(screen, font_small, PAD, y,
                            "Madeira", int(vila.madeira), 9999, (120,180,60))
        y += 16
        self._barra_recurso(screen, font_small, PAD, y,
                            "Pedra", int(vila.pedra), 9999, (160,160,180))
        y += 22

        # ── Status de batalha ─────────────────────────────
        y = gerenciador_batalha.desenhar_hud(screen, font_small, y, MAP_WIDTH)

        # ── Toasts ───────────────────────────────────────
        for toast in self._toasts:
            toast.desenhar(screen, font_small)
        return y

    # ── Helpers ──────────────────────────────────────────
    @staticmethod
    def _barra_recurso(
        screen, font_small, x, y,
        nome: str, valor: int, maximo: int, cor: tuple
    ) -> None:
        if not font_small:
            return
        LARGURA = 100
        lbl = font_small.render(f"{nome}: {valor}", True, BRANCO)
        screen.blit(lbl, (x, y))
        bx = x + 95
        pygame.draw.rect(screen, (40,40,40), (bx, y+2, LARGURA-95+60, 6))
        pct = min(1.0, valor / max(maximo, 1))
        pygame.draw.rect(screen, cor, (bx, y+2, int(pct*(LARGURA-95+60)), 6))

    @staticmethod
    def _cortar_texto(font_small, texto: str, largura: int) -> str:
        if font_small.size(texto)[0] <= largura:
            return texto
        while texto and font_small.size(texto + "...")[0] > largura:
            texto = texto[:-1]
        return texto + "..." if texto else ""
