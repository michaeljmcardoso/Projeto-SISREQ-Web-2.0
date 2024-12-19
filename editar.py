import streamlit as st
import sqlite3
import constantes
import re
from datetime import datetime
from obter_todos_registros import obter_todos_os_registros, obter_registro_por_id

# Página de Edição: Atualização de registros existentes
def pagina_editar():
    st.header("Editar Registros")

    st.subheader("Processos Salvos")
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
            #st.subheader("Atualizar Processo")

            # Divisão em colunas para entrada de dados
            col1, col2, col3, col4 = st.columns(4)
            
            # Coluna 1
            with col1:
                new_numero_processo = st.text_input("Número do Processo:", value=registro[1])
                new_data_abertura = st.date_input("Data de Abertura:", value=datetime.strptime(registro[2], '%d-%m-%Y'))
                new_nome_comunidade = st.text_input("Comunidade:", value=registro[3])
                new_municipio = st.text_input("Município:", value=registro[4])
                new_numero_familias = st.number_input("Número de Famílias:", min_value=0, value=int(registro[6]) if registro[6] else 0,)
                new_area_identificada = st.number_input("Área Identificada (ha):", min_value=0.0, step=0.01, format="%.2f", value=float(registro[5]) if registro[5] else 0.0)

            # Coluna 2
            with col2:
                # Recuperar os valores existentes ou usar vazio como padrão
                data_certificacao = registro[20] if registro [20] else ""

                new_fase_processo = st.select_slider("Fase:", options=constantes.FASE_PROCESSO, value=registro[7] if registro[7] in constantes.FASE_PROCESSO else constantes.FASE_PROCESSO[0])
                etapa_rtid = st.select_slider("Etapa RTID:", options=constantes.ETAPA_RTID, value=registro[8] if registro[8] in constantes.ETAPA_RTID else constantes.ETAPA_RTID[0])
                new_antropologico = st.selectbox("Antropológico:", constantes.RELATORIO_ANTROPOLOGICO, index=constantes.RELATORIO_ANTROPOLOGICO.index(registro[16]))
                new_certidao_fcp = st.selectbox("Certidão FCP:", constantes.CERTIFICACAO_FCP, index=constantes.CERTIFICACAO_FCP.index(registro[19]))
                new_data_certificacao = st.text_input("Data de Certificação (formato: DD-MM-YYYY):", value=data_certificacao)
                
                data_certificacao_formatada = None

                if new_data_certificacao.strip():  
                    # Regex para verificar se a data está no formato DD-MM-YYYY
                    if re.match(r'^\d{2}-\d{2}-\d{4}$', new_data_certificacao.strip()):
                        data_certificacao_formatada = new_data_certificacao.strip()  # Apenas atribuir a string
                    else:
                        st.error("Data Certificação inválida! Por favor, use o formato DD-MM-YYYY.")

            # Coluna 3
            with col3:
                new_area_titulada = st.number_input("Área Titulada (ha):", min_value=0.0, step=0.01, format="%.2f", value=float(registro[13] if registro[13] else 0.0))
                titulo = st.select_slider("Titulo:", options=constantes.FORMA_TITULO, value=registro[14] if registro[14] in constantes.FORMA_TITULO else constantes.FORMA_TITULO[0])
                new_pnra = st.selectbox("PNRA:", constantes.PNRA, index=constantes.PNRA.index(registro[15]) if registro[15] in constantes.PNRA else 0)
                new_latitude = st.text_input("Latitude:", value=registro[17])
                new_longitude = st.text_input("Longitude:", value=registro[18])

            # Coluna 4
            with col4:
                # Recuperar os valores existentes ou usar vazio como padrão
                portaria_dou = registro[11] if registro[11] else ""
                decreto_dou = registro[12] if registro[12] else ""

                new_edital_dou = st.text_input("Edital DOU:", value=registro[9])
                new_edital_doe = st.text_input("Edital DOE:", value=registro[10])
                new_portaria_dou_input = st.text_input("Portaria DOU (formato: DD-MM-YYYY):", value=portaria_dou)
                new_decreto_dou_input = st.text_input("Decreto DOU (formato: DD-MM-YYYY):", value=decreto_dou)
                sobreposicao_territorial = st.multiselect("Sobreposição Territorial:", constantes.TIPO_SOBREPOSICAO)
                new_detalhes_sobreposicao = st.text_input("Detalhes de Sobreposição:", value=registro[22])

                portaria_dou_formatada = None
                decreto_dou_formatada = None

                if new_portaria_dou_input.strip():  
                    # Regex para verificar se a data está no formato DD-MM-YYYY
                    if re.match(r'^\d{2}-\d{2}-\d{4}$', new_portaria_dou_input.strip()):
                        portaria_dou_formatada = new_portaria_dou_input.strip()  # Apenas atribuir a string
                    else:
                        st.error("Portaria DOU inválida! Por favor, use o formato DD-MM-YYYY.")

                if new_decreto_dou_input.strip():  
                    # Regex para verificar se a data está no formato DD-MM-YYYY
                    if re.match(r'^\d{2}-\d{2}-\d{4}$', new_decreto_dou_input.strip()):
                        decreto_dou_formatada = new_decreto_dou_input.strip()  # Apenas atribuir a string
                    else:
                        st.error("Decreto DOU inválido! Por favor, use o formato DD-MM-YYYY.")

            # Coluna 5
            st.markdown("---")

            new_acao_civil_publica = st.selectbox(
                "Ação Civil Pública:", 
                constantes.ACAO_CIVIL_PUBLICA, 
                index=constantes.ACAO_CIVIL_PUBLICA.index(registro[23])
            )

            # Recuperar os valores existentes ou usar vazio como padrão
            data_sentenca = registro[24] if registro[24] else ""
            
            # Campos de entrada de texto para data
            new_data_sentenca = st.text_input("Data da Sentença (formato: DD-MM-YYYY):", value=data_sentenca)
            
            # Inicializar as variáveis para salvar no banco
            data_sentenca_formatada = None
            
            # Validar o formato das datas como string
            if new_data_sentenca.strip():  
                # Regex para verificar se a data está no formato DD-MM-YYYY
                if re.match(r'^\d{2}-\d{2}-\d{4}$', new_data_sentenca.strip()):
                    data_sentenca_formatada = new_data_sentenca.strip()  # Apenas atribuir a string
                else:
                    st.error("Data da Sentença inválida! Por favor, use o formato DD-MM-YYYY.")

            new_teor_sentenca = st.text_input("Teor/Prazo da Sentença:", value=registro[25])
            new_outras_informacoes = st.text_area("Outras Informações:", value=registro[26], height=100)

            # Botão para atualizar o registro
            if st.button("Atualizar"):
                # Verificar se a data é inválida e exibir erro
                
                if (new_data_sentenca.strip() and not data_sentenca_formatada) or (new_portaria_dou_input.strip() and not portaria_dou_formatada) or (new_decreto_dou_input.strip() and not decreto_dou_formatada) or (new_data_certificacao.strip() and not data_certificacao_formatada):
                    st.error("Uma ou mais datas fornecidas são inválidas. Corrija antes de atualizar.")
                else:
                    # Convertendo as datas para o formato DD-MM-YYYY
                    data_abertura_formatada = new_data_abertura.strftime('%d-%m-%Y') if new_data_abertura else None
                    sobreposicao_territorial_formatada = ", ".join(sobreposicao_territorial) if sobreposicao_territorial else None
                    
                    # Conexão e atualização no banco
                    conn = sqlite3.connect('sisreq.db')
                    cursor = conn.cursor()
                    cursor.execute('''
                        UPDATE processos
                        SET Numero = ?, Data_Abertura = ?, Comunidade = ?, Municipio = ?, Area_ha = ?, Num_familias = ?, Fase_Processo = ?, 
                        Etapa_RTID = ?, Edital_DOU = ?, Edital_DOE = ?, Portaria_DOU = ?, Decreto_DOU = ?, Area_ha_Titulada = ?, Titulo = ?, 
                        PNRA = ?, Relatorio_Antropologico = ?, Latitude = ?, Longitude = ?, Certidao_FCP = ?, Data_Certificacao = ?, 
                        Sobreposicao = ?, Analise_de_Sobreposicao = ?, Acao_Civil_Publica = ?, Data_Decisao = ?, Teor_Decisao_Prazo_Sentença = ?, Outras_Informacoes = ?
                        WHERE id = ?
                    ''', (new_numero_processo, data_abertura_formatada, new_nome_comunidade, new_municipio, new_area_identificada, new_numero_familias, 
                        new_fase_processo, etapa_rtid, new_edital_dou, new_edital_doe, portaria_dou_formatada, decreto_dou_formatada, 
                        new_area_titulada, titulo, new_pnra, new_antropologico, new_latitude, new_longitude, new_certidao_fcp, 
                        data_certificacao_formatada, sobreposicao_territorial_formatada, new_detalhes_sobreposicao, new_acao_civil_publica, 
                        new_data_sentenca, new_teor_sentenca, new_outras_informacoes, item_id))
                    conn.commit()
                    st.success(f"Processo {new_nome_comunidade} atualizado com sucesso!")
                    conn.close()

        else:
            st.warning("ID inválido. Por favor, selecione um ID existente.")
    return(pagina_editar)