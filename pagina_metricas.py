"""
Página de Métricas de Acesso do SISREQ.
Acesso restrito ao usuário 'admin'.

Fonte de dados (busca em ordem de prioridade):
  1. sisreq.db         (raiz — desenvolvimento local)
  2. dados/sisreq.db   (versionado — Streamlit Cloud)
"""
import os
import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta


# =========================================================
# LOCALIZAÇÃO DO BANCO
# =========================================================
def _encontrar_db():
    """Retorna o caminho do banco de dados disponível."""
    candidatos = [
        'sisreq.db',              # local (raiz do projeto)
        'dados/sisreq.db',        # versionado no Git (Cloud)
        os.path.join(os.path.dirname(__file__), 'sisreq.db'),
        os.path.join(os.path.dirname(__file__), 'dados', 'sisreq.db'),
    ]
    for p in candidatos:
        if os.path.exists(p):
            return p
    return None


def _carregar_logs(db_path):
    """Lê todos os logs de acesso em um DataFrame."""
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("""
            SELECT id, usuario, data_hora, data, hora, dia_semana,
                   ip_local, hostname, sistema, origem
            FROM logs_acesso
            ORDER BY id DESC
        """, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"❌ Erro ao ler logs: {e}")
        return pd.DataFrame()


def _carregar_usuarios(db_path):
    """Lê a lista de usuários cadastrados."""
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(
            "SELECT id, usuario FROM usuarios ORDER BY id", conn
        )
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()


def _carregar_processos_count(db_path):
    """Conta o total de processos cadastrados."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM processos")
        n = cursor.fetchone()[0]
        conn.close()
        return n
    except Exception:
        return 0


# =========================================================
# PÁGINA PRINCIPAL
# =========================================================
def pagina_metricas():
    st.markdown("### 📊 Métricas de Acesso")
    st.caption("Acompanhe quem está usando o SISREQ e quando.")

    # ─── Localizar banco ───
    db_path = _encontrar_db()
    if not db_path:
        st.error("❌ Banco de dados não encontrado. "
                 "Verifique se `sisreq.db` ou `dados/sisreq.db` existem.")
        return

    # ─── Info de debug (pequeno rodapé) ───
    with st.expander("ℹ️ Informações técnicas", expanded=False):
        st.code(f"""
