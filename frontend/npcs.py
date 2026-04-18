import pygame
import random
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

    def _novo_destino(self):
        """Escolhe uma célula aleatória próxima como destino"""
        alcance = 5
        gx = int(self.x // GRID_SIZE)
        gy = int(self.y // GRID_SIZE)

        nx = random.randint(max(0, gx - alcance), min(COLS - 1, gx + alcance))
        ny = random.randint(max(0, gy - alcance), min(ROWS - 1, gy + alcance))

        self.dest_x = nx * GRID_SIZE + GRID_SIZE // 2
        self.dest_y = ny * GRID_SIZE + GRID_SIZE // 2
        self.timer_destino = random.randint(60, 180)  # pausa em frames antes de mover de novo

    def atualizar(self):
        self.timer_destino -= 1

        if self.timer_destino <= 0:
            self._novo_destino()

        # Move em direção ao destino
        dx = self.dest_x - self.x
        dy = self.dest_y - self.y
        distancia = (dx**2 + dy**2) ** 0.5

        if distancia > self.velocidade:
            self.x += (dx / distancia) * self.velocidade
            self.y += (dy / distancia) * self.velocidade
        else:
            self.x = self.dest_x
            self.y = self.dest_y

    def desenhar(self, screen, camera):
        sx, sy = camera.aplicar(int(self.x), int(self.y))

        # Culling — não desenha se fora da tela
        if sx < -20 or sx > MAP_WIDTH + 20 or sy < -20 or sy > HEIGHT + 20:
            return

        # Sombra
        pygame.draw.ellipse(screen, (0, 0, 0, 80),
                            (sx - 5, sy + self.tamanho - 2, 18, 6))

        # Corpo (círculo)
        pygame.draw.circle(screen, self.cor, (sx + 4, sy + 4), self.tamanho // 2 + 2)

        # Cabeça
        pygame.draw.circle(screen, self.cor,
                           (sx + 4, sy - 4), self.tamanho // 2)

        # Contorno
        pygame.draw.circle(screen, (0, 0, 0),
                           (sx + 4, sy - 4), self.tamanho // 2, 1)


class GerenciadorNPCs:
    # Cores diferentes para variar os NPCs
    CORES = [
        (220, 180, 120),  # pele clara
        (180, 130, 80),   # pele média
        (120, 80, 40),    # pele escura
        (200, 100, 100),  # vermelho
        (100, 150, 200),  # azul
    ]

    def __init__(self, quantidade=10):
        self.npcs_superficie = self._criar_npcs(quantidade)
        self.npcs_caverna    = []  # caverna começa sem NPCs
        self.quantidade_base = quantidade

    def _criar_npcs(self, quantidade):
        npcs = []
        for _ in range(quantidade):
            x   = random.randint(0, COLS - 1)
            y   = random.randint(0, ROWS - 1)
            cor = random.choice(self.CORES)
            vel = random.uniform(0.8, 2.0)
            npcs.append(NPC(x, y, cor, vel))
        return npcs

    def adicionar_npc_caverna(self):
        """Chame isso quando o jogador construir algo na caverna"""
        x   = random.randint(0, COLS - 1)
        y   = random.randint(0, ROWS - 1)
        cor = (100, 200, 180)  # cor diferente para NPCs da caverna
        self.npcs_caverna.append(NPC(x, y, cor, random.uniform(0.5, 1.2)))

    def atualizar(self, camada_atual):
        lista = self.npcs_superficie if camada_atual == "superficie" else self.npcs_caverna
        for npc in lista:
            npc.atualizar()

    def desenhar(self, screen, camera, camada_atual):
        lista = self.npcs_superficie if camada_atual == "superficie" else self.npcs_caverna
        for npc in lista:
            npc.desenhar(screen, camera)