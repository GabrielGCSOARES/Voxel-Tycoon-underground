"""
vila.py — Vila, Recursos, Construções com HP e sistema de reconstrução.

Cada construção tem HP individual.
Recursos (madeira, pedra) são produzidos pelas construções e gastos em reconstruções.
"""
from __future__ import annotations
import random
from dataclasses import dataclass, field
from typing import Final

# ── HP e custo de reconstrução por tipo ──────────────────
CONSTRUCAO_INFO: Final[dict[str, dict]] = {
    "casa":        {"hp": 60,  "madeira": 30, "pedra": 10, "tempo": 180},
    "fazenda":     {"hp": 50,  "madeira": 20, "pedra": 5,  "tempo": 120},
    "silo":        {"hp": 80,  "madeira": 40, "pedra": 20, "tempo": 240},
    "cachoeira":   {"hp": 70,  "madeira": 25, "pedra": 15, "tempo": 200},
    "palacio":     {"hp": 150, "madeira": 80, "pedra": 50, "tempo": 600},
    "mineracao":   {"hp": 90,  "madeira": 50, "pedra": 30, "tempo": 300},
    "cristal":     {"hp": 70,  "madeira": 30, "pedra": 40, "tempo": 360},
    "forja":       {"hp": 100, "madeira": 60, "pedra": 40, "tempo": 420},
    "laboratorio": {"hp": 80,  "madeira": 40, "pedra": 50, "tempo": 480},
    "reator":      {"hp": 120, "madeira": 50, "pedra": 80, "tempo": 720},
    "cripto":      {"hp": 100, "madeira": 40, "pedra": 60, "tempo": 600},
}
HP_PADRAO = {"hp": 50, "madeira": 20, "pedra": 10, "tempo": 150}

PRODUCAO_RECURSOS: Final[dict[str, dict]] = {
    "fazenda":   {"madeira": 0.05},
    "mineracao": {"pedra": 0.08},
    "silo":      {"madeira": 0.02, "pedra": 0.02},
    "forja":     {"pedra": 0.04},
    "cachoeira": {"madeira": 0.03},
}

@dataclass
class ConstrucaoViva:
    """Uma construção no mapa com HP próprio e estado de reconstrução."""
    tipo:   str
    gx:     int
    gy:     int
    camada: str
    hp_max: float = 0.0
    hp:     float = 0.0
    nivel:  int   = 1
    destruida:        bool  = False
    reconstruindo:    bool  = False
    timer_reconstrucao: int = 0

    def __post_init__(self) -> None:
        info = CONSTRUCAO_INFO.get(self.tipo, HP_PADRAO)
        self.hp_max = float(info["hp"]) * self.nivel
        if self.hp == 0.0:
            self.hp = self.hp_max

    def sofrer_dano(self, dano: float) -> bool:
        """Retorna True se foi destruída agora."""
        if self.destruida:
            return False
        self.hp = max(0.0, self.hp - dano)
        if self.hp <= 0:
            self.destruida = True
            return True
        return False

    def iniciar_reconstrucao(self) -> bool:
        """Inicia reconstrução se destruída e não reconstruindo. Retorna True se iniciou."""
        if not self.destruida or self.reconstruindo:
            return False
        info = CONSTRUCAO_INFO.get(self.tipo, HP_PADRAO)
        self.reconstruindo      = True
        self.timer_reconstrucao = info["tempo"]
        return True

    def atualizar(self) -> bool:
        """Retorna True quando terminou de reconstruir."""
        if not self.reconstruindo:
            return False
        self.timer_reconstrucao -= 1
        if self.timer_reconstrucao <= 0:
            self.hp          = self.hp_max
            self.destruida   = False
            self.reconstruindo = False
            return True
        return False

    @property
    def pct_hp(self) -> float:
        return self.hp / self.hp_max if self.hp_max > 0 else 0.0

    @property
    def pct_reconstrucao(self) -> float:
        info = CONSTRUCAO_INFO.get(self.tipo, HP_PADRAO)
        total = info["tempo"]
        restante = self.timer_reconstrucao
        return 1.0 - (restante / total) if total > 0 else 1.0

    def custo_reconstrucao(self) -> dict[str, int]:
        info = CONSTRUCAO_INFO.get(self.tipo, HP_PADRAO)
        return {"madeira": info["madeira"], "pedra": info["pedra"]}


# Fora do dataclass — dict mutável não pode ser field default no Python 3.10
_TROPA_STATS: Final[dict] = {
    "saqueador": {"hp": 30,  "dano": 8,  "vel": 2.0, "cor": (220, 80,  60)},
    "guerreiro": {"hp": 60,  "dano": 15, "vel": 1.4, "cor": (180, 60, 200)},
    "arqueiro":  {"hp": 25,  "dano": 20, "vel": 1.8, "cor": (60,  160, 220)},
    "defensor":  {"hp": 50,  "dano": 10, "vel": 1.2, "cor": (60,  200,  80)},
    "guardiao":  {"hp": 90,  "dano": 12, "vel": 0.9, "cor": (220, 180,  50)},
}


