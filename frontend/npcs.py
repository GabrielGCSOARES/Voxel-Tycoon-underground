import pygame
import random
import math
from config import GRID_SIZE, COLS, ROWS, MAP_WIDTH, HEIGHT

class NPC:
    def __init__(self, x, y, cor, velocidade=1.5):
        self.x = float(x * GRID_SIZE + GRID_SIZE // 4)
        self.y = float(y * GRID_SIZE + GRID_SIZE // 4)
        self.cor = cor
        self.velocidade = velocidade
        self.tamanho = 10

        # Destino atual
        self.dest_x = self.x
        self.dest_y = self.y

        # Tempo até escolher novo destino
        self.timer_destino = 0

        # Animação
        self.andando = False
        self.frame_animacao = 0
        self.alvo_item = None

    def _novo_destino(self, grid):
        """Escolhe uma construção aleatória no grid como destino. Se não houver, anda ao acaso."""
        construcoes = []
        for gy in range(ROWS):
            for gx in range(COLS):
                if grid[gy][gx] not in ["grama", "pedra", "elevador"]:
                    construcoes.append((gx, gy))

        if construcoes:
            gx, gy = random.choice(construcoes)
            self.dest_x = gx * GRID_SIZE + random.randint(GRID_SIZE // 4, 3 * GRID_SIZE // 4)
            self.dest_y = gy * GRID_SIZE + random.randint(GRID_SIZE // 4, 3 * GRID_SIZE // 4)
            self.alvo_item = grid[gy][gx]
        else:
            alcance = 5
            gx = int(self.x // GRID_SIZE)
            gy = int(self.y // GRID_SIZE)
            nx = random.randint(max(0, gx - alcance), min(COLS - 1, gx + alcance))
            ny = random.randint(max(0, gy - alcance), min(ROWS - 1, gy + alcance))
            self.dest_x = nx * GRID_SIZE + GRID_SIZE // 2
            self.dest_y = ny * GRID_SIZE + GRID_SIZE // 2
            self.alvo_item = None

        self.timer_destino = random.randint(60, 180)  # pausa em frames antes de mover de novo

    def atualizar(self, grid):
        self.timer_destino -= 1

        if self.timer_destino <= 0:
            self._novo_destino(grid)

        # Move em direção ao destino
        dx = self.dest_x - self.x
        dy = self.dest_y - self.y
        distancia = (dx**2 + dy**2) ** 0.5

        if distancia > self.velocidade:
            self.x += (dx / distancia) * self.velocidade
            self.y += (dy / distancia) * self.velocidade
            self.andando = True
            self.frame_animacao += 0.2
        else:
            self.x = self.dest_x
            self.y = self.dest_y
            self.andando = False
            self.frame_animacao += 0.1 # Continua a animação para o trabalho

    def desenhar(self, screen, camera):
        sx, sy = camera.aplicar(int(self.x), int(self.y))

        # Culling — não desenha se fora da tela
        if sx < -20 or sx > MAP_WIDTH + 20 or sy < -20 or sy > HEIGHT + 20:
            return

        # Animação (bobbing)
        offset_y = 0
        passo_esq = 0
        passo_dir = 0
        if self.andando:
            offset_y = abs(math.sin(self.frame_animacao)) * 3 - 1.5
            passo_esq = math.sin(self.frame_animacao) * 4
            passo_dir = math.sin(self.frame_animacao + math.pi) * 4

        # Sombra
        pygame.draw.ellipse(screen, (0, 0, 0, 80),
                            (sx - 5, sy + self.tamanho - 2, 18, 6))

        # Pernas (se movendo)
        cor_bota = (80, 50, 30) # Marrom
        pygame.draw.rect(screen, cor_bota, (sx, sy + self.tamanho // 2 + 2 + passo_esq, 4, 6))
        pygame.draw.rect(screen, cor_bota, (sx + 5, sy + self.tamanho // 2 + 2 + passo_dir, 4, 6))

        # Corpo (Macacão)
        cor_macacao = (50, 100, 200) # Azul
        pygame.draw.rect(screen, cor_macacao, (sx, sy + offset_y, 9, 10), border_radius=3)

        # Cabeça
        pygame.draw.circle(screen, self.cor,
                           (sx + 4, sy - 4 + offset_y), self.tamanho // 2)

        # Chapéu de Palha (Fazendeiro)
        cor_chapeu = (220, 200, 100) # Amarelo palha
        pygame.draw.ellipse(screen, cor_chapeu, (sx - 4, sy - 8 + offset_y, 17, 6))
        pygame.draw.rect(screen, cor_chapeu, (sx + 1, sy - 11 + offset_y, 7, 5), border_radius=2)

        # Animações de trabalho (quando não está andando e chegou ao alvo)
        if not self.andando and self.alvo_item:
            ferramenta_y = math.sin(self.frame_animacao * 2) * 5
            
            # Mão/Ferramenta direita
            mao_x, mao_y = sx + 12, sy + 4 + ferramenta_y
            
            tipo = self.alvo_item
            if tipo in ["mineracao", "cristal"]:
                # Picareta
                pygame.draw.line(screen, (100, 60, 20), (mao_x - 2, mao_y + 4), (mao_x + 6, mao_y - 8), 2)
                pygame.draw.polygon(screen, (180, 180, 180), [(mao_x + 8, mao_y - 12), (mao_x + 2, mao_y - 6), (mao_x + 10, mao_y - 4)])
            elif tipo == "forja":
                # Martelo
                pygame.draw.line(screen, (100, 60, 20), (mao_x, mao_y + 6), (mao_x + 4, mao_y - 4), 3)
                pygame.draw.rect(screen, (150, 150, 150), (mao_x + 2, mao_y - 6, 8, 5))
            elif tipo == "laboratorio":
                # Prancheta
                mao_y = sy + 4 + math.sin(self.frame_animacao * 4) * 2
                pygame.draw.rect(screen, (220, 220, 200), (mao_x, mao_y - 2, 6, 8))
            elif tipo in ["reator", "cripto"]:
                # Ferramenta girando/digitando
                mao_y = sy + 4 + math.sin(self.frame_animacao * 5) * 3
                pygame.draw.line(screen, (200, 200, 200), (mao_x, mao_y + 2), (mao_x + 8, mao_y - 2), 2)
            else:
                # Vassoura/ancinho
                pygame.draw.line(screen, (150, 100, 50), (mao_x - 4, mao_y + 8), (mao_x + 4, mao_y - 8), 2)
                pygame.draw.line(screen, (100, 100, 100), (mao_x + 2, mao_y - 8), (mao_x + 8, mao_y - 6), 2)


class GerenciadorNPCs:
    # Cores diferentes para variar os NPCs
    CORES = [
        (220, 180, 120),  # pele clara
        (180, 130, 80),   # pele média
        (120, 80, 40),    # pele escura
        (200, 100, 100),  # vermelho
        (100, 150, 200),  # azul
    ]

    def __init__(self):
        self.npcs_por_camada = {
            "superficie": [],
            "caverna_1": [],
            "caverna_2": [],
            "caverna_3": [],
            "caverna_4": [],
        }

    def adicionar_npc(self, camada, x, y):
        """Chame isso quando o jogador construir algo no mapa"""
        if camada == "superficie":
            cor = random.choice(self.CORES)
            vel = random.uniform(0.8, 2.0)
            self.npcs_por_camada["superficie"].append(NPC(x, y, cor, vel))
        else:
            cor = (100, 200, 180)  # cor diferente para NPCs da caverna
            vel = random.uniform(0.5, 1.2)
            if camada not in self.npcs_por_camada:
                self.npcs_por_camada[camada] = []
            self.npcs_por_camada[camada].append(NPC(x, y, cor, vel))

    def atualizar(self, camada_atual, grid):
        lista = self.npcs_por_camada.get(camada_atual, [])
        for npc in lista:
            npc.atualizar(grid)

    def desenhar(self, screen, camera, camada_atual):
        lista = self.npcs_por_camada.get(camada_atual, [])
        for npc in lista:
            npc.desenhar(screen, camera)