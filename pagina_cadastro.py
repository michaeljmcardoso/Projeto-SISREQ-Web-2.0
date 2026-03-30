import streamlit as st
import constantes
import sqlite3
import re

def tela_de_cadastro():
    st.markdown('<h4 style="color: "#1f77b4";">Iniciar Processo</h4df3>', unsafe_allow_html=True)
# Ajustando para 4 colunas
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        numero_processo = st.text_input("Nº do Processo:")
        data_abertura = st.date_input("Data de Abertura:")
        nome_comunidade = st.text_input("Comunidade:")
        municipio = st.selectbox("Municípios:", constantes.MUNICIPIOS)
        numero_familias = st.number_input("Número de Famílias:", min_value=0)
        area_identificada = st.number_input("Área Identificada (ha):", min_value=0.0,  step=0.01, format="%.4f")

        if numero_processo.strip():
            if re.match(r'^\d{5}.\d{6}/\d{4}-\d{2}', numero_processo.strip()):
                st.info("Número válido.")
            else:
                st.error("Número inválido! Por favor, use o formato 54000.000000/2000-00.")   

    with col2:
        fase_processo = st.selectbox("Fase:", constantes.FASE_PROCESSO)
        etapa_rtid = st.selectbox("Etapa RTID:", constantes.ETAPA_RTID)
        antropologico = st.selectbox("Antropológico:", constantes.RELATORIO_ANTROPOLOGICO)
        certidao_fcp = st.selectbox("Certidão FCP:", constantes.CERTIFICACAO_FCP)
        data_certificacao = st.text_input("Data de Certificação (DD-MM-YYYY):")

        # Validar a data de certificação
        if data_certificacao.strip():  # Verifica se a entrada não está vazia
            if re.match(r'^\d{2}-\d{2}-\d{4}$', data_certificacao.strip()):
                data_certificacao_formatada = data_certificacao.strip()
            else:
                st.error("Data de Certificação inválida! Por favor, use o formato DD-MM-YYYY.")
        else:
            data_certificacao_formatada = None  # Caso esteja vazia

    with col3:
        
        area_titulada = st.number_input("Área Titulada (ha):", min_value=0.0,  step=0.01, format="%.4f")
        titulo = st.selectbox("Título:", constantes.FORMA_TITULO)
        pnra = st.selectbox("PNRA:", constantes.PNRA)
        latitude = st.text_input("Latitude:")
        longitude = st.text_input("Longitude:")

    with col4:
        edital_dou = st.text_input("Edital DOU:")
        edital_doe = st.text_input("Edital DOE:")
        portaria_dou = st.text_input("Portaria DOU: (DD-MM-YYYY)")
        decreto_dou = st.text_input("Decreto DOU: (DD-MM-YYYY)")
        sobreposicao_territorial = st.multiselect("Sobreposição Territorial:", constantes.TIPO_SOBREPOSICAO)
        detalhes_sobreposicao = st.text_input("Detalhes de Sobreposição:")

        # Validação do campo Portaria DOU
        if portaria_dou.strip():
            if re.match(r'^\d{2}-\d{2}-\d{4}$', portaria_dou.strip()):
                st.info("Data da Portaria DOU válida.")
            else:
                st.error("Portaria DOU inválida! Por favor, use o formato DD-MM-YYYY.")

        # Validação do campo Decreto DOU
        if decreto_dou.strip():
            if re.match(r'^\d{2}-\d{2}-\d{4}$', decreto_dou.strip()):
                st.info("Data do Decreto DOU válida.")
            else:
                st.error("Decreto DOU inválido! Por favor, use o formato DD-MM-YYYY.")

    # Nova linha para campos adicionais, caso necessário
    col5 = st.columns(1)[0]
    with col5:
        acao_civil_publica = st.selectbox("Ação Civil Pública:", constantes.ACAO_CIVIL_PUBLICA)
        data_sentenca = st.text_input("Data da Sentença: (DD-MM-YYYY)")
        teor_sentenca = st.text_input("Teor/Prazo da Sentença:")
        outras_informacoes = st.text_area("Outras Informações:", height=100)

        if data_sentenca.strip():
            if re.match(r'^\d{2}-\d{2}-\d{4}$', data_sentenca.strip()):
                st.info("Data da Sentença válida.")
            else:
                st.error("Data da Sentença inválida! Por favor, use o formato DD-MM-YYYY.")

    if st.button("Salvar"):
        conn = sqlite3.connect('sisreq.db')
        cursor = conn.cursor()

        if numero_processo:
            # Convertendo as datas para o formato desejado antes de salvar
            data_abertura_formatada = data_abertura.strftime('%d-%m-%Y') if data_abertura else None
            data_certificacao_formatada = data_certificacao.strftime('%d-%m-%Y') if data_certificacao else None
            portaria_dou_formatada = portaria_dou.strftime('%d-%m-%Y') if portaria_dou else None
            decreto_dou_formatada = decreto_dou.strftime('%d-%m-%Y') if decreto_dou else None
            data_sentenca_formatada = data_sentenca.strftime('%d-%m-%Y') if data_sentenca else None

            # Convertendo a lista do multiselect para uma string
            #etapa_rtid_formatada = ", ".join(etapa_rtid) if etapa_rtid else None
            sobreposicao_territorial_formatada = ", ".join(sobreposicao_territorial) if sobreposicao_territorial else None

            # Executando o comando SQL com as datas formatadas
            cursor.execute('''INSERT INTO processos ('Numero', 'Data_Abertura', 'Comunidade', 'Municipio', 'Area_ha','Num_familias', 
                        'Fase_Processo', 'Etapa_RTID', 'Edital_DOU', 'Edital_DOE', 'Portaria_DOU', 'Decreto_DOU', 'Area_ha_Titulada',
                        'Titulo', 'PNRA', 'Relatorio_Antropologico', 'Latitude', 'Longitude', 'Certidao_FCP', 'Data_Certificacao', 
                        'Sobreposicao', 'Analise_de_Sobreposicao', 'Acao_Civil_Publica', 'Data_Decisao', 'Numero_Acao_Civil_Publica', 
                        'Outras_Informacoes') 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                        (numero_processo, data_abertura_formatada, nome_comunidade, municipio, area_identificada, numero_familias,
                        fase_processo, etapa_rtid, edital_dou, edital_doe, portaria_dou_formatada, decreto_dou_formatada,
                        area_titulada, titulo, pnra, antropologico, latitude, longitude, certidao_fcp, data_certificacao_formatada,
                        sobreposicao_territorial_formatada, detalhes_sobreposicao, acao_civil_publica, data_sentenca_formatada,
                        teor_sentenca, outras_informacoes))
            conn.commit()
            st.success(f"Os dados de comunidade {nome_comunidade} foram salvos com sucesso!")
        else:
            st.error("Por favor, preencha o campo 'Número do processo'.")
        conn.close()