📁 Fonte de dados: {db_path}
📅 Consulta em:    {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
📦 Tamanho:        {os.path.getsize(db_path) / 1024:.1f} KB
        """)

    # ─── Carregar dados ───
    df_logs = _carregar_logs(db_path)
    df_users = _carregar_usuarios(db_path)
    n_processos = _carregar_processos_count(db_path)

    if df_logs.empty:
        st.warning("⚠️ Nenhum registro de acesso encontrado ainda.")
        st.info("💡 Os dados aparecerão aqui conforme os usuários fizerem login.")
        return

    # ─── Converter datas ───
    df_logs['data_dt'] = pd.to_datetime(
        df_logs['data'], format='%d/%m/%Y', errors='coerce'
    )

    # ═════════════════════════════════════════════
    # FILTRO DE PERÍODO
    # ═════════════════════════════════════════════
    st.markdown("#### 🗓️ Filtro de Período")
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        periodo = st.selectbox(
            "Atalhos",
            ["Últimos 7 dias", "Últimos 30 dias", "Últimos 90 dias",
             "Todo o período", "Personalizado"],
            index=1,
            key="metricas_periodo"
        )

    data_min = df_logs['data_dt'].min()
    data_max = df_logs['data_dt'].max()
    hoje = datetime.now().date()

    if periodo == "Últimos 7 dias":
        inicio, fim = hoje - timedelta(days=7), hoje
    elif periodo == "Últimos 30 dias":
        inicio, fim = hoje - timedelta(days=30), hoje
    elif periodo == "Últimos 90 dias":
        inicio, fim = hoje - timedelta(days=90), hoje
    elif periodo == "Todo o período":
        inicio = data_min.date() if pd.notna(data_min) else hoje - timedelta(days=365)
        fim = hoje
    else:  # Personalizado
        with col2:
            inicio = st.date_input("De", value=hoje - timedelta(days=30))
        with col3:
            fim = st.date_input("Até", value=hoje)

    # Aplicar filtro
    mask = (
        (df_logs['data_dt'].dt.date >= inicio) &
        (df_logs['data_dt'].dt.date <= fim)
    )
    df_f = df_logs[mask].copy()

    if df_f.empty:
        st.warning(f"⚠️ Nenhum acesso entre {inicio.strftime('%d/%m/%Y')} "
                   f"e {fim.strftime('%d/%m/%Y')}.")
        return

    st.caption(f"📅 Exibindo **{len(df_f)}** acessos entre "
               f"**{inicio.strftime('%d/%m/%Y')}** e **{fim.strftime('%d/%m/%Y')}**")

    st.markdown("---")

    # ═════════════════════════════════════════════
    # KPIs
    # ═════════════════════════════════════════════
    st.markdown("#### 🎯 Indicadores Principais")

    total_acessos    = len(df_f)
    usuarios_unicos  = df_f['usuario'].nunique()
    media_dia        = df_f.groupby('data').size().mean()
    usuario_top      = df_f['usuario'].value_counts().idxmax()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("🔐 Total de Acessos", total_acessos)
    c2.metric("👥 Usuários Únicos", usuarios_unicos)
    c3.metric("📆 Média/Dia", f"{media_dia:.1f}")
    c4.metric("🏆 Usuário Top", usuario_top)
    c5.metric("📁 Processos Cadastrados", n_processos)

    st.markdown("---")

    # ═════════════════════════════════════════════
    # GRÁFICO 1 — Acessos por dia
    # ═════════════════════════════════════════════
    st.markdown("#### 📈 Acessos por Dia")

    df_dia = (
        df_f.groupby('data')
            .agg(acessos=('usuario', 'count'),
                 usuarios_unicos=('usuario', 'nunique'))
            .reset_index()
            .sort_values('data')
    )
    df_dia['data_dt'] = pd.to_datetime(df_dia['data'], format='%d/%m/%Y')
    df_dia = df_dia.sort_values('data_dt')

    fig_dia = px.bar(
        df_dia, x='data', y='acessos',
        title=None,
        labels={'data': 'Data', 'acessos': 'Nº de Acessos'},
        text='acessos',
        color='acessos',
        color_continuous_scale='Blues',
    )
    fig_dia.update_traces(textposition='outside')
    fig_dia.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        height=350,
        margin=dict(l=20, r=20, t=20, b=40),
    )
    st.plotly_chart(fig_dia, use_container_width=True)

    # ═════════════════════════════════════════════
    # GRÁFICOS 2 e 3 — Usuários e Horários
    # ═════════════════════════════════════════════
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### 👥 Distribuição por Usuário")
        df_user = (
            df_f.groupby('usuario')
                .size()
                .reset_index(name='acessos')
                .sort_values('acessos', ascending=False)
        )
        fig_user = px.pie(
            df_user, values='acessos', names='usuario',
            hole=0.4,
        )
        fig_user.update_traces(textposition='inside', textinfo='percent+label')
        fig_user.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_user, use_container_width=True)

    with col_b:
        st.markdown("#### 🕐 Acessos por Hora do Dia")
        df_f['hora_int'] = pd.to_numeric(
            df_f['hora'].str.split(':').str[0], errors='coerce'
        )
        df_hora = (
            df_f.dropna(subset=['hora_int'])
                .groupby('hora_int')
                .size()
                .reset_index(name='acessos')
        )
        df_hora['hora_label'] = df_hora['hora_int'].apply(lambda h: f"{int(h):02d}h")

        fig_hora = px.bar(
            df_hora, x='hora_label', y='acessos',
            labels={'hora_label': 'Hora', 'acessos': 'Acessos'},
            text='acessos',
            color='acessos',
            color_continuous_scale='Greens',
        )
        fig_hora.update_traces(textposition='outside')
        fig_hora.update_layout(
            showlegend=False,
            coloraxis_showscale=False,
            height=380,
            margin=dict(l=20, r=20, t=20, b=40),
        )
        st.plotly_chart(fig_hora, use_container_width=True)

    # ═════════════════════════════════════════════
    # GRÁFICO 4 — Dia da semana
    # ═════════════════════════════════════════════
    st.markdown("#### 📅 Acessos por Dia da Semana")

    ordem_dias = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                  'Friday', 'Saturday', 'Sunday']
    mapa_dias = {
        'Monday': 'Segunda', 'Tuesday': 'Terça', 'Wednesday': 'Quarta',
        'Thursday': 'Quinta', 'Friday': 'Sexta', 'Saturday': 'Sábado',
        'Sunday': 'Domingo',
    }

    df_semana = (
        df_f[df_f['dia_semana'].notna()]
            .groupby('dia_semana')
            .size()
            .reindex(ordem_dias, fill_value=0)
            .reset_index(name='acessos')
    )
    df_semana['dia_label'] = df_semana['dia_semana'].map(mapa_dias)

    fig_semana = px.bar(
        df_semana, x='dia_label', y='acessos',
        labels={'dia_label': 'Dia', 'acessos': 'Acessos'},
        text='acessos',
        color='acessos',
        color_continuous_scale='Oranges',
    )
    fig_semana.update_traces(textposition='outside')
    fig_semana.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        height=320,
        margin=dict(l=20, r=20, t=20, b=40),
    )
    st.plotly_chart(fig_semana, use_container_width=True)

    # ═════════════════════════════════════════════
    # TABELA RESUMO POR USUÁRIO
    # ═════════════════════════════════════════════
    st.markdown("#### 📋 Resumo por Usuário")

    df_resumo = (
        df_f.groupby('usuario')
            .agg(
                Total_Acessos=('usuario', 'count'),
                Primeiro_Acesso=('data_hora', 'min'),
                Ultimo_Acesso=('data_hora', 'max'),
                Dias_Ativos=('data', 'nunique'),
            )
            .reset_index()
            .sort_values('Total_Acessos', ascending=False)
    )
    df_resumo.columns = [
        'Usuário', 'Total de Acessos',
        'Primeiro Acesso', 'Último Acesso', 'Dias Ativos'
    ]
    st.dataframe(df_resumo, use_container_width=True, hide_index=True)

    # ═════════════════════════════════════════════
    # TABELA BRUTA (log detalhado)
    # ═════════════════════════════════════════════
    with st.expander(f"🔍 Log Detalhado ({len(df_f)} registros)", expanded=False):
        df_show = df_f[[
            'usuario', 'data_hora', 'dia_semana',
            'hostname', 'sistema', 'origem'
        ]].copy()
        df_show.columns = [
            'Usuário', 'Data/Hora', 'Dia', 'Hostname', 'Sistema', 'Origem'
        ]
        st.dataframe(df_show, use_container_width=True, height=400)

        # Botão de exportação CSV
        csv = df_show.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar Log em CSV",
            data=csv,
            file_name=f"logs_acesso_{datetime.now():%Y%m%d_%H%M}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    # ═════════════════════════════════════════════
    # ALERTA DE SEGURANÇA (opcional)
    # ═════════════════════════════════════════════
    st.markdown("---")
    st.markdown("#### 🚨 Alertas de Segurança")

    # Detecta acessos fora do horário comercial
    df_f['hora_int'] = pd.to_numeric(
        df_f['hora'].str.split(':').str[0], errors='coerce'
    )
    fora_horario = df_f[
        (df_f['hora_int'] < 6) | (df_f['hora_int'] > 22)
    ]

    if not fora_horario.empty:
        st.warning(
            f"⚠️ **{len(fora_horario)} acessos fora do horário comercial** "
            f"(antes das 06h ou após as 22h)."
        )
        with st.expander("Ver acessos suspeitos"):
            st.dataframe(
                fora_horario[['usuario', 'data_hora', 'hostname']],
                use_container_width=True,
                hide_index=True,
            )
    else:
        st.success("✅ Nenhum acesso em horário atípico nos últimos períodos.")

    # Detecta IPs diferentes para o mesmo usuário (possível compartilhamento)
    if 'ip_local' in df_f.columns:
        ips_por_user = (
            df_f[df_f['ip_local'].notna() & (df_f['ip_local'] != 'desconhecido')]
                .groupby('usuario')['ip_local']
                .nunique()
        )
        users_multi_ip = ips_por_user[ips_por_user > 1]

        if not users_multi_ip.empty:
            st.info(
                f"ℹ️ **{len(users_multi_ip)} usuário(s)** acessaram de "
                f"mais de um IP: {', '.join(users_multi_ip.index.tolist())}"
            )