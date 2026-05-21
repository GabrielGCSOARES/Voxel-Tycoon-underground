"""
quests.py — Sistema de missões progressivas com recompensas.

Missões são verificadas passivamente a cada frame.
Cada quest tem: descricao, condicao (lambda), recompensa (dinheiro, xp, recursos).
"""
from __future__ import annotations
import random
from dataclasses import dataclass, field
from typing import Callable, Any

@dataclass
class Quest:
    id:          str
    titulo:      str
    descricao:   str
    # Recompensas
    recompensa_dinheiro: float = 0.0
    recompensa_xp:       int   = 0
    recompensa_madeira:  float = 0.0
    recompensa_pedra:    float = 0.0
    nivel_req: int = 1
    # Estado
    concluida:   bool = False
    notificada:  bool = False   # já mostrou a mensagem de conclusão
    # Progresso numérico (ex: "construa 3 casas")
    progresso:   int  = 0
    meta:        int  = 1

    @property
    def pct(self) -> float:
        return min(1.0, self.progresso / max(self.meta, 1))


# ── Definição estática de todas as quests ────────────────
TODAS_AS_QUESTS: list[dict] = [
    # ── Construção básica ────────────────────────────────
    {
        "id": "primeira_casa",
        "titulo": "Primeiros Passos",
        "descricao": "Construa 1 casa",
        "meta": 1,
        "recompensa_dinheiro": 1_000,
        "recompensa_xp": 50,
    },
    {
        "id": "tres_fazendas",
        "titulo": "Agricultor",
        "descricao": "Construa 3 fazendas",
        "meta": 3,
        "recompensa_dinheiro": 2_000,
        "recompensa_xp": 100,
        "recompensa_madeira": 50,
    },
    {
        "id": "primeiro_palacio",
        "titulo": "Nobreza",
        "descricao": "Construa 1 palacio",
        "meta": 1,
        "recompensa_dinheiro": 5_000,
        "recompensa_xp": 300,
    },
    {
        "id": "cinco_construcoes",
        "titulo": "Vila Emergente",
        "descricao": "Tenha 5 construcoes na superficie",
        "meta": 5,
        "recompensa_dinheiro": 3_000,
        "recompensa_xp": 200,
        "recompensa_madeira": 80,
        "recompensa_pedra": 40,
    },
    # ── Caverna ──────────────────────────────────────────
    {
        "id": "primeira_mineracao",
        "titulo": "Mineiro",
        "descricao": "Construa 1 mineracao na caverna",
        "meta": 1,
        "recompensa_dinheiro": 4_000,
        "recompensa_xp": 200,
        "recompensa_pedra": 100,
    },
    {
        "id": "tres_cavernosos",
        "titulo": "Explorador das Profundezas",
        "descricao": "Tenha 3 construcoes na caverna",
        "meta": 3,
        "recompensa_dinheiro": 8_000,
        "recompensa_xp": 400,
        "recompensa_pedra": 150,
    },
    # ── Recursos ─────────────────────────────────────────
    {
        "id": "madeira_100",
        "titulo": "Lenhador",
        "descricao": "Acumule 100 unidades de madeira",
        "meta": 100,
        "recompensa_dinheiro": 2_500,
        "recompensa_xp": 150,
    },
    {
        "id": "pedra_100",
        "titulo": "Pedreiro",
        "descricao": "Acumule 100 unidades de pedra",
        "meta": 100,
        "recompensa_dinheiro": 2_500,
        "recompensa_xp": 150,
    },
    # ── Batalha ──────────────────────────────────────────
    {
        "id": "primeira_defesa",
        "titulo": "Resistencia",
        "descricao": "Sobreviva a 1 invasao NPC",
        "meta": 1,
        "recompensa_dinheiro": 6_000,
        "recompensa_xp": 500,
        "recompensa_madeira": 60,
        "recompensa_pedra": 60,
    },
    {
        "id": "reconstruir_1",
        "titulo": "Fênix",
        "descricao": "Reconstrua 1 construcao destruida",
        "meta": 1,
        "recompensa_dinheiro": 3_000,
        "recompensa_xp": 250,
    },
    {
        "id": "derrotar_invasao",
        "titulo": "Guerreiro",
        "descricao": "Repila 3 invasoes NPC",
        "meta": 3,
        "recompensa_dinheiro": 15_000,
        "recompensa_xp": 1_000,
        "recompensa_madeira": 100,
        "recompensa_pedra": 100,
    },
    # ── Economia ─────────────────────────────────────────
    {
        "id": "dinheiro_10k",
        "titulo": "Comerciante",
        "descricao": "Acumule $10,000",
        "meta": 10_000,
        "recompensa_xp": 300,
        "recompensa_madeira": 120,
    },
    {
        "id": "nivel_5",
        "titulo": "Veterano",
        "descricao": "Alcance o nivel 5",
        "meta": 5,
        "recompensa_dinheiro": 10_000,
        "recompensa_xp": 800,
    },
    {
        "id": "nivel_10",
        "titulo": "Mestre",
        "descricao": "Alcance o nivel 10",
        "meta": 10,
        "recompensa_dinheiro": 50_000,
        "recompensa_xp": 3_000,
        "recompensa_madeira": 200,
        "recompensa_pedra": 200,
    },
    {
        "id": "construcoes_10",
        "titulo": "Cidade Ativa",
        "descricao": "Tenha 10 construcoes no total",
        "meta": 10,
        "recompensa_dinheiro": 12_000,
        "recompensa_xp": 900,
        "recompensa_madeira": 120,
        "recompensa_pedra": 120,
    },
]


