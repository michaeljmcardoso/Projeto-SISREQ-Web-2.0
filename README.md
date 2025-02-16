# Projeto-SISREQ-Web-2.0
Versão Web 2.0 do Sistema de Regularização Quilombola

---

# SISREQ - Sistema de Regularização Quilombola

<p>
  O SISREQ é um sistema de gerenciamento de registros para a regularização quilombola, desenvolvido para facilitar o controle, acompanhamento e análise de processos. Ele utiliza tecnologias modernas para oferecer uma experiência intuitiva e eficiente, tanto em ambientes desktop quanto mobile. O sistema agora conta com um assistente virtual chamado SISREQ_IA, que utiliza a API `google.generativeai` para fornecer suporte e informações em tempo real. Além disso, o projeto possui controle de acesso de usuários, garantindo segurança e privacidade dos dados.
</p>

## Tecnologias Utilizadas

<p>
  Para a concepção do programa, utilizamos as seguintes bibliotecas e ferramentas:

   - **Backend e Banco de Dados:**
     - `sqlite3` para manipulação do banco de dados SQLite.
     - `pandas` para manipulação de dados e exportação para planilha.
     - `google.generativeai` para integração com a API de geração de texto.

   - **Interface Gráfica e Deploy:**
     - `Streamlit` para criação da interface gráfica e deploy da aplicação.
     - `Streamlit Cloud` para hospedagem e disponibilização da aplicação.

   - **Visualização de Dados:**
     - `Seaborn` e `Matplotlib` para criação e plotagem de visualizações gráficas.

   - **Segurança:**
     - Controle de acesso de usuários para garantir a privacidade e segurança dos dados.
</p>

## Funcionalidades Principais

### 1. **Cadastro e Gerenciamento de Processos**
   - Permite cadastrar processos com informações como número do processo, município, fase do processo, data de entrada, entre outros.
   - Oferece funcionalidades para consultar, filtrar, atualizar e excluir registros.

### 2. **SISREQ IA - Assistente Virtual**
   - O assistente virtual **SISREQ IA** utiliza a API `google.generativeai` para interagir com os usuários, fornecendo informações e suporte em tempo real.
   - Configurado com o modelo `gemini-1.5-flash`, o mais rápido e multimodal da Google, ele gera respostas criativas e precisas.
   - Funcionalidades do SISREQ IA:
     - Responde a perguntas sobre processos, fases, prazos e outras informações relevantes.
     - Mantém um tom amigável e humanizado, melhorando a experiência do usuário.
     - Configurações de segurança personalizadas para garantir interações seguras.

### 3. **Controle de Acesso**
   - O sistema possui controle de acesso de usuários, garantindo que apenas pessoas autorizadas possam visualizar, inserir ou alterar dados.
   - Futuramente, será implementada autenticação multifator para maior segurança.

### 4. **Relatórios e Gráficos**
   - Gera relatórios e gráficos com base nos dados armazenados, permitindo a análise de informações como:
     - Quantidade de processos por município.
     - Distribuição dos processos por fase.
     - Outras métricas relevantes.

### 5. **Exportação de Dados**
   - Permite exportar registros para planilhas Excel, facilitando a geração de relatórios externos.

### 6. **Interface Moderna e Responsiva**
   - Desenvolvida com `Streamlit`, a interface é moderna, intuitiva e responsiva, funcionando tanto em desktops quanto em dispositivos móveis.
   - Componentes interativos, como seletores, botões e gráficos dinâmicos, melhoram a experiência do usuário.

---

## Step by Step

