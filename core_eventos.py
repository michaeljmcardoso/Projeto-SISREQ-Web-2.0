"""Entrega notificações e sincronizações para alterações do banco."""
from core_notificacao import enviar_email, notificar_mudanca_banco
from core_sync import sincronizar_github


def reportar_mudanca_banco(
    evento: str, tipo: str, dados: dict
) -> list[tuple[str, str]]:
    """Retorna mensagens de status para exibição na interface."""
    mensagens = []

    try:
        assunto, html = notificar_mudanca_banco(evento, dados)
        enviado, destinatarios = enviar_email(assunto, html)
        if enviado:
            mensagens.append((
                'info',
                f"Email enviado para: {', '.join(destinatarios)}",
            ))
        else:
            mensagens.append(('warning', 'O email não pôde ser enviado.'))
    except Exception as erro:
        mensagens.append(('warning', f'Erro ao enviar email: {erro}'))

    try:
        resultado = sincronizar_github(tipo, dados)
        if resultado.get('success'):
            mensagens.append(('success', resultado.get('message', 'GitHub sincronizado.')))
        else:
            mensagens.append((
                'warning',
                f"Falha na sincronização com GitHub: {resultado.get('error', '')}",
            ))
    except Exception as erro:
        mensagens.append(('warning', f'Erro na sincronização com GitHub: {erro}'))

    return mensagens