@dataclass
class Tropa:
    """Unidade de combate (atacante ou defensora)."""
    tipo:       str
    x:          float
    y:          float
    defende:    bool  = False
    hp:         float = 0.0
    hp_max:     float = 0.0
    dano:       float = 0.0
    velocidade: float = 1.5
    dest_x:     float = 0.0
    dest_y:     float = 0.0
    alvo_gx:    int   = -1
    alvo_gy:    int   = -1

    def __post_init__(self) -> None:
        stats = _TROPA_STATS.get(self.tipo, _TROPA_STATS["saqueador"])
        self.hp_max     = float(stats["hp"])
        self.hp         = self.hp_max
        self.dano       = float(stats["dano"])
        self.velocidade = float(stats["vel"]) * random.uniform(0.85, 1.15)
        self.dest_x     = self.x
        self.dest_y     = self.y

    @property
    def vivo(self) -> bool:
        return self.hp > 0

    @property
    def cor(self) -> tuple[int, int, int]:
        return _TROPA_STATS.get(self.tipo, _TROPA_STATS["saqueador"])["cor"]

    @property
    def pct_hp(self) -> float:
        return max(0.0, self.hp / self.hp_max)

    def sofrer_dano(self, dano: float) -> None:
        self.hp = max(0.0, self.hp - dano)

    def mover(self) -> None:
        import math
        dx, dy = self.dest_x - self.x, self.dest_y - self.y
        dist = math.hypot(dx, dy)
        if dist > self.velocidade:
            inv = self.velocidade / dist
            self.x += dx * inv
            self.y += dy * inv


@dataclass
class Vila:
    """Vila do jogador: construções vivas, recursos, defensores."""
    nome:     str
    dinheiro: float = 500.0
    nivel:    int   = 1

    # Recursos físicos
    madeira:  float = 50.0
    pedra:    float = 50.0

    # Construções rastreadas com HP
    construcoes_vivas: list[ConstrucaoViva] = field(default_factory=list)

    # Defensores permanentes
    defensores: list[Tropa] = field(default_factory=list)

    # Estado de invasão
    em_invasao:            bool  = False
    cooldown_invasao:      int   = 0
    ultima_invasao_resultado: dict | None = None

    def registrar_construcao(self, tipo: str, gx: int, gy: int, camada: str, nivel: int = 1) -> ConstrucaoViva:
        """Chamado pelo events.py quando o jogador constrói."""
        c = ConstrucaoViva(tipo=tipo, gx=gx, gy=gy, camada=camada, nivel=nivel)
        self.construcoes_vivas.append(c)
        return c

    def comprar_defensor(self, tipo: str, gx: int, gy: int) -> Tropa:
        """Cria um defensor permanente comprado pelo jogador."""
        from config import GRID_SIZE
        t = Tropa(tipo=tipo, x=float(gx*GRID_SIZE), y=float(gy*GRID_SIZE), defende=True)
        self.defensores.append(t)
        return t

    def get_construcao(self, gx: int, gy: int, camada: str) -> ConstrucaoViva | None:
        for c in self.construcoes_vivas:
            if c.gx == gx and c.gy == gy and c.camada == camada:
                return c
        return None

    def pode_reconstruir(self, c: ConstrucaoViva) -> bool:
        custo = c.custo_reconstrucao()
        return self.madeira >= custo["madeira"] and self.pedra >= custo["pedra"]

    def gastar_reconstrucao(self, c: ConstrucaoViva) -> bool:
        custo = c.custo_reconstrucao()
        if not self.pode_reconstruir(c):
            return False
        self.madeira -= custo["madeira"]
        self.pedra   -= custo["pedra"]
        return c.iniciar_reconstrucao()

    def tick_recursos(self) -> None:
        """Produz recursos passivamente. Chamar a cada frame."""
        for c in self.construcoes_vivas:
            if not c.destruida:
                prod = PRODUCAO_RECURSOS.get(c.tipo, {})
                self.madeira += prod.get("madeira", 0.0)
                self.pedra   += prod.get("pedra",   0.0)
        # Caps suaves
        self.madeira = min(self.madeira, 9999.0)
        self.pedra   = min(self.pedra,   9999.0)

    def atualizar(self) -> None:
        if self.cooldown_invasao > 0:
            self.cooldown_invasao -= 1
        for c in self.construcoes_vivas:
            c.atualizar()
        self.tick_recursos()

    def pode_ser_invadida(self) -> bool:
        return not self.em_invasao and self.cooldown_invasao <= 0

    def construcoes_intactas(self, camada: str = "superficie") -> list[ConstrucaoViva]:
        return [c for c in self.construcoes_vivas if c.camada == camada and not c.destruida]

    def gerar_rival(self) -> None:
        """Gera estado inicial de vila rival."""
        self.construcoes_vivas = []
        tipos = ["palacio", "cachoeira", "silo", "fazenda", "casa"]
        for tipo in tipos:
            qtd = random.randint(1, 3)
            for _ in range(qtd):
                gx = random.randint(5, 44)
                gy = random.randint(5, 44)
                self.construcoes_vivas.append(
                    ConstrucaoViva(tipo=tipo, gx=gx, gy=gy, camada="superficie")
                )
        self.dinheiro = 300.0 + self.nivel * 150
        self.madeira  = 80.0 + self.nivel * 20
        self.pedra    = 60.0 + self.nivel * 20
        # Defensores
        for _ in range(2 + self.nivel):
            tipo = random.choice(["defensor","guardiao"])
            gx = random.randint(5, 44)
            gy = random.randint(5, 44)
            from config import GRID_SIZE
            self.defensores.append(Tropa(tipo=tipo, x=float(gx*GRID_SIZE), y=float(gy*GRID_SIZE), defende=True))

    def resumo(self) -> tuple[str, int, float, int]:
        hp_total = sum(c.hp for c in self.construcoes_vivas)
        hp_max   = sum(c.hp_max for c in self.construcoes_vivas)
        return (self.nome, self.nivel, hp_total / max(hp_max, 1) * 100, int(self.dinheiro))
