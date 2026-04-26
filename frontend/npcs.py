import pygame
import random
import math
from config import GRID_SIZE, COLS, ROWS, MAP_WIDTH, HEIGHT

# ═══════════════════════════════════════════════════════
#  EMPRESAS — dados estáticos
# ═══════════════════════════════════════════════════════
EMPRESAS = [
    {"nome": "AgroMax",   "cor": (220, 80,  80),  "cor_carrinho": (200, 60,  60)},
    {"nome": "TechVerde", "cor": (80,  200, 100), "cor_carrinho": (60,  180, 80)},
    {"nome": "BlueMine",  "cor": (80,  130, 220), "cor_carrinho": (60,  110, 200)},
    {"nome": "GoldRush",  "cor": (220, 180, 50),  "cor_carrinho": (200, 160, 30)},
]

MAX_CARRINHOS = 6

# ═══════════════════════════════════════════════════════
#  MERCADO GLOBAL — simulacao de bolsa de valores
# ═══════════════════════════════════════════════════════
class MercadoGlobal:
    TICK_FRAMES   = 180
    RUIDO_BASE    = 0.04
    VARIACAO_MAX  = 0.18
    PRECO_INICIAL = 10.0
    PRECO_MIN     = 2.0
    PRECO_MAX     = 200.0
    HIST_MAX      = 40

    def __init__(self):
        self.precos    = {e["nome"]: self.PRECO_INICIAL for e in EMPRESAS}
        self.historico = {e["nome"]: [self.PRECO_INICIAL] for e in EMPRESAS}
        self.variacao  = {e["nome"]: 0.0 for e in EMPRESAS}
        self.lider     = EMPRESAS[0]["nome"]
        self._timer    = 0
        self._drift    = {e["nome"]: random.uniform(-0.005, 0.005) for e in EMPRESAS}

    def atualizar(self, contagem):
        self._timer += 1
        if self._timer < self.TICK_FRAMES:
            return
        self._timer = 0

        total = max(1, sum(contagem.values()))

        for emp in EMPRESAS:
            nome  = emp["nome"]
            preco = self.precos[nome]
            share = contagem.get(nome, 0) / total

            ruido   = random.uniform(-self.RUIDO_BASE, self.RUIDO_BASE)
            pressao = self.VARIACAO_MAX * (0.5 - share)

            drift = self._drift[nome]
            self._drift[nome] = max(-0.01, min(0.01, drift + random.uniform(-0.001, 0.001)))

            evento = 0.0
            if random.random() < 0.05:
                evento = random.choice([-0.12, -0.08, 0.10, 0.15])

            media    = self.PRECO_INICIAL * 2
            reversao = (media - preco) * 0.005

            fator = 1.0 + ruido + pressao + drift + evento + reversao / max(preco, 1)
            novo  = max(self.PRECO_MIN, min(self.PRECO_MAX, preco * fator))

            self.variacao[nome] = (novo - preco) / max(preco, 0.01)
            self.precos[nome]   = round(novo, 2)
            self.historico[nome].append(novo)
            if len(self.historico[nome]) > self.HIST_MAX:
                self.historico[nome].pop(0)

        self.lider = max(self.precos, key=self.precos.get)

    def get_preco(self, nome):
        return self.precos.get(nome, self.PRECO_INICIAL)

    def get_variacao(self, nome):
        return self.variacao.get(nome, 0.0)


mercado = MercadoGlobal()


