# Calculadora de Notas de Treinamento

Esta é uma aplicação web desenvolvida em Streamlit para automatizar o cálculo de notas de participantes de treinamentos, baseada em critérios específicos de pontualidade, interação e avaliação.

## Funcionalidades Principais

- **Cálculo Automatizado de Notas:** Calcula a nota final dos colaboradores com base em três pilares: Pontualidade, Interação e Avaliação Final.
- **Upload de Lista de Presença (CSV ou PDF com IA):** Permite carregar a lista de presença exportada do Microsoft Teams (`.csv`) ou arquivos PDF. Para PDFs, a extração de dados é realizada por Inteligência Artificial.
- **Cálculo de Frequência e Atraso:** Utiliza os logs de entrada e saída do arquivo do Teams (ou dados extraídos por IA do PDF) para calcular automaticamente a frequência e o atraso de cada participante.
- **Geração de Relatórios em PDF:** Gera um relatório detalhado e profissional em PDF com o resumo do desempenho da turma e os resultados individuais.
- **Interface Intuitiva:** Interface web simples e direta para que os instrutores possam inserir os dados e obter os resultados de forma rápida.
- **IA de PDF (Perguntas e Respostas / Extração Estruturada):** Uma seção dedicada onde você pode fazer perguntas sobre o conteúdo de PDFs ou extrair dados estruturados (em formato JSON) de documentos PDF usando modelos de IA.

## Como Usar

1.  **Acesse a Aplicação:** Abra o link da aplicação no Streamlit Cloud.
2.  **Configure o Treinamento:** Na barra lateral, ajuste as configurações do treinamento:
    *   **Título do Treinamento:** Defina o nome do treinamento que aparecerá no relatório.
    *   **Total de Oportunidades de Interação:** Informe quantas interações foram planejadas.
    *   **Total de Check-ins no Dia:** Defina o número de verificações de pontualidade (ex: início e volta do almoço).
    *   **Horário de Início, Duração e Mínimo de Presença:** Ajuste os parâmetros para o cálculo automático de frequência.
3.  **Carregue a Lista de Presença:** Faça o upload do arquivo `.csv` ou `.pdf`.
    *   Para arquivos CSV, o processamento é direto.
    *   Para arquivos PDF, a IA tentará extrair automaticamente os dados de nome, timestamp e ação (Joined/Left).
4.  **Preencha os Dados Manuais:** Para cada colaborador, preencha os campos que requerem avaliação do instrutor (Nº de Check-ins Pontuais, Interações Válidas e Acertos na Prova).
5.  **Calcule e Baixe o Relatório:** Clique no botão "Calcular Resultados Finais" e, em seguida, baixe o relatório completo em PDF.

## Estrutura do Projeto

```
calc_opsul/
├── app.py                # Arquivo principal da aplicação Streamlit
├── requirements.txt        # Dependências do projeto
├── README.md               # Este arquivo
├── end/
│   └── calculos.py       # Módulo com as lógicas de cálculo das notas
├── front/
│   └── interface.py      # Módulo que define a interface do usuário
├── ia/
│   ├── api_load.py       # Módulo para carregar a API do Gemini
│   └── pdf_qa.py         # Módulo para funcionalidades de QA e extração de dados de PDF com IA
```

## Instalação e Execução Local

1.  **Clone o repositório:**
    ```bash
    git clone <url-do-seu-repositorio>
    cd calc_opsul
    ```

2.  **Crie um ambiente virtual e instale as dependências:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Execute a aplicação:**
    ```bash
    streamlit run app.py
    ```
