"""
Módulo central de tratamento de data/hora.
Garante que todos os timestamps usem o fuso configurado (America/Sao_Paulo).
"""
import os
from datetime import datetime

try:
    from zoneinfo import ZoneInfo   # Python 3.9+
    ZONEINFO_DISPONIVEL = True
except ImportError:
    ZONEINFO_DISPONIVEL = False
    try:
        from backports.zoneinfo import ZoneInfo  # Python 3.8
    except ImportError:
        ZONEINFO_DISPONIVEL = False

# Fuso padrão — configurável via .env / secrets
TIMEZONE_NAME = os.getenv('TIMEZONE', 'America/Sao_Paulo')

# Cache do objeto de fuso
_tz = None
if ZONEINFO_DISPONIVEL:
    try:
        _tz = ZoneInfo(TIMEZONE_NAME)
    except Exception as e:
        print(f"⚠️ [time] Fuso '{TIMEZONE_NAME}' inválido: {e}. Usando UTC-3 fixo.")
        _tz = None


def agora() -> datetime:
    """
    Retorna o datetime ATUAL no fuso configurado.

    Se zoneinfo estiver disponível → usa America/Sao_Paulo (com DST/regras corretas)
    Se não estiver → usa UTC-3 fixo (fallback seguro para o Brasil)
    """
    if _tz is not None:
        return datetime.now(_tz)

    # Fallback: UTC-3 fixo
    from datetime import timezone, timedelta
    return datetime.now(timezone(timedelta(hours=-3)))


def agora_str(formato: str = '%d/%m/%Y %H:%M:%S') -> str:
    """Retorna a hora atual formatada como string."""
    return agora().strftime(formato)


def timezone_nome() -> str:
    """Retorna o nome do fuso atualmente em uso (para debug)."""
    if _tz is not None:
        return TIMEZONE_NAME
    return "UTC-3 (fallback)"