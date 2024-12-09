import streamlit as st
import sqlite3
import constantes
from datetime import datetime
from obter_todos_registros import obter_todos_os_registros, obter_registro_por_id

# Página de Edição: Atualização de registros existentes
def pagina_editar():
    st.header("Editar Registro de Processos")

    st.subheader("Registros Salvos")
    df = obter_todos_os_registros()  # Função que busca todos os registros no banco
    if not df.empty:
        if 'ID' in df.columns:
            df = df.drop(columns=['ID'])
            df.index = df.index + 1  # Ajusta o índice para começar em 1
            st.dataframe(df)

        # Entrada do ID para edição
        item_id = st.number_input("Digite o ID do Processo para Editar", min_value=1, step=1)
        registro = obter_registro_por_id(item_id)  # Função para obter o registro específico

        if registro:
            st.subheader("Atualizar Processo")

            # Divisão em colunas para entrada de dados
            col1, col2, col3, col4, col5 = st.columns(5)
            
            # Coluna 1
            with col1:
                new_numero_processo = st.text_input("Número do Processo:", value=registro[1])
                new_data_abertura = st.date_input("Data de Abertura:", value=datetime.strptime(registro[2], '%d-%m-%Y'))
                new_nome_comunidade = st.text_input("Comunidade:", value=registro[3])
                new_municipio = st.text_input("Município:", value=registro[4])
                new_numero_familias = st.number_input("Número de Famílias:", min_value=0, value=int(registro[6]) if registro[6] else 0,)

            # Coluna 2
            with col2:
                new_fase_processo = st.select_slider("Fase:", options=constantes.FASE_PROCESSO, value=registro[7] if registro[7] in constantes.FASE_PROCESSO else constantes.FASE_PROCESSO[0])
                new_etapa_rtid = st.selectbox("Etapa RTID:", constantes.ETAPA_RTID, index=constantes.ETAPA_RTID.index(registro[8]))
                new_antropologico = st.selectbox("Antropológico:", constantes.RELATORIO_ANTROPOLOGICO, index=constantes.RELATORIO_ANTROPOLOGICO.index(registro[16]))
                new_certidao_fcp = st.selectbox("Certidão FCP:", constantes.CERTIFICACAO_FCP, index=constantes.CERTIFICACAO_FCP.index(registro[19]))
                new_data_certificacao = st.date_input("Data de Certificação:", value=datetime.strptime(registro[11], '%d-%m-%Y') if registro[11] else None)

            # Coluna 3
            with col3:
                new_area_identificada = st.text_input("Área Identificada (ha):", value=str(registro[5]))
                new_area_titulada = st.text_input("Área Titulada (ha):", value=str(registro[13]))
                new_titulo = st.selectbox("Título:", constantes.FORMA_TITULO, index=constantes.FORMA_TITULO.index(registro[14]) if registro[14] in constantes.FORMA_TITULO else 0)
                new_pnra = st.selectbox("PNRA:", constantes.PNRA, index=constantes.PNRA.index(registro[15]) if registro[15] in constantes.PNRA else 0)
                new_latitude = st.text_input("Latitude:", value=registro[17])
                new_longitude = st.text_input("Longitude:", value=registro[18])

            # Coluna 4
            with col4:
                new_edital_dou = st.text_input("Edital DOU:", value=registro[9])
                new_edital_doe = st.text_input("Edital DOE:", value=registro[10])
                new_portaria_dou = st.date_input("Portaria DOU:", value=datetime.strptime(registro[11], '%d-%m-%Y') if registro[11] else None)
                new_decreto_dou = st.date_input("Decreto DOU:", value=datetime.strptime(registro[12], '%d-%m-%Y') if registro[12] else None)
                new_sobreposicao_territorial = st.selectbox("Sobreposição Territorial:", constantes.TIPO_SOBREPOSICAO, index=constantes.TIPO_SOBREPOSICAO.index(registro[21]))

            # Coluna 5
            with col5:
                new_detalhes_sobreposicao = st.text_input("Detalhes de Sobreposição:", value=registro[22])
                new_acao_civil_publica = st.selectbox("Ação Civil Pública:", constantes.ACAO_CIVIL_PUBLICA, index=constantes.ACAO_CIVIL_PUBLICA.index(registro[23]))
                new_data_sentenca = st.date_input("Data da Sentença:", value=datetime.strptime(registro[24], '%d-%m-%Y') if registro[24] else None)
                new_teor_sentenca = st.text_input("Teor/Prazo da Sentença:", value=registro[25])
                new_outras_informacoes = st.text_area("Outras Informações:", value=registro[26], height=50)

            # Botão para atualizar o registro
            if st.button("Atualizar"):
                # Convertendo as datas para o formato YYYY-MM-DD
                data_abertura_formatada = new_data_abertura.strftime('%d-%m-%Y') if new_data_abertura else None
                data_certificacao_formatada = new_data_certificacao.strftime('%d-%m-%Y') if new_data_certificacao else None
                portaria_dou_formatada = new_portaria_dou.strftime('%d-%m-%Y') if new_portaria_dou else None
                decreto_dou_formatada = new_decreto_dou.strftime('%d-%m-%Y') if new_decreto_dou else None

                # Conexão e atualização no banco
                conn = sqlite3.connect('sisreq.db')
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE processos
                    SET Numero = ?, Data_Abertura = ?, Comunidade = ?, Municipio = ?, Num_familias = ?, Fase_Processo = ?, 
                        Data_Certificacao = ?, Portaria_DOU = ?, Decreto_DOU = ?
                    WHERE id = ?
                ''', (new_numero_processo, data_abertura_formatada, new_nome_comunidade, new_municipio, new_numero_familias, 
                      new_fase_processo, data_certificacao_formatada, portaria_dou_formatada, decreto_dou_formatada, item_id))
                conn.commit()
                st.success(f"Registro {new_numero_processo} atualizado com sucesso!")
                conn.close()

        else:
            st.warning("ID inválido. Por favor, selecione um ID existente.")
    return(pagina_editar)