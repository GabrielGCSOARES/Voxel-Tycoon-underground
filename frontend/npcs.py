"""npcs.py — NPC, CarrinhoMineracao e GerenciadorNPCs."""
from __future__ import annotations

import math
import random
from typing import Final

import pygame

from config import COLS, GRID_SIZE, HEIGHT, MAP_WIDTH, ROWS
from mercado import (
    CAMADAS, EMPRESAS, MAX_CARRINHOS, Empresa,
    formatar_preco, mercado,
)

_TILES_BASE: Final[frozenset[str]] = frozenset({"grama", "pedra", "elevador"})
_FERRAMENTA: Final[dict[str, str]] = {
    "mineracao": "picareta", "cristal":    "picareta",
    "forja":     "martelo",  "laboratorio":"prancheta",
    "reator":    "digital",  "cripto":     "digital",
}


# ─────────────────────────────────────────────────────────
#  CARRINHO DE MINERAÇÃO
# ─────────────────────────────────────────────────────────
class CarrinhoMineracao:
    __slots__ = (
        "empresa", "cor", "x", "y", "velocidade",
        "dest_x", "dest_y", "carga", "max_carga",
        "frame", "andando", "_timer",
    )

    def __init__(self, empresa: Empresa, gx: int, gy: int) -> None:
        self.empresa    = empresa.nome
        self.cor        = empresa.cor_carrinho
        self.x          = float(gx * GRID_SIZE + GRID_SIZE // 2)
        self.y          = float(gy * GRID_SIZE + GRID_SIZE // 2)
        self.velocidade = random.uniform(1.2, 2.2)
        self.dest_x     = self.x
        self.dest_y     = self.y
        self.carga      = 0
        self.max_carga  = 10
        self.frame      = 0.0
        self.andando    = False
        self._timer     = 0

    def _novo_destino(self, grid: list) -> None:
        alvos = [(gx, gy) for gy in range(ROWS) for gx in range(COLS)
                 if grid[gy][gx] not in ("pedra", "elevador")]
        if alvos:
            gx, gy      = random.choice(alvos)
            self.dest_x = gx * GRID_SIZE + GRID_SIZE // 2 + random.randint(-8, 8)
            self.dest_y = gy * GRID_SIZE + GRID_SIZE // 2 + random.randint(-8, 8)
        else:
            self.dest_x = random.randint(1, COLS - 2) * GRID_SIZE + GRID_SIZE // 2
            self.dest_y = random.randint(1, ROWS - 2) * GRID_SIZE + GRID_SIZE // 2
        self._timer = random.randint(90, 240)

    def atualizar(self, grid: list) -> None:
        self._timer -= 1
        if self._timer <= 0:
            self.carga = (0 if self.carga >= self.max_carga
                          else min(self.max_carga, self.carga + random.randint(0, 2)))
            self._novo_destino(grid)
        dx, dy = self.dest_x - self.x, self.dest_y - self.y
        dist   = math.hypot(dx, dy)
        if dist > self.velocidade:
            inv = self.velocidade / dist
            self.x += dx * inv;  self.y += dy * inv
            self.andando = True;  self.frame += 0.3
        else:
            self.x, self.y = self.dest_x, self.dest_y
            self.andando = False; self.frame += 0.1

    def desenhar(self, screen: pygame.Surface, camera) -> None:
        sx, sy = camera.aplicar(int(self.x), int(self.y))
        if not (-30 < sx < MAP_WIDTH + 30 and -30 < sy < HEIGHT + 30):
            return
        if self.andando:
            sy += int(math.sin(self.frame * 4) * 1.5)
        r, g, b = self.cor
        pygame.draw.ellipse(screen, (0, 0, 0), (sx - 12, sy + 8, 28, 7))
        pygame.draw.line(screen, (60, 55, 50), (sx - 14, sy + 12), (sx + 14, sy + 12), 2)
        ang = self.frame * (2.0 if self.andando else 0.3)
        for rx in (sx - 8, sx + 8):
            pygame.draw.circle(screen, (30, 30, 30), (rx, sy + 8), 5)
            pygame.draw.circle(screen, (80, 80, 80), (rx, sy + 8), 3)
            pygame.draw.line(screen, (120, 120, 120), (rx, sy + 8),
                             (rx + int(math.cos(ang) * 2), sy + 8 + int(math.sin(ang) * 2)), 1)
        pygame.draw.rect(screen, (r, g, b), (sx - 10, sy - 4, 20, 12), border_radius=2)
        pygame.draw.rect(screen, (min(255, r+40), min(255, g+40), min(255, b+40)),
                         (sx - 10, sy - 4, 20, 4), border_radius=2)
        if self.carga:
            pygame.draw.rect(screen, (50, 220, 100),
                             (sx - 8, sy - 2, int(self.carga / self.max_carga * 16), 3))


# ─────────────────────────────────────────────────────────
#  NPC
# ─────────────────────────────────────────────────────────
class NPC:
    __slots__ = (
        "empresa", "cor", "x", "y", "velocidade", "tamanho",
        "dest_x", "dest_y", "_timer", "andando", "frame",
        "alvo_item", "estoque", "max_estoque",
    )

    def __init__(self, x: int, y: int, empresa: Empresa, velocidade: float = 1.5) -> None:
        self.empresa     = empresa.nome
        self.cor         = empresa.cor
        self.x           = float(x * GRID_SIZE + GRID_SIZE // 4)
        self.y           = float(y * GRID_SIZE + GRID_SIZE // 4)
        self.velocidade  = velocidade
        self.tamanho     = 10
        self.dest_x      = self.x;  self.dest_y = self.y
        self._timer      = 0;       self.andando = False
        self.frame       = 0.0;     self.alvo_item: str | None = None
        self.estoque     = 0;       self.max_estoque = 5

    def _novo_destino(self, grid: list) -> None:
        alvos = [(gx, gy) for gy in range(ROWS) for gx in range(COLS)
                 if grid[gy][gx] not in _TILES_BASE]
        if alvos:
            gx, gy         = random.choice(alvos)
            off            = GRID_SIZE // 4
            self.dest_x    = gx * GRID_SIZE + random.randint(off, GRID_SIZE - off)
            self.dest_y    = gy * GRID_SIZE + random.randint(off, GRID_SIZE - off)
            self.alvo_item = grid[gy][gx]
        else:
            gx0 = int(self.x // GRID_SIZE);  gy0 = int(self.y // GRID_SIZE)
            self.dest_x    = random.randint(max(0, gx0-5), min(COLS-1, gx0+5)) * GRID_SIZE + GRID_SIZE//2
            self.dest_y    = random.randint(max(0, gy0-5), min(ROWS-1, gy0+5)) * GRID_SIZE + GRID_SIZE//2
            self.alvo_item = None
        self._timer = random.randint(60, 180)

    def atualizar(self, grid: list) -> None:
        self._timer -= 1
        if self._timer <= 0:
            self.estoque = (0 if (self.alvo_item and self.estoque > 0)
                            else min(self.max_estoque, self.estoque + random.randint(1, 3)))
            self._novo_destino(grid)
        dx, dy = self.dest_x - self.x, self.dest_y - self.y
        dist   = math.hypot(dx, dy)
        if dist > self.velocidade:
            inv = self.velocidade / dist
            self.x += dx * inv;  self.y += dy * inv
            self.andando = True;  self.frame += 0.2
        else:
            self.x, self.y = self.dest_x, self.dest_y
            self.andando = False; self.frame += 0.1

    def desenhar(self, screen: pygame.Surface, camera) -> None:
        sx, sy = camera.aplicar(int(self.x), int(self.y))
        if not (-20 < sx < MAP_WIDTH + 20 and -20 < sy < HEIGHT + 20):
            return
        off = pl = pr = 0.0
        if self.andando:
            off = abs(math.sin(self.frame)) * 3 - 1.5
            pl  = math.sin(self.frame) * 4
            pr  = math.sin(self.frame + math.pi) * 4
        ioff, ipl, ipr = int(off), int(pl), int(pr)
        r, g, b = self.cor
        pygame.draw.ellipse(screen, (0, 0, 0), (sx - 5, sy + self.tamanho - 2, 18, 6))
        pygame.draw.rect(screen, (80, 50, 30), (sx,     sy + 7 + ipl, 4, 6))
        pygame.draw.rect(screen, (80, 50, 30), (sx + 5, sy + 7 + ipr, 4, 6))
        corpo = (max(0, r-60), max(0, g-60), max(0, b-60))
        pygame.draw.rect(screen, corpo, (sx, sy + ioff, 9, 10), border_radius=3)
        pygame.draw.circle(screen, (220, 180, 120), (sx + 4, sy - 4 + ioff), 5)
        pygame.draw.ellipse(screen, (r, g, b), (sx - 4, sy - 8 + ioff, 17, 6))
        pygame.draw.rect(screen,   (r, g, b), (sx + 1, sy - 11 + ioff, 7, 5), border_radius=2)
        if self.estoque:
            pygame.draw.rect(screen, (200, 160, 80),
                             (sx + 9, sy + 2 + ioff, 5, self.estoque + 2), border_radius=1)
        if not self.andando and self.alvo_item:
            self._desenhar_ferramenta(screen, sx, sy)

    def _desenhar_ferramenta(self, screen: pygame.Surface, sx: int, sy: int) -> None:
        tipo = _FERRAMENTA.get(self.alvo_item or "", "vassoura")
        mx   = sx + 12
        my   = sy + 4 + int(math.sin(self.frame * 2) * 5)
        if tipo == "picareta":
            pygame.draw.line(screen, (100, 60, 20), (mx-2, my+4), (mx+6, my-8), 2)
            pygame.draw.polygon(screen, (180,180,180), [(mx+8,my-12),(mx+2,my-6),(mx+10,my-4)])
        elif tipo == "martelo":
            pygame.draw.line(screen, (100, 60, 20), (mx, my+6), (mx+4, my-4), 3)
            pygame.draw.rect(screen, (150,150,150), (mx+2, my-6, 8, 5))
        elif tipo == "prancheta":
            pygame.draw.rect(screen, (220,220,200),
                             (mx, sy + 4 + int(math.sin(self.frame*4)*2) - 2, 6, 8))
        elif tipo == "digital":
            my2 = sy + 4 + int(math.sin(self.frame * 5) * 3)
            pygame.draw.line(screen, (200,200,200), (mx, my2+2), (mx+8, my2-2), 2)
        else:
            pygame.draw.line(screen, (150,100,50), (mx-4, my+8), (mx+4, my-8), 2)
            pygame.draw.line(screen, (100,100,100), (mx+2, my-8), (mx+8, my-6), 2)


# ─────────────────────────────────────────────────────────
#  GERENCIADOR
# ─────────────────────────────────────────────────────────
class GerenciadorNPCs:
    """Fachada pública: adicionar_npc, atualizar, desenhar, desenhar_hud_mercado."""

    def __init__(self) -> None:
        self._npcs      = {c: [] for c in CAMADAS}
        self._carrinhos = {c: [] for c in CAMADAS if c != "superficie"}
        self._contagem  = {c: {e.nome: 0 for e in EMPRESAS} for c in CAMADAS}

    def adicionar_npc(self, camada: str, gx: int, gy: int) -> None:
        emp = random.choice(EMPRESAS)
        vel = random.uniform(0.8, 2.0) if camada == "superficie" else random.uniform(0.5, 1.2)
        self._npcs[camada].append(NPC(gx, gy, emp, vel))
        self._contagem[camada][emp.nome] = self._contagem[camada].get(emp.nome, 0) + 1
        if camada.startswith("caverna_"):
            lista = self._carrinhos.setdefault(camada, [])
            if sum(1 for c in lista if c.empresa == emp.nome) < MAX_CARRINHOS:
                lista.append(CarrinhoMineracao(emp, gx, gy))

    def atualizar(self, camada_atual: str, grid: list) -> None:
        for npc in self._npcs.get(camada_atual, []):
            npc.atualizar(grid)
        if camada_atual.startswith("caverna_"):
            for c in self._carrinhos.get(camada_atual, []):
                c.atualizar(grid)
        global_cnt: dict[str, int] = {e.nome: 0 for e in EMPRESAS}
        for dados in self._contagem.values():
            for nome, qtd in dados.items():
                global_cnt[nome] += qtd
        mercado.atualizar(global_cnt)

    def desenhar(self, screen: pygame.Surface, camera, camada_atual: str) -> None:
        for npc in self._npcs.get(camada_atual, []):
            npc.desenhar(screen, camera)
        if camada_atual.startswith("caverna_"):
            for c in self._carrinhos.get(camada_atual, []):
                c.desenhar(screen, camera)

    def desenhar_hud_mercado(self, screen: pygame.Surface, font_small: pygame.font.Font,
                              painel_x: int, y_inicio: int) -> None:
        PAD = painel_x + 10;  LARGURA = 155
        LINHA_H = 13;         SPARK_H = 12
        y = y_inicio

        pygame.draw.line(screen, (70,70,50), (PAD, y), (PAD+LARGURA, y), 1)
        y += 5
        screen.blit(font_small.render("BOLSA DE VALORES", True, (180,170,60)), (PAD, y))
        y += 15

        for emp in EMPRESAS:
            preco = mercado.get_preco(emp.nome)
            var   = mercado.get_variacao(emp.nome)
            hist  = mercado.historico[emp.nome]
            cor   = emp.cor
            pygame.draw.rect(screen, cor, (PAD, y+3, 7, 7))
            tc = (255,220,50) if emp.nome == mercado.lider else (190,190,190)
            screen.blit(font_small.render(emp.nome[:8], True, tc), (PAD+11, y))
            ps = font_small.render(formatar_preco(preco), True, tc)
            screen.blit(ps, (PAD+LARGURA - ps.get_width() - 14, y))
            seta, sc = ("+", (80,220,80)) if var > 0.005 else ("-", (220,80,80)) if var < -0.005 else ("=", (160,160,160))
            screen.blit(font_small.render(seta, True, sc), (PAD+LARGURA-10, y))
            y += LINHA_H
            if len(hist) >= 2:
                ams = hist[-20:];  mn = min(ams);  rng = max(max(ams)-mn, 1e-9)
                pts = [(PAD + int(j*LARGURA/max(len(ams)-1,1)),
                        y + SPARK_H - int((v-mn)/rng*SPARK_H))
                       for j, v in enumerate(ams)]
                pygame.draw.line(screen, (50,50,45), (PAD, y+SPARK_H), (PAD+LARGURA, y+SPARK_H), 1)
                if len(pts) >= 2:
                    pygame.draw.lines(screen, cor, False, pts, 1)
            y += SPARK_H + 6

        pygame.draw.line(screen, (70,70,50), (PAD, y), (PAD+LARGURA, y), 1)
        y += 4
        screen.blit(font_small.render(f"Lider: {mercado.lider}", True, (255,215,0)), (PAD, y))