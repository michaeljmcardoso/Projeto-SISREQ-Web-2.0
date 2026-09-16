"""
Módulo de notificação por email + detecção de alterações.
"""
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# =========================================================
# CONFIGURAÇÕES (lidas do .env)
# =========================================================
EMAIL_ENABLED      = os.getenv('EMAIL_ENABLED', 'False').lower() == 'true'
SMTP_SERVER        = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT          = int(os.getenv('SMTP_PORT', 587))
EMAIL_REMETENTE    = os.getenv('EMAIL_REMETENTE', '')
EMAIL_SENHA        = os.getenv('EMAIL_SENHA', '')
EMAIL_DESTINATARIO = os.getenv('EMAIL_DESTINATARIO', '')


# =========================================================
# MAPA DE CAMPOS DA TABELA PROCESSOS
# (usado para detectar alterações e renderizar email)
# =========================================================
MAPA_CAMPOS_PROCESSO = {
    'Numero':                    '📄 Nº Processo',
    'Data_Abertura':             '📅 Data de Abertura',
    'Comunidade':                '🏘️ Comunidade',
    'Municipio':                 '📍 Município',
    'Area_ha':                   '📐 Área Identificada (ha)',
    'Num_familias':              '👥 Nº de Famílias',
    'Fase_Processo':             '🔄 Fase do Processo',
    'Etapa_RTID':                '📊 Etapa RTID',
    'Edital_DOU':                '📰 Edital DOU',
    'Edital_DOE':                '📰 Edital DOE',
    'Portaria_DOU':              '📋 Portaria DOU',
    'Decreto_DOU':               '📋 Decreto DOU',
    'Area_ha_Titulada':          '📐 Área Titulada (ha)',
    'Titulo':                    '🏆 Título',
    'PNRA':                      '📚 PNRA',
    'Relatorio_Antropologico':   '👨‍🏫 Relatório Antropológico',
    'Latitude':                  '🌐 Latitude',
    'Longitude':                 '🌐 Longitude',
    'Certidao_FCP':              '📜 Certidão FCP',
    'Data_Certificacao':         '📅 Data de Certificação',
    'Sobreposicao':              '⚠️ Sobreposição',
    'Analise_de_Sobreposicao':   '🔍 Análise de Sobreposição',
    'Acao_Civil_Publica':        '⚖️ Ação Civil Pública',
    'Data_Decisao':              '📅 Data da Decisão',
    'Numero_Acao_Civil_Publica': '🔢 Nº Ação Civil Pública',
    'Outras_Informacoes':        '📝 Outras Informações',
}


# =========================================================
# COMPARAÇÃO DE CAMPOS
# =========================================================
def comparar_campos(antigo: dict, novo: dict, mapa: dict) -> list:
    """
    Retorna lista de dicts {campo, valor_antigo, valor_novo}
    para os campos que mudaram entre `antigo` e `novo`.
    """
    alteracoes = []

    def normaliza(v):
        if v is None:
            return ''
        if isinstance(v, (list, tuple)):
            return ", ".join(str(x) for x in v)
        return str(v).strip()

    for campo, label in mapa.items():
        va = normaliza(antigo.get(campo, ''))
        vn = normaliza(novo.get(campo, ''))
        if va != vn:
            alteracoes.append({
                'campo': label,
                'valor_antigo': va or '(vazio)',
                'valor_novo':   vn or '(vazio)'
            })
    return alteracoes


# =========================================================
# EMAIL GENÉRICO
# =========================================================
def enviar_email(assunto: str, html: str, destinatarios_extras=None):
    """
    Envia email HTML. Retorna (sucesso, [destinatarios_enviados]).
    """
    if not EMAIL_ENABLED:
        print("⚠️ EMAIL_ENABLED=False — email não enviado.")
        return False, []

    if not EMAIL_REMETENTE or not EMAIL_SENHA:
        print("⚠️ Credenciais SMTP incompletas.")
        return False, []

    destinatarios = []
    if EMAIL_DESTINATARIO:
        destinatarios.append(EMAIL_DESTINATARIO)
    if destinatarios_extras:
        for d in destinatarios_extras:
            if d and d not in destinatarios:
                destinatarios.append(d)

    if not destinatarios:
        return False, []

    enviados = []
    for dest in destinatarios:
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = assunto
            msg['From']    = EMAIL_REMETENTE
            msg['To']      = dest
            msg.attach(MIMEText(html, 'html'))

            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(EMAIL_REMETENTE, EMAIL_SENHA)
            server.send_message(msg)
            server.quit()
            enviados.append(dest)
            print(f"✅ Email enviado para {dest}")
        except Exception as e:
            print(f"❌ Erro ao enviar para {dest}: {e}")

    return len(enviados) > 0, enviados


