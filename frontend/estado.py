"""estado.py — Contêiner mutável com todo o estado em tempo de execução."""
from __future__ import annotations

_MSG_DURACAO = 120  # frames


class EstadoJogo:
    __slots__ = (
        "estado", "dinheiro", "populacao", "nivel", "xp", "xp_max",
        "renda_passiva", "selected_index", "arrastando",
        "drag_start", "drag_offset_start",
        "construcao_selecionada", "mensagem_tela", "tempo_mensagem",
    )

    def __init__(self) -> None:
        self.estado               = "menu"
        self.dinheiro             = 500.0
        self.populacao            = 0
        self.nivel                = 1
        self.xp                   = 0
        self.xp_max               = 100
        self.renda_passiva        = 0.0
        self.selected_index       = 0
        self.arrastando           = False
        self.drag_start           = (0, 0)
        self.drag_offset_start    = (0, 0)
        self.construcao_selecionada: tuple | None = None
        self.mensagem_tela        = ""
        self.tempo_mensagem       = 0

    def exibir_mensagem(self, texto: str) -> None:
        self.mensagem_tela  = texto
        self.tempo_mensagem = _MSG_DURACAO

    def ganhar_xp(self, qtd: int) -> None:
        self.xp += qtd
        while self.xp >= self.xp_max:
            self.xp    -= self.xp_max
            self.nivel += 1
            self.xp_max = int(self.xp_max * 1.5)