# ═══════════════════════════════════════════════════════
#  CARRINHO DE MINERACAO
# ═══════════════════════════════════════════════════════
class CarrinhoMineracao:
    def __init__(self, empresa_info, gx, gy):
        self.empresa    = empresa_info["nome"]
        self.cor        = empresa_info["cor_carrinho"]
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

    def _novo_destino(self, grid):
        construcoes = [
            (gx, gy)
            for gy in range(ROWS)
            for gx in range(COLS)
            if grid[gy][gx] not in ("pedra", "elevador")
        ]
        if construcoes:
            gx, gy = random.choice(construcoes)
            self.dest_x = gx * GRID_SIZE + GRID_SIZE // 2 + random.randint(-8, 8)
            self.dest_y = gy * GRID_SIZE + GRID_SIZE // 2 + random.randint(-8, 8)
        else:
            self.dest_x = random.randint(1, COLS - 2) * GRID_SIZE + GRID_SIZE // 2
            self.dest_y = random.randint(1, ROWS - 2) * GRID_SIZE + GRID_SIZE // 2
        self._timer = random.randint(90, 240)

    def atualizar(self, grid):
        self._timer -= 1
        if self._timer <= 0:
            self.carga = 0 if self.carga >= self.max_carga else min(self.max_carga, self.carga + random.randint(0, 2))
            self._novo_destino(grid)

        dx   = self.dest_x - self.x
        dy   = self.dest_y - self.y
        dist = math.hypot(dx, dy)
        if dist > self.velocidade:
            self.x      += (dx / dist) * self.velocidade
            self.y      += (dy / dist) * self.velocidade
            self.andando = True
            self.frame  += 0.3
        else:
            self.x = self.dest_x
            self.y = self.dest_y
            self.andando = False
            self.frame  += 0.1

    def desenhar(self, screen, camera):
        sx, sy = camera.aplicar(int(self.x), int(self.y))
        if sx < -30 or sx > MAP_WIDTH + 30 or sy < -30 or sy > HEIGHT + 30:
            return

        vib = int(math.sin(self.frame * 4) * 1.5) if self.andando else 0
        sy += vib
        r, g, b = self.cor

        pygame.draw.ellipse(screen, (0, 0, 0), (sx - 12, sy + 8, 28, 7))
        pygame.draw.line(screen, (60, 55, 50), (sx - 14, sy + 12), (sx + 14, sy + 12), 2)

        for rx in (sx - 8, sx + 8):
            pygame.draw.circle(screen, (30, 30, 30), (rx, sy + 8), 5)
            pygame.draw.circle(screen, (80, 80, 80), (rx, sy + 8), 3)
            ang = self.frame * (2 if self.andando else 0.3)
            pygame.draw.line(screen, (120, 120, 120),
                             (rx, sy + 8),
                             (rx + int(math.cos(ang) * 2), sy + 8 + int(math.sin(ang) * 2)), 1)

        pygame.draw.rect(screen, (r, g, b), (sx - 10, sy - 4, 20, 12), border_radius=2)
        pygame.draw.rect(screen, (min(255, r+40), min(255, g+40), min(255, b+40)),
                         (sx - 10, sy - 4, 20, 4), border_radius=2)

        if self.carga > 0:
            bw = int((self.carga / self.max_carga) * 16)
            pygame.draw.rect(screen, (50, 220, 100), (sx - 8, sy - 2, bw, 3))

        try:
            _f = pygame.font.SysFont("arial", 8, bold=True)
            screen.blit(_f.render(self.empresa[0], True, (255, 255, 255)), (sx - 3, sy))
        except Exception:
            pass