# =========================================================
# TEMPLATES HTML
# =========================================================
def _montar_email_base(titulo: str, subtitulo: str, corpo_html: str,
                        cor_primaria: str = "#1f77b4") -> str:
    return f"""
    <!DOCTYPE html><html><head><meta charset="utf-8"><style>
        body {{ font-family: Arial, sans-serif; background:#f4f4f4; padding:20px; }}
        .container {{ max-width:680px; margin:auto; background:#fff;
                     border-radius:10px; padding:30px;
                     box-shadow:0 2px 10px rgba(0,0,0,.1); }}
        .header {{ background:{cor_primaria}; color:#fff; padding:20px;
                  border-radius:8px; text-align:center; margin-bottom:20px; }}
        .header h1 {{ margin:0; color:#FFD700; }}
        .header p  {{ margin:5px 0 0 0; color:#e0e0e0; }}
        .info-row {{ display:flex; justify-content:space-between;
                    padding:8px 0; border-bottom:1px solid #eee; }}
        .info-label {{ font-weight:bold; color:#555; }}
        .info-value {{ color:#333; text-align:right; }}
        .footer {{ margin-top:30px; text-align:center; color:#999;
                  font-size:12px; border-top:1px solid #eee; padding-top:20px; }}
        table {{ width:100%; border-collapse:collapse; margin:15px 0; font-size:14px; }}
        th {{ background:{cor_primaria}; color:#fff; padding:10px; text-align:left; }}
        td {{ padding:8px; border:1px solid #ddd; vertical-align:top; }}
        .badge {{ background:#FFD700; color:{cor_primaria};
                 padding:5px 15px; border-radius:20px;
                 font-weight:bold; display:inline-block; }}
    </style></head><body>
        <div class="container">
            <div class="header">
                <h1>{titulo}</h1>
                <p>{subtitulo}</p>
            </div>
            {corpo_html}
            <div class="footer">
                <p>📧 Email automático gerado pelo <strong>SISREQ</strong>.</p>
                <p>© {datetime.now().year} - Sistema de Regularização Quilombola.</p>
            </div>
        </div>
    </body></html>
    """


def _linhas_dados(dados: dict, mapa: dict) -> str:
    """Gera as linhas '<label> | <valor>' em HTML."""
    linhas = ""
    for campo, label in mapa.items():
        valor = dados.get(campo, '') or '(vazio)'
        linhas += f"""
        <div class="info-row">
            <span class="info-label">{label}:</span>
            <span class="info-value">{valor}</span>
        </div>
        """
    return linhas


def _tabela_alteracoes(alteracoes: list) -> str:
    if not alteracoes:
        return "<p>Nenhuma alteração significativa detectada.</p>"
    linhas = "".join(f"""
        <tr>
            <td style="font-weight:bold;">{a['campo']}</td>
            <td style="background:#f8d7da;color:#721c24;">
                <del>{a['valor_antigo']}</del>
            </td>
            <td style="background:#d4edda;color:#155724;">
                <strong>{a['valor_novo']}</strong>
            </td>
        </tr>
    """ for a in alteracoes)
    return f"""
    <h3>📝 Alterações Realizadas ({len(alteracoes)})</h3>
    <table>
        <thead><tr><th>Campo</th><th>Antes</th><th>Depois</th></tr></thead>
        <tbody>{linhas}</tbody>
    </table>
    """


# =========================================================
# NOTIFICAÇÕES DE ALTO NÍVEL
# =========================================================
def notificar_cadastro(dados: dict) -> tuple:
    """Retorna (assunto, html) para um NOVO processo."""
    comunidade = dados.get('Comunidade', 'N/D')
    assunto = f"✅ Novo Processo Cadastrado — {comunidade}"

    corpo = f"""
        <div style="background:#E8F5E9; padding:15px; border-radius:8px;
                    border-left:6px solid #2E7D32; margin-bottom:20px;">
            <h2 style="margin:0; color:#2E7D32;">✅ Novo Processo Registrado</h2>
        </div>
        <h3>📋 Dados do Processo</h3>
        {_linhas_dados(dados, MAPA_CAMPOS_PROCESSO)}
        <p style="margin-top:20px; color:#666; font-size:13px;">
            🕐 Cadastrado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        </p>
    """
    html = _montar_email_base(
        titulo="🏘️ SISREQ",
        subtitulo="Sistema de Regularização Quilombola",
        corpo_html=corpo,
        cor_primaria="#1f77b4"
    )
    return assunto, html


def notificar_alteracao(dados_novos: dict, dados_antigos: dict) -> tuple:
    """Retorna (assunto, html) para uma EDIÇÃO com diff."""
    comunidade = dados_novos.get('Comunidade', 'N/D')
    alteracoes = comparar_campos(dados_antigos or {}, dados_novos, MAPA_CAMPOS_PROCESSO)

    assunto = f"✏️ Processo ALTERADO — {comunidade} ({len(alteracoes)} mudanças)"

    corpo = f"""
        <div style="background:#FFF8E1; padding:15px; border-radius:8px;
                    border-left:6px solid #FFA000; margin-bottom:20px;">
            <h2 style="margin:0; color:#E65100;">✏️ Processo Alterado</h2>
            <p style="margin:10px 0 0 0;">
                <span class="badge">{len(alteracoes)} alterações</span>
            </p>
        </div>

        {_tabela_alteracoes(alteracoes)}

        <h3>📋 Estado Atual do Processo</h3>
        {_linhas_dados(dados_novos, MAPA_CAMPOS_PROCESSO)}
        <p style="margin-top:20px; color:#666; font-size:13px;">
            🕐 Alterado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        </p>
    """
    html = _montar_email_base(
        titulo="🏘️ SISREQ",
        subtitulo="Sistema de Regularização Quilombola",
        corpo_html=corpo,
        cor_primaria="#1a237e"
    )
    return assunto, html