### 1. **Banco de Dados**
   - O sistema cria ou conecta-se a um banco de dados SQLite chamado `sisreq.db`.
   - A tabela `sisreq` é criada com as seguintes colunas:
     - **ID, Numero TEXT, Data_Abertura DATE, Comunidade TEXT, Municipio TEXT, Area_ha NUMERIC, Num_familias NUMERIC, Fase_Processo TEXT, Etapa_RTID TEXT, Edital_DOU TEXT, Edital_DOE TEXT, Portaria_DOU DATE, Decreto_DOU DATE, Titulo TEXT, PNRA TEXT, Relatorio_Antropologico TEXT, Certidao_FCP TEXT, Data_Certificacao DATE, Sobreposicao TEXT, Analise_de_Sobreposicao TEXT, Acao_Civil_Publica TEXT, Data_Decisao DATE, Teor_Decisao_Prazo_Sentença TEXT, Outras_Informacoes TEXT.**

### 2. **Interface Gráfica**
   - A interface é construída com `Streamlit`, oferecendo:
     - Campos de entrada para cadastro de processos.
     - Botões para consulta, filtragem e exportação de dados.
     - Tabelas interativas para exibição de registros.
     - Componentes para seleção de fases e filtros.

### 3. **SISREQ IA - Integração com API**
   - O assistente virtual é configurado com a API `google.generativeai`.
   - Utiliza o modelo `gemini-1.5-flash` para gerar respostas rápidas e precisas.
   - Configurações de segurança personalizadas garantem interações seguras.

### 4. **Deploy com Streamlit Cloud**
   - A aplicação foi deployada utilizando o `Streamlit Cloud`, permitindo acesso global via navegador.
   - O deploy é simples e eficiente, garantindo alta disponibilidade e escalabilidade.

---

## Como Executar o Projeto

### 1. **Instalação das Dependências**
   ```bash
   pip install streamlit pandas sqlite3 matplotlib seaborn google-generativeai
   ```

### 2. **Executar a Aplicação Localmente**
   ```bash
   streamlit run app.py
   ```

### 3. **Acessar a Interface**
   - Abra o navegador e acesse o endereço fornecido pelo `Streamlit` (geralmente `http://localhost:8501`).

### 4. **Deploy na Nuvem**
   - Para realizar o deploy no `Streamlit Cloud`, siga as instruções da plataforma:
     1. Crie uma conta no [Streamlit Cloud](https://streamlit.io/cloud).
     2. Conecte o repositório do projeto (GitHub, GitLab, etc.).
     3. Configure as variáveis de ambiente, como a chave da API `google.generativeai`.
     4. Faça o deploy e acesse a aplicação online.

---

## Exemplo de Uso

### 1. **Interação com o SISREQ IA**
   - **Usuário:** "Qual é o próximo passo para o processo X?"
   - **SISREQ IA:** "O próximo passo para o processo X é a fase de análise técnica. Recomendamos enviar os documentos necessários até o dia 30/10/2023."

### 2. **Geração de Relatórios**
   - O usuário pode filtrar processos por município e exportar um relatório em Excel.

### 3. **Visualização de Gráficos**
   - Gráficos interativos mostram a distribuição de processos por fase ou município.

---

## Objetivo do Projeto

O SISREQ foi projetado para:
- Facilitar o gerenciamento de processos de regularização quilombola.
- Oferecer suporte virtual por meio do **SISREQ IA**.
- Garantir segurança e privacidade com controle de acesso de usuários.
- Fornecer uma interface moderna e responsiva, acessível em qualquer dispositivo.
- Gerar relatórios e gráficos para análise e tomada de decisões.

---

## Próximos Passos

1. **Autenticação Multifator:** Implementar autenticação multifator para maior segurança.
2. **Integração com Outros Sistemas:** Conectar o SISREQ a sistemas governamentais para sincronização automática de dados.
3. **Notificações Automáticas:** Enviar notificações por e-mail ou SMS sobre prazos e atualizações de processos.

---

## Contato

Para mais informações, sugestões ou colaborações, entre em contato:
- **E-mail:** [michaeljmc@outlook.com.br]
- **Repositório:** [(https://github.com/michaeljmcardoso/Projeto-SISREQ-Web-2.0)]

---

Este `README` reflete todas as funcionalidades atuais do projeto, incluindo o controle de acesso, o assistente virtual SISREQ IA, e o deploy com Streamlit Cloud. 😊