# ═══════════════════════════════════════════════════════
#  NPC  (trabalhador)
# ═══════════════════════════════════════════════════════
class NPC:
    def __init__(self, x, y, empresa_info, velocidade=1.5):
        self.empresa     = empresa_info["nome"]
        self.cor         = empresa_info["cor"]
        self.x           = float(x * GRID_SIZE + GRID_SIZE // 4)
        self.y           = float(y * GRID_SIZE + GRID_SIZE // 4)
        self.velocidade  = velocidade
        self.tamanho     = 10
        self.dest_x      = self.x
        self.dest_y      = self.y
        self._timer      = 0
        self.andando     = False
        self.frame       = 0.0
        self.alvo_item   = None
        self.estoque     = 0
        self.max_estoque = 5

    def _novo_destino(self, grid):
        construcoes = [
            (gx, gy)
            for gy in range(ROWS)
            for gx in range(COLS)
            if grid[gy][gx] not in ("grama", "pedra", "elevador")
        ]
        if construcoes:
            gx, gy = random.choice(construcoes)
            self.dest_x    = gx * GRID_SIZE + random.randint(GRID_SIZE // 4, 3 * GRID_SIZE // 4)
            self.dest_y    = gy * GRID_SIZE + random.randint(GRID_SIZE // 4, 3 * GRID_SIZE // 4)
            self.alvo_item = grid[gy][gx]
        else:
            gx = int(self.x // GRID_SIZE)
            gy = int(self.y // GRID_SIZE)
            nx = random.randint(max(0, gx - 5), min(COLS - 1, gx + 5))
            ny = random.randint(max(0, gy - 5), min(ROWS - 1, gy + 5))
            self.dest_x    = nx * GRID_SIZE + GRID_SIZE // 2
            self.dest_y    = ny * GRID_SIZE + GRID_SIZE // 2
            self.alvo_item = None
        self._timer = random.randint(60, 180)

    def atualizar(self, grid):
        self._timer -= 1
        if self._timer <= 0:
            if self.alvo_item and self.estoque > 0:
                self.estoque = 0
            else:
                self.estoque = min(self.max_estoque, self.estoque + random.randint(1, 3))
            self._novo_destino(grid)

        dx   = self.dest_x - self.x
        dy   = self.dest_y - self.y
        dist = math.hypot(dx, dy)
        if dist > self.velocidade:
            self.x      += (dx / dist) * self.velocidade
            self.y      += (dy / dist) * self.velocidade
            self.andando = True
            self.frame  += 0.2
        else:
            self.x = self.dest_x
            self.y = self.dest_y
            self.andando = False
            self.frame  += 0.1

    def desenhar(self, screen, camera):
        sx, sy = camera.aplicar(int(self.x), int(self.y))
        if sx < -20 or sx > MAP_WIDTH + 20 or sy < -20 or sy > HEIGHT + 20:
            return

        off = pl = pr = 0
        if self.andando:
            off = abs(math.sin(self.frame)) * 3 - 1.5
            pl  = math.sin(self.frame) * 4
            pr  = math.sin(self.frame + math.pi) * 4

        pygame.draw.ellipse(screen, (0, 0, 0), (sx - 5, sy + self.tamanho - 2, 18, 6))
        pygame.draw.rect(screen, (80, 50, 30), (sx,     sy + 7 + int(pl), 4, 6))
        pygame.draw.rect(screen, (80, 50, 30), (sx + 5, sy + 7 + int(pr), 4, 6))

        r, g, b = self.cor
        corpo = (max(0, r - 60), max(0, g - 60), max(0, b - 60))
        pygame.draw.rect(screen, corpo, (sx, sy + int(off), 9, 10), border_radius=3)
        pygame.draw.circle(screen, (220, 180, 120), (sx + 4, sy - 4 + int(off)), 5)
        pygame.draw.ellipse(screen, (r, g, b), (sx - 4, sy - 8 + int(off), 17, 6))
        pygame.draw.rect(screen,   (r, g, b), (sx + 1, sy - 11 + int(off), 7, 5), border_radius=2)

        if self.estoque > 0:
            pygame.draw.rect(screen, (200, 160, 80),
                             (sx + 9, sy + 2 + int(off), 5, self.estoque + 2), border_radius=1)

        if not self.andando and self.alvo_item:
            fy   = math.sin(self.frame * 2) * 5
            mx_  = sx + 12
            my_  = sy + 4 + int(fy)
            tipo = self.alvo_item
            if tipo in ("mineracao", "cristal"):
                pygame.draw.line(screen, (100, 60, 20), (mx_-2, my_+4), (mx_+6, my_-8), 2)
                pygame.draw.polygon(screen, (180,180,180), [(mx_+8,my_-12),(mx_+2,my_-6),(mx_+10,my_-4)])
            elif tipo == "forja":
                pygame.draw.line(screen, (100, 60, 20), (mx_, my_+6), (mx_+4, my_-4), 3)
                pygame.draw.rect(screen, (150,150,150), (mx_+2, my_-6, 8, 5))
            elif tipo == "laboratorio":
                my_ = sy + 4 + int(math.sin(self.frame * 4) * 2)
                pygame.draw.rect(screen, (220,220,200), (mx_, my_-2, 6, 8))
            elif tipo in ("reator", "cripto"):
                my_ = sy + 4 + int(math.sin(self.frame * 5) * 3)
                pygame.draw.line(screen, (200,200,200), (mx_, my_+2), (mx_+8, my_-2), 2)
            else:
                pygame.draw.line(screen, (150,100,50), (mx_-4, my_+8), (mx_+4, my_-8), 2)
                pygame.draw.line(screen, (100,100,100), (mx_+2, my_-8), (mx_+8, my_-6), 2)


# ═══════════════════════════════════════════════════════
#  GERENCIADOR PRINCIPAL
# ═══════════════════════════════════════════════════════
class GerenciadorNPCs:
    CAMADAS = ["superficie", "caverna_1", "caverna_2", "caverna_3", "caverna_4"]

    def __init__(self):
        self.npcs_por_camada = {c: [] for c in self.CAMADAS}
        self.carrinhos_por_caverna = {c: [] for c in self.CAMADAS if c != "superficie"}
        # contagem de construcoes por empresa (alimenta o mercado)
        self._contagem = {c: {e["nome"]: 0 for e in EMPRESAS} for c in self.CAMADAS}

    def adicionar_npc(self, camada, gx, gy):
        empresa_info = random.choice(EMPRESAS)
        nome = empresa_info["nome"]
        vel  = random.uniform(0.8, 2.0) if camada == "superficie" else random.uniform(0.5, 1.2)

        self.npcs_por_camada[camada].append(NPC(gx, gy, empresa_info, vel))
        self._contagem[camada][nome] = self._contagem[camada].get(nome, 0) + 1

        if camada.startswith("caverna_"):
            lista = self.carrinhos_por_caverna.setdefault(camada, [])
            if sum(1 for c in lista if c.empresa == nome) < MAX_CARRINHOS:
                lista.append(CarrinhoMineracao(empresa_info, gx, gy))

    def atualizar(self, camada_atual, grid):
        for npc in self.npcs_por_camada.get(camada_atual, []):
            npc.atualizar(grid)

        if camada_atual.startswith("caverna_"):
            for carrinho in self.carrinhos_por_caverna.get(camada_atual, []):
                carrinho.atualizar(grid)

        # mercado usa soma global de todas as camadas
        contagem_global = {e["nome"]: 0 for e in EMPRESAS}
        for camada_data in self._contagem.values():
            for nome, qtd in camada_data.items():
                contagem_global[nome] += qtd
        mercado.atualizar(contagem_global)

    def desenhar(self, screen, camera, camada_atual):
        for npc in self.npcs_por_camada.get(camada_atual, []):
            npc.desenhar(screen, camera)
        if camada_atual.startswith("caverna_"):
            for carrinho in self.carrinhos_por_caverna.get(camada_atual, []):
                carrinho.desenhar(screen, camera)

    def desenhar_hud_mercado(self, screen, font_small, painel_x, y_inicio):
        PAD     = painel_x + 10
        LARGURA = 155
        y       = y_inicio

        pygame.draw.line(screen, (70, 70, 50), (PAD, y), (PAD + LARGURA, y), 1)
        y += 5
        screen.blit(font_small.render("BOLSA DE VALORES", True, (180, 170, 60)), (PAD, y))
        y += 15

        LINHA_H = 13
        SPARK_H = 12

        for emp in EMPRESAS:
            nome  = emp["nome"]
            preco = mercado.get_preco(nome)
            var   = mercado.get_variacao(nome)
            hist  = mercado.historico[nome]
            cor   = emp["cor"]

            # quadradinho colorido
            pygame.draw.rect(screen, cor, (PAD, y + 3, 7, 7))

            eh_lider = (nome == mercado.lider)
            txt_cor  = (255, 220, 50) if eh_lider else (190, 190, 190)
            screen.blit(font_small.render(nome[:8], True, txt_cor), (PAD + 11, y))

            preco_str = f"${preco:.1f}"
            ps = font_small.render(preco_str, True, txt_cor)
            screen.blit(ps, (PAD + LARGURA - ps.get_width() - 14, y))

            # seta ASCII pura
            if var > 0.005:
                seta, sc = "+", (80, 220, 80)
            elif var < -0.005:
                seta, sc = "-", (220, 80, 80)
            else:
                seta, sc = "=", (160, 160, 160)
            screen.blit(font_small.render(seta, True, sc), (PAD + LARGURA - 10, y))

            y += LINHA_H

            # sparkline
            if len(hist) >= 2:
                amostras = hist[-20:]
                mn  = min(amostras)
                mx  = max(amostras)
                rng = max(mx - mn, 0.01)
                pts = []
                for j, v in enumerate(amostras):
                    px = PAD + int(j * LARGURA / max(len(amostras) - 1, 1))
                    py = y + SPARK_H - int((v - mn) / rng * SPARK_H)
                    pts.append((px, py))
                pygame.draw.line(screen, (50, 50, 45), (PAD, y + SPARK_H), (PAD + LARGURA, y + SPARK_H), 1)
                if len(pts) >= 2:
                    pygame.draw.lines(screen, cor, False, pts, 1)

            y += SPARK_H + 6

        pygame.draw.line(screen, (70, 70, 50), (PAD, y), (PAD + LARGURA, y), 1)
        y += 4
        screen.blit(font_small.render(f"Lider: {mercado.lider}", True, (255, 215, 0)), (PAD, y))