"""
Módulo de métricas de acesso — registra logins silenciosamente.
O usuário NUNCA vê nada disso.
"""
import os
import sqlite3
import getpass
import platform
from datetime import datetime
from dotenv import load_dotenv

from core_notificacao import enviar_email, _montar_email_base

load_dotenv()

DB_PATH = os.getenv('DB_PATH', 'sisreq.db')


# =========================================================
# 1. TABELA DE LOGS (criada automaticamente se não existir)
# =========================================================
def _garantir_tabela_logs():
    """Cria a tabela logs_acesso se não existir."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs_acesso (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT NOT NULL,
                data_hora TEXT NOT NULL,
                data TEXT NOT NULL,
                hora TEXT NOT NULL,
                dia_semana TEXT,
                ip_local TEXT,
                hostname TEXT,
                sistema TEXT,
                user_agent TEXT,
                origem TEXT DEFAULT 'web'
            )
        ''')
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"⚠️ [logs] Erro ao criar tabela: {e}")
        return False


# =========================================================
# 2. COLETA DE METADADOS DO AMBIENTE
# =========================================================
def _coletar_metadados():
    """Coleta informações do ambiente de execução (para contexto)."""
    meta = {
        'hostname': 'desconhecido',
        'sistema':  'desconhecido',
        'ip_local': 'desconhecido',
    }
    try:
        meta['hostname'] = platform.node() or 'desconhecido'
        meta['sistema']  = f"{platform.system()} {platform.release()}"
    except Exception:
        pass

    try:
        import socket
        # IP local da máquina (não o público)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        meta['ip_local'] = s.getsockname()[0]
        s.close()
    except Exception:
        pass

    return meta


# =========================================================
# 3. GRAVAR NO BANCO (silencioso)
# =========================================================
def _gravar_log(usuario: str, meta: dict) -> bool:
    try:
        _garantir_tabela_logs()
        agora = datetime.now()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO logs_acesso
            (usuario, data_hora, data, hora, dia_semana,
             ip_local, hostname, sistema, origem)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            usuario,
            agora.strftime('%d/%m/%Y %H:%M:%S'),
            agora.strftime('%d/%m/%Y'),
            agora.strftime('%H:%M:%S'),
            agora.strftime('%A'),
            meta.get('ip_local', ''),
            meta.get('hostname', ''),
            meta.get('sistema', ''),
            'web'
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"⚠️ [logs] Erro ao gravar: {e}")
        return False


# =========================================================
# 4. MONTAR EMAIL DE NOTIFICAÇÃO DE ACESSO
# =========================================================
def _montar_email_acesso(usuario: str, meta: dict) -> tuple:
    agora = datetime.now()
    assunto = f"🔐 Acesso registrado — {usuario}"

    dias = {
        'Monday': 'Segunda-feira', 'Tuesday': 'Terça-feira',
        'Wednesday': 'Quarta-feira', 'Thursday': 'Quinta-feira',
        'Friday': 'Sexta-feira', 'Saturday': 'Sábado',
        'Sunday': 'Domingo',
    }
    dia_semana = dias.get(agora.strftime('%A'), agora.strftime('%A'))

    corpo = f"""
        <div style="background:#E8EAF6; padding:15px; border-radius:8px;
                    border-left:6px solid #3949AB; margin-bottom:20px;">
            <h2 style="margin:0; color:#1A237E;">🔐 Novo Acesso ao SISREQ</h2>
            <p style="margin:8px 0 0 0; color:#555;">
                Um login foi realizado no sistema.
            </p>
        </div>

        <h3>📋 Detalhes do Acesso</h3>

        <div class="info-row">
            <span class="info-label">👤 Usuário:</span>
            <span class="info-value"><strong>{usuario}</strong></span>
        </div>
        <div class="info-row">
            <span class="info-label">📅 Data:</span>
            <span class="info-value">{agora.strftime('%d/%m/%Y')}</span>
        </div>
        <div class="info-row">
            <span class="info-label">🕐 Hora:</span>
            <span class="info-value">{agora.strftime('%H:%M:%S')}</span>
        </div>
        <div class="info-row">
            <span class="info-label">📆 Dia da semana:</span>
            <span class="info-value">{dia_semana}</span>
        </div>
        <div class="info-row">
            <span class="info-label">🖥️ Hostname:</span>
            <span class="info-value">{meta.get('hostname', 'N/D')}</span>
        </div>
        <div class="info-row">
            <span class="info-label">💻 Sistema:</span>
            <span class="info-value">{meta.get('sistema', 'N/D')}</span>
        </div>
        <div class="info-row">
            <span class="info-label">🌐 IP local:</span>
            <span class="info-value">{meta.get('ip_local', 'N/D')}</span>
        </div>

        <p style="margin-top:20px; padding:12px; background:#FFF8E1;
                  border-left:4px solid #FFA000; border-radius:4px;
                  color:#856404; font-size:13px;">
            ℹ️ Este é um registro automático para fins de métricas de acesso.
            Se este acesso não foi autorizado, verifique imediatamente.
        </p>
    """

    html = _montar_email_base(
        titulo="🏘️ SISREQ",
        subtitulo="Registro de Acesso",
        corpo_html=corpo,
        cor_primaria="#3949AB"
    )
    return assunto, html


# =========================================================
# 5. FUNÇÃO PRINCIPAL — chamada APÓS o login bem-sucedido
# =========================================================
def registrar_acesso(usuario: str):
    """
    Registra um acesso de forma TOTALMENTE silenciosa.

    Executa 3 tarefas independentes:
       1) Grava no banco local (tabela logs_acesso)
       2) Envia email para o admin
       3) Sincroniza com GitHub (opcional)

    Nenhuma falha é propagada — tudo é engolido com print().
    """
    if not usuario:
        return

    try:
        meta = _coletar_metadados()

        # 1️⃣ BANCO LOCAL
        try:
            _gravar_log(usuario, meta)
        except Exception as e:
            print(f"⚠️ [acesso] Erro ao gravar log: {e}")

        # 2️⃣ EMAIL
        try:
            assunto, html = _montar_email_acesso(usuario, meta)
            enviado, _ = enviar_email(assunto, html)
            if not enviado:
                print(f"⚠️ [acesso] Email não pôde ser enviado para {usuario}")
        except Exception as e:
            print(f"⚠️ [acesso] Erro no email: {e}")

        # 3️⃣ GITHUB (opcional — descomente se quiser backup dos logs)
        try:
            from core_sync import sincronizar_github
            sincronizar_github("login", {'usuario': usuario})
        except Exception as e:
            print(f"⚠️ [acesso] Erro no GitHub: {e}")

    except Exception as e:
        # Blindagem total — NADA pode quebrar o app por causa de métricas
        print(f"⚠️ [acesso] Erro inesperado: {e}")