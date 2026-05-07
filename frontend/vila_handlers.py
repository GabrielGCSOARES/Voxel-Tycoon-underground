
def _handle_modal_vila(pos: tuple, estado, interface_ui) -> None:
    """Handle cliques no modal de vila."""
    botoes = interface_ui.modal_vila_botoes
    if not botoes:
        return
    if botoes["fechar"].collidepoint(pos):
        interface_vila.mostrando_vila = False
        if CLICK_SOUND: CLICK_SOUND.play()
        return
    if botoes["atacar"].collidepoint(pos):
        estado.modo_ataque = True
        interface_vila.mostrando_ataque = True
        if CLICK_SOUND: CLICK_SOUND.play()


def _handle_ataque(pos: tuple, estado, interface_ui) -> None:
    """Handle cliques no modal de ataque."""
    botoes = interface_ui.modal_ataque_botoes
    if not botoes:
        return
    if botoes["cancelar"].collidepoint(pos):
        estado.modo_ataque = False
        interface_vila.mostrando_ataque = False
        if CLICK_SOUND: CLICK_SOUND.play()
        return
    if botoes["atacar"].collidepoint(pos):
        # Inicia invasão
        try:
            gerenciador_batalha.iniciar_invasao(
                estado.vila_rival,
                estado.vila_jogador.nome,
                estado.nivel,
            )
            estado.modo_ataque = False
            interface_vila.mostrando_ataque = False
            estado.exibir_mensagem("Ataque iniciado! Destrua as defesas do rival!")
            if CLICK_SOUND: CLICK_SOUND.play()
        except ValueError as e:
            estado.exibir_mensagem(str(e))
            if CLICK_SOUND: CLICK_SOUND.play()