class GerenciadorQuests:
    """
    Rastreia progresso de quests e distribui recompensas.
    Integração: chamar tick() a cada frame com o EstadoJogo.
    """

    def __init__(self) -> None:
        nivel_por_quest = {
            "primeira_casa": 1,
            "tres_fazendas": 1,
            "madeira_100": 1,
            "cinco_construcoes": 2,
            "pedra_100": 2,
            "dinheiro_10k": 2,
            "primeiro_palacio": 3,
            "primeira_defesa": 3,
            "reconstruir_1": 3,
            "primeira_mineracao": 4,
            "tres_cavernosos": 4,
            "derrotar_invasao": 4,
            "nivel_5": 5,
            "construcoes_10": 5,
            "nivel_10": 5,
        }
        quests = []
        for i, q in enumerate(TODAS_AS_QUESTS):
            dados = dict(q)
            dados.setdefault("nivel_req", nivel_por_quest.get(dados["id"], i // 3 + 1))
            quests.append(Quest(**dados))
        self.quests: list[Quest] = quests
        self._nivel_atual = 1
        self._contadores: dict[str, int] = {
            "casa": 0, "fazenda": 0, "palacio": 0,
            "mineracao": 0, "total_sup": 0, "total_cav": 0,
            "invasoes_repelidas": 0, "reconstrucoes": 0,
        }
        # Fila de notificações pendentes: (titulo, recompensa_str)
        self.notificacoes: list[tuple[str, str]] = []

    # ── Eventos disparados pelo resto do jogo ────────────
    def on_construir(self, tipo: str, camada: str) -> None:
        self._contadores[tipo] = self._contadores.get(tipo, 0) + 1
        if camada == "superficie":
            self._contadores["total_sup"] += 1
        else:
            self._contadores["total_cav"] += 1

    def on_invasao_repelida(self) -> None:
        self._contadores["invasoes_repelidas"] += 1

    def on_reconstrucao(self) -> None:
        self._contadores["reconstrucoes"] += 1

    # ── Tick principal ────────────────────────────────────
    def tick(self, estado) -> None:
        """Chama a cada frame com o EstadoJogo."""
        self._nivel_atual = estado.nivel
        self._atualizar_progresso(estado)
        self._verificar_conclusoes(estado)

    def _atualizar_progresso(self, estado) -> None:
        vila = estado.vila_jogador
        cnt  = self._contadores

        _mapa = {
            "primeira_casa":      cnt.get("casa", 0),
            "tres_fazendas":      cnt.get("fazenda", 0),
            "primeiro_palacio":   cnt.get("palacio", 0),
            "cinco_construcoes":  cnt.get("total_sup", 0),
            "primeira_mineracao": cnt.get("mineracao", 0),
            "tres_cavernosos":    cnt.get("total_cav", 0),
            "construcoes_10":      cnt.get("total_sup", 0) + cnt.get("total_cav", 0),
            "madeira_100":        int(vila.madeira),
            "pedra_100":          int(vila.pedra),
            "primeira_defesa":    cnt.get("invasoes_repelidas", 0),
            "reconstruir_1":      cnt.get("reconstrucoes", 0),
            "derrotar_invasao":   cnt.get("invasoes_repelidas", 0),
            "dinheiro_10k":       int(estado.dinheiro),
            "nivel_5":            estado.nivel,
            "nivel_10":           estado.nivel,
        }
        for q in self.quests:
            if not q.concluida:
                q.progresso = _mapa.get(q.id, 0)

    def _verificar_conclusoes(self, estado) -> None:
        vila = estado.vila_jogador
        for q in self.quests:
            if q.concluida or q.notificada:
                continue
            if q.progresso >= q.meta:
                q.concluida  = True
                q.notificada = True
                # Distribui recompensas
                estado.dinheiro    += q.recompensa_dinheiro
                estado.ganhar_xp(q.recompensa_xp)
                vila.madeira       += q.recompensa_madeira
                vila.pedra         += q.recompensa_pedra
                # Enfileira notificação
                partes = []
                if q.recompensa_dinheiro:
                    partes.append(f"${q.recompensa_dinheiro:,.0f}")
                if q.recompensa_xp:
                    partes.append(f"{q.recompensa_xp} XP")
                if q.recompensa_madeira:
                    partes.append(f"{q.recompensa_madeira:.0f} madeira")
                if q.recompensa_pedra:
                    partes.append(f"{q.recompensa_pedra:.0f} pedra")
                self.notificacoes.append((q.titulo, " + ".join(partes)))

    def quests_ativas(self) -> list[Quest]:
        ativas = [
            q for q in self.quests
            if not q.concluida and q.nivel_req <= self._nivel_atual
        ]
        return ativas[:3]

    def quests_concluidas(self) -> list[Quest]:
        return [q for q in self.quests if q.concluida]

    def pop_notificacao(self) -> tuple[str,str] | None:
        return self.notificacoes.pop(0) if self.notificacoes else None
