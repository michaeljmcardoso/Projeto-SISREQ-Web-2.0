import streamlit as st
import constantes
import sqlite3
import re
from datetime import datetime

# ✅ NOVOS IMPORTS
from core_notificacao import enviar_email, notificar_cadastro
from core_sync import sincronizar_github


def tela_de_cadastro():
    st.markdown('<h4 style="color: #1f77b4;">Iniciar Processo</h4>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    # ─────────────────────────────────────────────
    # COLUNA 1
    # ─────────────────────────────────────────────
    with col1:
        numero_processo = st.text_input("Nº do Processo:")
        data_abertura = st.date_input("Data de Abertura:")
        nome_comunidade = st.text_input("Comunidade:")
        municipio = st.selectbox("Municípios:", constantes.MUNICIPIOS)
        numero_familias = st.number_input("Número de Famílias:", min_value=0)
        area_identificada = st.number_input(
            "Área Identificada (ha):", min_value=0.0, step=0.01, format="%.4f"
        )

        if numero_processo.strip():
            if re.match(r'^\d{5}.\d{6}/\d{4}-\d{2}', numero_processo.strip()):
                st.info("Número válido.")
            else:
                st.error("Número inválido! Formato: 54000.000000/2000-00.")

    # ─────────────────────────────────────────────
    # COLUNA 2
    # ─────────────────────────────────────────────
    with col2:
        fase_processo = st.selectbox("Fase:", constantes.FASE_PROCESSO)
        etapa_rtid = st.selectbox("Etapa RTID:", constantes.ETAPA_RTID)
        antropologico = st.selectbox("Antropológico:", constantes.RELATORIO_ANTROPOLOGICO)
        certidao_fcp = st.selectbox("Certidão FCP:", constantes.CERTIFICACAO_FCP)
        data_certificacao = st.text_input("Data de Certificação (DD-MM-YYYY):")

        if data_certificacao.strip():
            if re.match(r'^\d{2}-\d{2}-\d{4}$', data_certificacao.strip()):
                data_certificacao_formatada = data_certificacao.strip()
            else:
                st.error("Data de Certificação inválida! Use DD-MM-YYYY.")
                data_certificacao_formatada = None
        else:
            data_certificacao_formatada = None

    # ─────────────────────────────────────────────
    # COLUNA 3
    # ─────────────────────────────────────────────
    with col3:
        area_titulada = st.number_input(
            "Área Titulada (ha):", min_value=0.0, step=0.01, format="%.4f"
        )
        titulo = st.selectbox("Título:", constantes.FORMA_TITULO)
        pnra = st.selectbox("PNRA:", constantes.PNRA)
        latitude = st.text_input("Latitude:")
        longitude = st.text_input("Longitude:")

    # ─────────────────────────────────────────────
    # COLUNA 4
    # ─────────────────────────────────────────────
    with col4:
        edital_dou = st.text_input("Edital DOU:")
        edital_doe = st.text_input("Edital DOE:")
        portaria_dou = st.text_input("Portaria DOU: (DD-MM-YYYY)")
        decreto_dou = st.text_input("Decreto DOU: (DD-MM-YYYY)")
        sobreposicao_territorial = st.multiselect(
            "Sobreposição Territorial:", constantes.TIPO_SOBREPOSICAO
        )
        detalhes_sobreposicao = st.text_input("Detalhes de Sobreposição:")

        if portaria_dou.strip():
            if re.match(r'^\d{2}-\d{2}-\d{4}$', portaria_dou.strip()):
                st.info("Data da Portaria DOU válida.")
            else:
                st.error("Portaria DOU inválida! Use DD-MM-YYYY.")

        if decreto_dou.strip():
            if re.match(r'^\d{2}-\d{2}-\d{4}$', decreto_dou.strip()):
                st.info("Data do Decreto DOU válida.")
            else:
                st.error("Decreto DOU inválido! Use DD-MM-YYYY.")

    # ─────────────────────────────────────────────
    # LINHA FINAL
    # ─────────────────────────────────────────────
    col5 = st.columns(1)[0]
    with col5:
        acao_civil_publica = st.selectbox(
            "Ação Civil Pública:", constantes.ACAO_CIVIL_PUBLICA
        )
        data_sentenca = st.text_input("Data da Sentença: (DD-MM-YYYY)")
        teor_sentenca = st.text_input("Teor/Prazo da Sentença:")
        outras_informacoes = st.text_area("Outras Informações:", height=100)

        if data_sentenca.strip():
            if re.match(r'^\d{2}-\d{2}-\d{4}$', data_sentenca.strip()):
                st.info("Data da Sentença válida.")
            else:
                st.error("Data da Sentença inválida! Use DD-MM-YYYY.")

    # ═════════════════════════════════════════════
    # BOTÃO SALVAR — FLUXO: BD → EMAIL → GITHUB
    # ═════════════════════════════════════════════
    if st.button("Salvar", type="primary", use_container_width=True):

        if not numero_processo.strip():
            st.error("Por favor, preencha o campo 'Nº do processo'.")
            return

        # ── Formatação das datas ───────────────────
        data_abertura_formatada      = data_abertura.strftime('%d-%m-%Y') if data_abertura else None
        sobreposicao_formatada       = ", ".join(sobreposicao_territorial) if sobreposicao_territorial else None

        # ── Monta dict único com os dados (reutilizado em email + GitHub) ──
        dados_processo = {
            'Numero':                    numero_processo,
            'Data_Abertura':             data_abertura_formatada,
            'Comunidade':                nome_comunidade,
            'Municipio':                 municipio,
            'Area_ha':                   area_identificada,
            'Num_familias':              numero_familias,
            'Fase_Processo':             fase_processo,
            'Etapa_RTID':                etapa_rtid,
            'Edital_DOU':                edital_dou,
            'Edital_DOE':                edital_doe,
            'Portaria_DOU':              portaria_dou,
            'Decreto_DOU':               decreto_dou,
            'Area_ha_Titulada':          area_titulada,
            'Titulo':                    titulo,
            'PNRA':                      pnra,
            'Relatorio_Antropologico':   antropologico,
            'Latitude':                  latitude,
            'Longitude':                 longitude,
            'Certidao_FCP':              certidao_fcp,
            'Data_Certificacao':         data_certificacao_formatada,
            'Sobreposicao':              sobreposicao_formatada,
            'Analise_de_Sobreposicao':   detalhes_sobreposicao,
            'Acao_Civil_Publica':        acao_civil_publica,
            'Data_Decisao':              data_sentenca,
            'Numero_Acao_Civil_Publica': teor_sentenca,
            'Outras_Informacoes':        outras_informacoes,
        }

        # ─────────────────────────────────────────
        # 1️⃣ SALVAR NO BANCO
        # ─────────────────────────────────────────
        try:
            conn = sqlite3.connect('sisreq.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO processos (
                    Numero, Data_Abertura, Comunidade, Municipio, Area_ha,
                    Num_familias, Fase_Processo, Etapa_RTID, Edital_DOU, Edital_DOE,
                    Portaria_DOU, Decreto_DOU, Area_ha_Titulada, Titulo, PNRA,
                    Relatorio_Antropologico, Latitude, Longitude, Certidao_FCP,
                    Data_Certificacao, Sobreposicao, Analise_de_Sobreposicao,
                    Acao_Civil_Publica, Data_Decisao, Numero_Acao_Civil_Publica,
                    Outras_Informacoes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                numero_processo, data_abertura_formatada, nome_comunidade, municipio,
                area_identificada, numero_familias, fase_processo, etapa_rtid,
                edital_dou, edital_doe, portaria_dou, decreto_dou, area_titulada,
                titulo, pnra, antropologico, latitude, longitude, certidao_fcp,
                data_certificacao_formatada, sobreposicao_formatada,
                detalhes_sobreposicao, acao_civil_publica, data_sentenca,
                teor_sentenca, outras_informacoes
            ))
            conn.commit()
            novo_id = cursor.lastrowid
            conn.close()
            dados_processo['id'] = novo_id
            st.success(f"✅ Processo {nome_comunidade} salvo com sucesso! (ID {novo_id})")
        except Exception as e:
            st.error(f"❌ Erro ao salvar no banco: {e}")
            return

        # ─────────────────────────────────────────
        # 2️⃣ ENVIAR EMAIL DE CONFIRMAÇÃO
        # ─────────────────────────────────────────
        try:
            with st.spinner("📧 Enviando email de confirmação..."):
                assunto, html = notificar_cadastro(dados_processo)
                enviado, destinatarios = enviar_email(assunto, html)

            if enviado:
                st.info(f"📧 Email enviado para: {', '.join(destinatarios)}")
            else:
                st.warning("⚠️ Processo salvo, mas o email não pôde ser enviado.")
        except Exception as e:
            st.warning(f"⚠️ Processo salvo, mas houve erro no email: {e}")

        # ─────────────────────────────────────────
        # 3️⃣ SINCRONIZAR COM GITHUB
        # ─────────────────────────────────────────
        try:
            with st.spinner("🔄 Sincronizando com GitHub..."):
                github_result = sincronizar_github("cadastro", dados_processo)

            if github_result.get('success'):
                st.success(f"🔄 {github_result.get('message', 'Sincronizado com GitHub!')}")
            else:
                st.warning(f"⚠️ Erro na sincronização: {github_result.get('error', '')}")
        except Exception as e:
            st.warning(f"⚠️ Erro na sincronização com GitHub: {e}")