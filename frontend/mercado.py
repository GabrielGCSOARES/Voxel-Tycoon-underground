"""mercado.py — Bolsa de valores autônoma entre as empresas."""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Final


# ── Dados estáticos ──────────────────────────────────────
@dataclass(frozen=True)
class Empresa:
    nome:         str
    cor:          tuple[int, int, int]
    cor_carrinho: tuple[int, int, int]


EMPRESAS: Final[tuple[Empresa, ...]] = (
    Empresa("AgroMax",   (220,  80,  80), (200,  60,  60)),
    Empresa("TechVerde", ( 80, 200, 100), ( 60, 180,  80)),
    Empresa("BlueMine",  ( 80, 130, 220), ( 60, 110, 200)),
    Empresa("GoldRush",  (220, 180,  50), (200, 160,  30)),
)

MAX_CARRINHOS: Final[int] = 6
CAMADAS: Final[tuple[str, ...]] = (
    "superficie", "caverna_1", "caverna_2", "caverna_3", "caverna_4"
)


# ── Utilitários ──────────────────────────────────────────
def formatar_preco(v: float) -> str:
    if v >= 1e12: return f"${v/1e12:.2f}T"
    if v >= 1e9:  return f"${v/1e9:.2f}B"
    if v >= 1e6:  return f"${v/1e6:.2f}M"
    if v >= 1e3:  return f"${v:,.0f}"
    return f"${v:.2f}"


def clamp(v: float, lo: float, hi: float) -> float:
    return lo if v < lo else hi if v > hi else v


# ── Mercado ──────────────────────────────────────────────
class MercadoGlobal:
    """
    Forças por tick: ruído base, pressão de share, drift individual,
    evento aleatório. Sem teto — crescimento ilimitado.
    """
    TICK_FRAMES:   Final[int]   = 480
    RUIDO_BASE:    Final[float] = 0.012
    VARIACAO_MAX:  Final[float] = 0.06
    PRECO_INICIAL: Final[float] = 10.0
    PRECO_MIN:     Final[float] = 0.01
    HIST_MAX:      Final[int]   = 40
    _EVENTOS:      Final       = (-0.06, -0.04, 0.05, 0.08)

    def __init__(self) -> None:
        self.precos    = {e.nome: self.PRECO_INICIAL for e in EMPRESAS}
        self.historico = {e.nome: [self.PRECO_INICIAL] for e in EMPRESAS}
        self.variacao  = {e.nome: 0.0 for e in EMPRESAS}
        self.lider     = EMPRESAS[0].nome
        self._timer    = 0
        self._drift    = {e.nome: random.uniform(-0.005, 0.005) for e in EMPRESAS}

    def atualizar(self, contagem: dict[str, int]) -> None:
        self._timer += 1
        if self._timer < self.TICK_FRAMES:
            return
        self._timer = 0
        total = max(1, sum(contagem.values()))

        for emp in EMPRESAS:
            nome  = emp.nome
            preco = self.precos[nome]
            share = contagem.get(nome, 0) / total
            ruido   = random.uniform(-self.RUIDO_BASE, self.RUIDO_BASE)
            pressao = self.VARIACAO_MAX * (0.5 - share)
            drift   = self._drift[nome]
            self._drift[nome] = clamp(drift + random.uniform(-0.001, 0.001), -0.01, 0.01)
            evento  = random.choice(self._EVENTOS) if random.random() < 0.02 else 0.0
            novo    = max(self.PRECO_MIN, preco * (1.0 + ruido + pressao + drift + evento))
            self.variacao[nome] = (novo - preco) / max(preco, 1e-9)
            self.precos[nome]   = round(novo, 2)
            hist = self.historico[nome]
            hist.append(novo)
            if len(hist) > self.HIST_MAX:
                hist.pop(0)

        self.lider = max(self.precos, key=self.precos.get)  # type: ignore

    def get_preco(self, nome: str) -> float:
        return self.precos.get(nome, self.PRECO_INICIAL)

    def get_variacao(self, nome: str) -> float:
        return self.variacao.get(nome, 0.0)


# Singleton global
mercado = MercadoGlobal()