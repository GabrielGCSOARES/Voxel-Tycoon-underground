"""batalha.py — Sistema de combate, invasão e resolução de batalhas."""
from __future__ import annotations

import random
from vila import Tropa, Invasao, Vila


class GerenciadorBatalha:
    """Gerencia invasões e combates entre vilas."""

    __slots__ = (
        "_invasoes_ativas",
        "_historico_ataques",
    )

    def __init__(self) -> None:
        self._invasoes_ativas: dict[str, Invasao] = {}
        self._historico_ataques: list[dict] = []

    def iniciar_invasao(
        self,
        vila_alvo: Vila,
        atacante_nome: str,
        nivel_ataque: int,
    ) -> Invasao:
        """Inicia uma invasão na vila."""
        if not vila_alvo.pode_ser_invadida():
            raise ValueError("Vila ainda está em cooldown")

        tropas = self._gerar_tropas_ataque(nivel_ataque)
        invasao = Invasao(atacante_nome, tropas)
        vila_alvo.invasao_ativa = invasao
        vila_alvo.tempo_proxima_invasao = 600  # 10 segundos de cooldown

        return invasao

    def _gerar_tropas_ataque(self, nivel: int) -> list[Tropa]:
        """Gera tropas baseado no nível de ataque."""
        tropas = []
        quantidade = 3 + nivel
        for _ in range(quantidade):
            tipo = random.choice(["soldado", "cavaleiro", "arqueiro"])
            tropas.append(Tropa(tipo, x=0.0, y=0.0, defende=False))
        return tropas

    def processar_invasao(self, vila: Vila) -> dict | None:
        """Processa uma invasão em andamento."""
        if not vila.invasao_ativa:
            return None

        invasao = vila.invasao_ativa
        invasao.atualizar()

        # Simular combate simplificado
        for tropa in invasao.tropas_atacantes:
            if tropa.saude > 0:
                dano_recebido = random.uniform(0.5, 2.0)
                tropa.sofrer_dano(dano_recebido)

        # Destruir construções se tropas estão na vila
        if len([t for t in invasao.tropas_atacantes if t.saude > 0]) > 0:
            invasao.dano_total += random.uniform(5.0, 15.0)
            if invasao.dano_total > 50:
                invasao.construcoes_destruidas += 1
                invasao.dano_total = 0

        vila.sofrer_dano(invasao.dano_total * 0.01)

        # Verificar fim da invasão
        if invasao.acabou():
            resultado = invasao.resultado()
            self._historico_ataques.append(resultado)
            vila.invasao_ativa = None
            return resultado

        return None

    def finalizador_invasao(self, vila_atacada: Vila, vila_atacante: Vila) -> dict:
        """Finaliza uma invasão e distribui recompensas."""
        if not vila_atacada.invasao_ativa:
            return {"erro": "Sem invasão ativa"}

        resultado = vila_atacada.invasao_ativa.resultado()

        if resultado["vitoria"]:
            # Atacante vence: rouba dinheiro
            roubo = vila_atacada.obter_valor_roubavel()
            vila_atacada.dinheiro -= roubo
            vila_atacante.dinheiro += roubo
            resultado["dinheiro_roubado"] = roubo
        else:
            # Defensor vence: ganha defesa de recursos
            resultado["dinheiro_ganho"] = 50 * (4 - resultado["tropas_vivas"])

        vila_atacada.invasao_ativa = None
        return resultado

    def obter_invasoes_ativas(self) -> list[Invasao]:
        """Retorna todas as invasões ativas."""
        return list(self._invasoes_ativas.values())

    def obter_historico(self, limite: int = 10) -> list[dict]:
        """Retorna histórico de ataques."""
        return self._historico_ataques[-limite:]


# Singleton global
gerenciador_batalha = GerenciadorBatalha()
