"""
batalha.py — Sistema completo de ataque/defesa estilo Clash of Clans.

Fluxo:
  1. A cada INTERVALO_INVASAO frames, sorteia % de chance de invasão
  2. Se ativada, gera horda de NPCs atacantes com tipo e HP variados
  3. Cada atacante tem um alvo (construção viva) e caminha até ela no mapa
  4. Ao chegar: destrói a construção (remove do grid, marca destruida)
  5. Defensores interceptam atacantes e combatem em tempo real
  6. Após o raid: NPCs reconstruidores aparecem e rebuildam com custo de recursos
  7. Resultado é registrado e repassado ao GerenciadorQuests
"""
from __future__ import annotations

import math
import random
from typing import TYPE_CHECKING

import pygame

from config import COLS, GRID_SIZE, HEIGHT, MAP_WIDTH, ROWS
from vila import ConstrucaoViva, Tropa, Vila

if TYPE_CHECKING:
    from estado import EstadoJogo

# ── Parâmetros ───────────────────────────────────────────
INTERVALO_INVASAO  = 1800   # frames entre tentativas (~30s a 60fps)
CHANCE_INVASAO_BASE = 0.25  # 25% base, sobe com o nível da vila
DANO_POR_FRAME     = 0.18   # dano que um atacante faz por frame ao chegar no alvo
DANO_DEFENSOR      = 0.12   # dano que defensor faz por frame ao atacante
ALCANCE_DEFENSOR   = 120    # pixels — defensor ataca se atacante estiver perto
VELOCIDADE_REBUILD = 0.4    # pixels por frame do NPC reconstrutor


class NPCAtacante:
    """Atacante visual que caminha até uma construção e a destrói."""

    __slots__ = (
        "tropa", "alvo", "chegou", "frame", "retirada",
    )

    def __init__(self, tropa: Tropa, alvo: ConstrucaoViva) -> None:
        self.tropa   = tropa
        self.alvo    = alvo
        self.chegou  = False
        self.frame   = 0.0
        self.retirada = False  # voltando após destruir

    @property
    def vivo(self) -> bool:
        return self.tropa.vivo and not self.retirada

    def atualizar(self, grid: list[list[str]], mundo) -> bool:
        """Retorna True se destruiu a construção neste frame."""
        if not self.tropa.vivo or self.retirada:
            return False

        self.frame += 0.2
        alvo_px = self.alvo.gx * GRID_SIZE + GRID_SIZE // 2
        alvo_py = self.alvo.gy * GRID_SIZE + GRID_SIZE // 2
        self.tropa.dest_x = float(alvo_px)
        self.tropa.dest_y = float(alvo_py)
        self.tropa.mover()

        dist = math.hypot(self.tropa.x - alvo_px, self.tropa.y - alvo_py)
        if dist < GRID_SIZE * 0.6:
            self.chegou = True
            # Aplica dano à construção
            destruida = self.alvo.sofrer_dano(DANO_POR_FRAME)
            if destruida:
                # Remove do grid visualmente
                try:
                    camada_grid = grid
                    camada_grid[self.alvo.gy][self.alvo.gx] = mundo.get_base_tile()
                except (IndexError, AttributeError):
                    pass
                self.retirada = True
                return True
        return False

    def desenhar(self, screen: pygame.Surface, camera) -> None:
        if not self.tropa.vivo:
            return
        sx, sy = camera.aplicar(int(self.tropa.x), int(self.tropa.y))
        if not (-20 < sx < MAP_WIDTH + 20 and -20 < sy < HEIGHT + 20):
            return

        r, g, b = self.tropa.cor
        off = abs(math.sin(self.frame)) * 2

        # Sombra
        pygame.draw.ellipse(screen, (0,0,0), (sx-5, sy+8, 18, 5))
        # Pernas
        pygame.draw.rect(screen, (60,40,20), (sx,     sy+6+int(math.sin(self.frame)*3), 4,5))
        pygame.draw.rect(screen, (60,40,20), (sx+5,   sy+6+int(math.sin(self.frame+math.pi)*3), 4,5))
        # Corpo
        pygame.draw.rect(screen, (r,g,b), (sx, sy+int(off), 9,9), border_radius=2)
        # Cabeça — caveira/elmo
        pygame.draw.circle(screen, (r,g,b), (sx+4, sy-3+int(off)), 5)
        pygame.draw.circle(screen, (200,200,200), (sx+3, sy-4+int(off)), 2)

        # Arma
        ax, ay = sx+10, sy+2+int(off)
        if self.tropa.tipo == "arqueiro":
            pygame.draw.line(screen, (180,120,40), (ax,ay+6),(ax+4,ay-6), 2)
        elif self.tropa.tipo == "guerreiro":
            pygame.draw.line(screen, (180,180,180),(ax,ay+4),(ax+2,ay-8),3)
            pygame.draw.rect(screen,(200,200,200),(ax+1,ay-8,5,3))
        else:
            pygame.draw.line(screen,(180,100,40),(ax,ay+6),(ax+6,ay-4),2)

        # Barra de HP
        bw = 14
        hp_w = int(self.tropa.pct_hp * bw)
        pygame.draw.rect(screen, (80,0,0),   (sx-2, sy-13, bw, 3))
        pygame.draw.rect(screen, (0,200,60), (sx-2, sy-13, hp_w, 3))

        # Se chegou no alvo: efeito de ataque
        if self.chegou:
            pygame.draw.circle(screen, (255,200,0), (sx+4, sy-3+int(off)), 7, 2)


