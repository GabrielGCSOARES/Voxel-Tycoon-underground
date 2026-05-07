"""vila.py — Sistema de vilas para jogador e rival com construções e defesas."""
from __future__ import annotations

import random
from typing import Final


class Vila:
    """Representa a vila de um jogador com construções, defesas e recursos."""

    __slots__ = (
        "nome", "dinheiro", "nivel", "construcoes", "defesas",
        "saude_total", "saude_atual", "tempo_proxima_invasao",
        "invasao_ativa", "tropas_defendendo",
    )

    def __init__(self, nome: str, dinheiro_inicial: float = 500.0) -> None:
        self.nome                = nome
        self.dinheiro            = dinheiro_inicial
        self.nivel               = 1
        self.construcoes: dict[str, int] = {}  # {"casa": 3, "fazenda": 2}
        self.defesas: dict[str, int]     = {}  # {"torre": 1, "muralha": 5}
        self.saude_total         = 100.0
        self.saude_atual         = 100.0
        self.tempo_proxima_invasao = 0
        self.invasao_ativa: Invasao | None = None
        self.tropas_defendendo: list[Tropa] = []

    def gerar_vila_rival(self) -> None:
        """Gera uma vila aleatória para o rival."""
        self.construcoes = {
            "palacio": random.randint(1, 3),
            "cachoeira": random.randint(1, 4),
            "silo": random.randint(2, 5),
            "fazenda": random.randint(3, 6),
        }
        self.defesas = {
            "torre": random.randint(2, 4),
            "muralha": random.randint(3, 7),
        }
        self.saude_total = 50.0 + self.nivel * 20
        self.saude_atual = self.saude_total
        self.dinheiro = 300.0 + self.nivel * 100

    def adicionar_construcao(self, tipo: str, qtd: int = 1) -> None:
        """Adiciona uma construção à vila."""
        self.construcoes[tipo] = self.construcoes.get(tipo, 0) + qtd
        self.saude_total += 10 * qtd

    def adicionar_defesa(self, tipo: str, qtd: int = 1) -> None:
        """Adiciona uma defesa à vila."""
        self.defesas[tipo] = self.defesas.get(tipo, 0) + qtd
        self.saude_total += 15 * qtd

    def sofrer_dano(self, dano: float) -> None:
        """Aplica dano à vila."""
        self.saude_atual = max(0, self.saude_atual - dano)

    def pode_ser_invadida(self) -> bool:
        """Verifica se a vila pode ser invadida novamente."""
        return self.tempo_proxima_invasao <= 0

    def atualizar(self) -> None:
        """Atualiza estado da vila a cada frame."""
        if self.tempo_proxima_invasao > 0:
            self.tempo_proxima_invasao -= 1
        if self.invasao_ativa:
            self.invasao_ativa.atualizar()

    def obter_valor_roubavel(self) -> float:
        """Calcula quanto dinheiro pode ser roubado."""
        return self.dinheiro * 0.5  # Máximo 50% do dinheiro

    def resumo(self) -> tuple[str, int, float, int]:
        """Retorna (nome, nível, saúde_atual, dinheiro)."""
        return (self.nome, self.nivel, int(self.saude_atual), int(self.dinheiro))


class Tropa:
    """Representa uma tropa que pode atacar ou defender."""

    __slots__ = (
        "tipo", "saude", "saude_max", "dano", "velocidade",
        "x", "y", "dest_x", "dest_y", "defende",
    )

    TIPOS: Final[dict[str, tuple[float, float]]] = {
        "soldado": (20.0, 5.0),      # saude, dano
        "cavaleiro": (40.0, 10.0),
        "arqueiro": (15.0, 12.0),
    }

    def __init__(self, tipo: str, x: float = 0.0, y: float = 0.0, defende: bool = False) -> None:
        self.tipo      = tipo
        saude, dano    = self.TIPOS.get(tipo, (20.0, 5.0))
        self.saude_max = saude
        self.saude     = saude
        self.dano      = dano
        self.velocidade = random.uniform(1.0, 2.0)
        self.x         = x
        self.y         = y
        self.dest_x    = x
        self.dest_y    = y
        self.defende   = defende

    def sofrer_dano(self, dano: float) -> bool:
        """Aplica dano e retorna True se morreu."""
        self.saude -= dano
        return self.saude <= 0

    def mover_para(self, x: float, y: float) -> None:
        """Define novo destino."""
        self.dest_x = x
        self.dest_y = y

    def atualizar(self) -> None:
        """Atualiza posição."""
        dx = self.dest_x - self.x
        dy = self.dest_y - self.y
        dist = (dx**2 + dy**2) ** 0.5
        if dist > self.velocidade:
            inv = self.velocidade / dist
            self.x += dx * inv
            self.y += dy * inv


class Invasao:
    """Representa uma invasão ativa na vila."""

    __slots__ = (
        "atacante_nome", "tempo_restante", "tropas_atacantes",
        "construcoes_destruidas", "dano_total",
    )

    def __init__(self, atacante_nome: str, tropas: list[Tropa]) -> None:
        self.atacante_nome       = atacante_nome
        self.tempo_restante      = 300  # 5 segundos em frames (60fps)
        self.tropas_atacantes    = tropas
        self.construcoes_destruidas = 0
        self.dano_total          = 0.0

    def atualizar(self) -> None:
        """Atualiza tropas e tempo de invasão."""
        self.tempo_restante -= 1
        for tropa in self.tropas_atacantes:
            tropa.atualizar()

    def acabou(self) -> bool:
        """Verifica se a invasão acabou."""
        return (
            self.tempo_restante <= 0
            or all(t.saude <= 0 for t in self.tropas_atacantes)
        )

    def resultado(self) -> dict:
        """Retorna o resultado da invasão."""
        tropas_vivas = [t for t in self.tropas_atacantes if t.saude > 0]
        vitoria = len(tropas_vivas) > 0
        return {
            "vitoria": vitoria,
            "atacante": self.atacante_nome,
            "tropas_vivas": len(tropas_vivas),
            "construcoes_destruidas": self.construcoes_destruidas,
            "dano_total": self.dano_total,
        }