class NPCReconstrutor:
    """NPC que caminha até uma construção destruída e a reconstrói."""

    __slots__ = ("x", "y", "alvo", "frame", "concluido")

    def __init__(self, alvo: ConstrucaoViva) -> None:
        # Aparece numa posição aleatória próxima
        self.x     = float(random.randint(0, COLS-1) * GRID_SIZE)
        self.y     = float(random.randint(0, ROWS-1) * GRID_SIZE)
        self.alvo  = alvo
        self.frame = 0.0
        self.concluido = False

    def atualizar(self, grid: list[list[str]], mundo) -> bool:
        """Retorna True quando a reconstrução terminou."""
        if self.concluido:
            return False
        self.frame += 0.15
        alvo_px = float(self.alvo.gx * GRID_SIZE + GRID_SIZE // 2)
        alvo_py = float(self.alvo.gy * GRID_SIZE + GRID_SIZE // 2)
        dx, dy = alvo_px - self.x, alvo_py - self.y
        dist = math.hypot(dx, dy)
        if dist > VELOCIDADE_REBUILD * 2:
            inv = VELOCIDADE_REBUILD / dist
            self.x += dx * inv
            self.y += dy * inv
        else:
            # Chegou: avança timer da construção
            concluiu = self.alvo.atualizar()
            if concluiu:
                # Restaura no grid
                try:
                    grid[self.alvo.gy][self.alvo.gx] = self.alvo.tipo
                except IndexError:
                    pass
                self.concluido = True
                return True
        return False

    def desenhar(self, screen: pygame.Surface, camera) -> None:
        if self.concluido:
            return
        sx, sy = camera.aplicar(int(self.x), int(self.y))
        if not (-20 < sx < MAP_WIDTH + 20 and -20 < sy < HEIGHT + 20):
            return
        off = abs(math.sin(self.frame)) * 2
        pygame.draw.ellipse(screen, (0,0,0), (sx-5, sy+8, 18, 5))
        pygame.draw.rect(screen, (80,50,30), (sx, sy+6+int(math.sin(self.frame)*3), 4,5))
        pygame.draw.rect(screen, (80,50,30), (sx+5, sy+6+int(math.sin(self.frame+math.pi)*3), 4,5))
        pygame.draw.rect(screen, (60,160,220), (sx, sy+int(off), 9,9), border_radius=2)
        pygame.draw.circle(screen, (220,180,120), (sx+4, sy-3+int(off)), 5)
        # Capacete de construtor
        pygame.draw.ellipse(screen, (255,200,50), (sx-3, sy-8+int(off), 15, 6))
        # Ferramenta (martelo)
        pygame.draw.line(screen, (120,80,40), (sx+10, sy+5+int(off)), (sx+14, sy-4+int(off)), 2)
        pygame.draw.rect(screen, (160,160,160), (sx+12, sy-6+int(off), 6,4))
        # Barra de progresso da reconstrução
        pct = self.alvo.pct_reconstrucao
        bw = 14
        pygame.draw.rect(screen, (40,40,40),   (sx-2, sy-14, bw, 3))
        pygame.draw.rect(screen, (100,180,255),(sx-2, sy-14, int(pct*bw), 3))


class GerenciadorBatalha:
    """
    Orquestra invasões NPC, combate defensor x atacante e reconstruções.
    Integração: chamar atualizar() e desenhar() a cada frame.
    """

    def __init__(self) -> None:
        self._timer:         int                  = INTERVALO_INVASAO
        self._atacantes:     list[NPCAtacante]    = []
        self._reconstrutores:list[NPCReconstrutor]= []
        self._defensores_ativos: list[Tropa]      = []
        self.em_invasao:     bool                  = False
        self.resultado_pendente: dict | None       = None
        self._invasoes_completadas: int            = 0

    # ── API pública ──────────────────────────────────────
    def atualizar(self, estado: "EstadoJogo", mundo) -> None:
        vila   = estado.vila_jogador
        grid   = mundo.get_grid_ativo()
        camada = mundo.camada_atual

        # Só processa invasão na superfície
        if camada != "superficie":
            self._tick_reconstrutores(grid, mundo)
            return

        if self.em_invasao:
            self._tick_invasao(vila, grid, mundo, estado)
        else:
            self._tick_reconstrutores(grid, mundo)
            self._timer -= 1
            if self._timer <= 0:
                self._timer = INTERVALO_INVASAO
                self._tentar_invasao(vila, grid, estado)

    def desenhar(self, screen: pygame.Surface, camera, camada_atual: str) -> None:
        if camada_atual != "superficie":
            return
        for a in self._atacantes:
            a.desenhar(screen, camera)
        for r in self._reconstrutores:
            r.desenhar(screen, camera)
        for d in self._defensores_ativos:
            self._desenhar_defensor(screen, camera, d)

    def desenhar_hud(self, screen: pygame.Surface, font_small, y: int, painel_x: int) -> int:
        """Desenha status de invasão no painel lateral. Retorna próximo y."""
        if not self.em_invasao and not self._reconstrutores:
            return y
        PAD = painel_x + 10
        cor_titulo = (220,80,80) if self.em_invasao else (60,160,220)
        txt = "!! INVASAO !!" if self.em_invasao else "Reconstruindo..."
        screen.blit(font_small.render(txt, True, cor_titulo), (PAD, y)); y += 14
        vivos = sum(1 for a in self._atacantes if a.vivo)
        if self.em_invasao:
            screen.blit(font_small.render(f"Inimigos: {vivos}", True, (220,80,80)), (PAD, y)); y += 13
        recons = sum(1 for r in self._reconstrutores if not r.concluido)
        if recons:
            screen.blit(font_small.render(f"Reconstruindo: {recons}", True, (60,160,220)), (PAD, y)); y += 13
        return y + 4

    # ── Internos ─────────────────────────────────────────
    def _tentar_invasao(self, vila: Vila, grid, estado) -> None:
        if not vila.pode_ser_invadida():
            return
        construcoes = vila.construcoes_intactas("superficie")
        if not construcoes:
            return
        chance = CHANCE_INVASAO_BASE + estado.nivel * 0.01
        if random.random() > chance:
            return
        # Gera atacantes
        n_atacantes = random.randint(2, 4 + estado.nivel // 2)
        tipos_pool  = ["saqueador"] * 3 + ["guerreiro"] * 2 + ["arqueiro"]
        for _ in range(n_atacantes):
            alvo = random.choice(construcoes)
            # Posição inicial: borda aleatória do mapa
            borda = random.choice(["top","bot","left","right"])
            if borda == "top":
                tx, ty = random.randint(0,COLS-1)*GRID_SIZE, 0
            elif borda == "bot":
                tx, ty = random.randint(0,COLS-1)*GRID_SIZE, (ROWS-1)*GRID_SIZE
            elif borda == "left":
                tx, ty = 0, random.randint(0,ROWS-1)*GRID_SIZE
            else:
                tx, ty = (COLS-1)*GRID_SIZE, random.randint(0,ROWS-1)*GRID_SIZE
            tipo  = random.choice(tipos_pool)
            tropa = Tropa(tipo=tipo, x=float(tx), y=float(ty))
            self._atacantes.append(NPCAtacante(tropa, alvo))

        # Ativa defensores da vila
        self._defensores_ativos = [
            Tropa(tipo=d.tipo, x=d.x, y=d.y, defende=True)
            for d in vila.defensores
        ]
        self.em_invasao       = True
        vila.em_invasao       = True
        vila.cooldown_invasao = INTERVALO_INVASAO
        estado.exibir_mensagem("!! INVASAO DETECTADA !!")

    def _tick_invasao(self, vila: Vila, grid, mundo, estado) -> None:
        construcoes_destruidas = 0

        # Atacantes
        for atk in self._atacantes:
            if atk.vivo:
                destruiu = atk.atualizar(grid, mundo)
                if destruiu:
                    construcoes_destruidas += 1
                    # Agenda reconstrução
                    self._reconstrutores.append(NPCReconstrutor(atk.alvo))

        # Defensores vs atacantes
        for defensor in self._defensores_ativos:
            if not defensor.vivo:
                continue
            # Busca atacante mais próximo
            alvo_atk = None
            menor_dist = float("inf")
            for atk in self._atacantes:
                if not atk.vivo:
                    continue
                dist = math.hypot(defensor.x - atk.tropa.x, defensor.y - atk.tropa.y)
                if dist < ALCANCE_DEFENSOR and dist < menor_dist:
                    menor_dist = dist
                    alvo_atk   = atk
            if alvo_atk:
                alvo_atk.tropa.sofrer_dano(DANO_DEFENSOR)
                defensor.sofrer_dano(DANO_POR_FRAME * 0.5)
                # Move defensor em direção ao atacante
                dx = alvo_atk.tropa.x - defensor.x
                dy = alvo_atk.tropa.y - defensor.y
                dist = math.hypot(dx, dy)
                if dist > 20:
                    inv = defensor.velocidade / dist
                    defensor.x += dx * inv
                    defensor.y += dy * inv

        # Remove mortos
        self._atacantes[:] = [a for a in self._atacantes if not a.retirada and a.tropa.vivo or not a.tropa.vivo and not a.retirada]

        # Verifica fim
        todos_mortos   = all(not a.vivo for a in self._atacantes)
        todos_retirados= all(a.retirada or not a.tropa.vivo for a in self._atacantes)

        if todos_mortos or todos_retirados:
            vivos_def = sum(1 for d in self._defensores_ativos if d.vivo)
            vitoria_defesa = vivos_def > 0 or construcoes_destruidas == 0
            self._finalizar_invasao(vila, estado, construcoes_destruidas, vitoria_defesa)

    def _finalizar_invasao(self, vila: Vila, estado, destruidas: int, vitoria: bool) -> None:
        self.em_invasao = False
        vila.em_invasao = False
        self._atacantes.clear()
        self._defensores_ativos.clear()
        self._invasoes_completadas += 1

        if vitoria:
            estado.quests.on_invasao_repelida()
            bonus = 200 * (1 + estado.nivel)
            estado.dinheiro += bonus
            estado.exibir_mensagem(f"Invasao repelida! +${bonus:,}")
        else:
            roubo = min(estado.dinheiro * 0.1, 500.0)
            estado.dinheiro = max(0, estado.dinheiro - roubo)
            estado.exibir_mensagem(f"Invasao! -{destruidas} construcoes destruidas")

        self.resultado_pendente = {
            "vitoria": vitoria,
            "destruidas": destruidas,
            "invasoes_total": self._invasoes_completadas,
        }

    def _tick_reconstrutores(self, grid, mundo) -> None:
        for r in self._reconstrutores:
            if not r.concluido:
                concluiu = r.atualizar(grid, mundo)

    def _desenhar_defensor(self, screen: pygame.Surface, camera, d: Tropa) -> None:
        if not d.vivo:
            return
        sx, sy = camera.aplicar(int(d.x), int(d.y))
        if not (-20 < sx < MAP_WIDTH+20 and -20 < sy < HEIGHT+20):
            return
        r, g, b = d.cor
        pygame.draw.ellipse(screen, (0,0,0), (sx-5, sy+8, 18,5))
        pygame.draw.rect(screen, (40,80,40), (sx, sy, 10,10), border_radius=2)
        pygame.draw.circle(screen, (220,180,120), (sx+4, sy-4), 5)
        pygame.draw.ellipse(screen, (r,g,b), (sx-3, sy-9, 15,6))
        # Escudo
        pygame.draw.rect(screen, (r,g,b), (sx-6, sy+1, 5, 8), border_radius=1)
        pygame.draw.rect(screen, (255,255,255), (sx-6,sy+1,5,8),1,border_radius=1)
        # HP
        bw = 14
        hp_w = int(d.pct_hp * bw)
        pygame.draw.rect(screen,(80,0,0),(sx-2,sy-13,bw,3))
        pygame.draw.rect(screen,(0,220,60),(sx-2,sy-13,hp_w,3))


# Singleton
gerenciador_batalha = GerenciadorBatalha()