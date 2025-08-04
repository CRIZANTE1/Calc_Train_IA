import streamlit as st
import pandas as pd
import io
import requests
import base64
from weasyprint import HTML
from datetime import datetime, time, timedelta

# Importação do pacote IA
from IA.pdf_qa import PDFQA

# --- Funções de Geração de PDF ---

@st.cache_data(ttl=3600)
def get_logo_base64(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            encoded_string = base64.b64encode(response.content).decode('utf-8')
            return f"data:image/svg+xml;base64,{encoded_string}"
        return None
    except Exception:
        return None

def create_enhanced_report_html(df, logo_url, training_title):
    logo_base64 = get_logo_base64(logo_url)
    total_colaboradores = len(df)
    aprovados = df[df['Status'] == 'Aprovado'].shape[0]
    reprovados = total_colaboradores - aprovados
    taxa_aprovacao = (aprovados / total_colaboradores * 100) if total_colaboradores > 0 else 0

    df_html = df.to_html(index=False, border=0, classes='styled-table')

    html_string = f"""
    <html>
        <head>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
                body {{ font-family: 'Roboto', sans-serif; color: #333; }}
                .header {{ text-align: center; border-bottom: 2px solid #005a8c; padding-bottom: 15px; }}
                .logo {{ max-width: 200px; margin-bottom: 10px; }}
                h1 {{ color: #002a4d; font-size: 24px; margin: 0; }}
                h2 {{ color: #002a4d; font-size: 20px; border-bottom: 1px solid #eee; padding-bottom: 5px; margin-top: 25px; }}
                .summary {{ 
                    display: flex; 
                    justify-content: space-around; 
                    text-align: center; 
                    padding: 15px; 
                    background-color: #f8f9fa; 
                    border-radius: 8px; 
                    margin: 20px 0;
                }}
                .summary-item {{ flex-grow: 1; }}
                .summary-item h3 {{ margin: 0; font-size: 16px; color: #005a8c; }}
                .summary-item p {{ margin: 5px 0 0 0; font-size: 22px; font-weight: bold; }}
                .styled-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                    font-size: 12px;
                }}
                .styled-table th, .styled-table td {{
                    border: 1px solid #ddd;
                    padding: 8px 10px;
                    text-align: left;
                }}
                .styled-table th {{
                    background-color: #e9ecef;
                    color: #002a4d;
                    font-weight: bold;
                }}
                .footer {{
                    text-align: center; position: fixed; bottom: 0; width: 100%;
                    font-size: 10px; color: #777; border-top: 1px solid #eee; padding-top: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                {f'<img src="{logo_base64}" class="logo">' if logo_base64 else ''}
                <h1>Relatório de Avaliação de Treinamento</h1>
                <p style="font-size: 16px; color: #555; margin-top: 5px;">{training_title}</p>
            </div>
            <h2>Resumo do Desempenho</h2>
            <div class="summary">
                <div class="summary-item"><h3>Total de Participantes</h3><p>{total_colaboradores}</p></div>
                <div class="summary-item"><h3>Aprovados</h3><p style="color: #28a745;">{aprovados}</p></div>
                <div class="summary-item"><h3>Reprovados</h3><p style="color: #dc3545;">{reprovados}</p></div>
                <div class="summary-item"><h3>Taxa de Aprovação</h3><p style="color: #005a8c;">{taxa_aprovacao:.1f}%</p></div>
            </div>
            <h2>Resultados Detalhados</h2>
            {df_html}
            <div class="footer">
                <p>Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | IT: 040.010.060.0999.IT</p>
            </div>
        </body>
    </html>
    """
    return html_string

def generate_pdf(df, logo_url, training_title):
    html_content = create_enhanced_report_html(df, logo_url, training_title)
    pdf_file = io.BytesIO()
    HTML(string=html_content).write_pdf(pdf_file)
    pdf_file.seek(0)
    return pdf_file

# --- Funções de Interface do Streamlit ---

def configurar_pagina():
    st.set_page_config(page_title="Calculadora de Notas VIBRA", page_icon="⚡", layout="wide")

def exibir_cabecalho():
    st.image("https://www.vibraenergia.com.br/wp-content/themes/vibra/static/images/logo-vibra.svg", width=200)
    st.title("Calculadora de Notas de Treinamento")
    st.markdown("Ferramenta para calcular a nota final dos colaboradores com base nos critérios da Instrução de Trabalho `040.010.060.0999.IT`.")

def configurar_barra_lateral():
    st.sidebar.header("⚙️ Configurações do Treinamento")
    training_title = st.sidebar.text_input("Título do Treinamento", "NR-35 Trabalho em Altura (Teórica)")
    total_oportunidades = st.sidebar.number_input("Total de Oportunidades de Interação", min_value=1, value=4, step=1)
    total_check_ins = st.sidebar.number_input("Total de Check-ins no Dia", min_value=1, value=2, step=1)
    start_time = st.sidebar.time_input("Horário de Início do Treinamento", value=time(9, 0))
    training_duration = st.sidebar.number_input("Duração Total (min)", min_value=1, value=240, step=10)
    min_presence = st.sidebar.slider("Mínimo de Presença (%)", min_value=1, max_value=100, value=70, step=1)

    st.sidebar.markdown("---")
    st.sidebar.header("📥 Carregar Lista de Presença (via IA)")
    
    uploaded_file = st.sidebar.file_uploader("Selecione o arquivo de presença (CSV ou PDF)", type=['csv', 'pdf'])
    if uploaded_file is not None:
        processar_arquivo_com_ia(uploaded_file, start_time, training_duration, min_presence)

    st.sidebar.markdown("---")
    if st.sidebar.button("➕ Adicionar Colaborador Manualmente"):
        if 'colaboradores' not in st.session_state:
            st.session_state.colaboradores = []
        st.session_state.colaboradores.append({})
    
    return training_title, total_oportunidades, total_check_ins

def processar_arquivo_com_ia(uploaded_file, start_time, training_duration, min_presence):
    """
    Processa um arquivo (PDF ou CSV) usando a IA para extrair dados de presença.
    """
    try:
        if 'pdf_qa_instance' not in st.session_state:
            st.session_state.pdf_qa_instance = PDFQA()
        pdf_qa = st.session_state.pdf_qa_instance

        extraction_prompt = """
        Your task is to act as an attendance sheet processor.
        From the provided file (which can be a PDF or a text/csv file), do the following:
        1.  Extract the full name of each participant. The column might be 'Full Name' or 'Nome Completo'.
        2.  Extract the timestamp of each action. The column might be 'Timestamp'.
        3.  Extract the action itself. The column might be 'User Action' or 'Action'. The values are typically 'Joined' and 'Left'.
        4.  Return the data as a clean JSON array of objects. Each object must have three keys: "Full Name", "Timestamp", and "Action".
        5.  Ensure the 'Timestamp' is in the format 'MM/DD/YYYY, HH:MM:SS AM/PM'.
        6.  If a participant joins and leaves multiple times, create a separate JSON object for each action.
        7.  Ignore any header rows or summary information in the file that is not part of the main data table.
        8.  If no valid data is found, return an empty JSON array.

        Example of the desired output format:
        [
            {"Full Name": "John Doe", "Timestamp": "07/29/2024, 08:00:00 AM", "Action": "Joined"},
            {"Full Name": "John Doe", "Timestamp": "07/29/2024, 08:30:00 AM", "Action": "Left"},
            {"Full Name": "Jane Smith", "Timestamp": "07/29/2024, 08:05:00 AM", "Action": "Joined"}
        ]
        """
        extracted_data = pdf_qa.extract_structured_data(uploaded_file, extraction_prompt)

        if not extracted_data:
            st.sidebar.warning(f"A IA não encontrou dados de colaborador no arquivo '{uploaded_file.name}'. Verifique o formato do arquivo.")
            return

        df = pd.DataFrame(extracted_data)
        
        if 'Full Name' in df.columns and 'Timestamp' in df.columns and 'Action' in df.columns:
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%m/%d/%Y, %I:%M:%S %p', errors='coerce')
            df.dropna(subset=['Timestamp'], inplace=True) 
            df = df.sort_values(by=['Full Name', 'Timestamp'])

            st.session_state.colaboradores = []
            if not df.empty:
                for name, group in df.groupby('Full Name'):
                    total_duration = timedelta(0)
                    last_join_time = None
                    for _, row in group.iterrows():
                        if row['Action'] == 'Joined':
                            last_join_time = row['Timestamp']
                        elif row['Action'] == 'Left' and last_join_time is not None:
                            total_duration += row['Timestamp'] - last_join_time
                            last_join_time = None
                    if last_join_time is not None:
                        total_duration += df['Timestamp'].max() - last_join_time

                    presence_percentage = (total_duration.total_seconds() / (training_duration * 60)) * 100
                    frequencia_ok = presence_percentage >= min_presence

                    st.session_state.colaboradores.append({
                        'nome': name, 'frequencia': frequencia_ok, 'check_ins_pontuais': 0,
                    })
                st.sidebar.success(f"{len(st.session_state.colaboradores)} colaboradores processados de '{uploaded_file.name}' via IA!")
            else:
                st.sidebar.warning("Nenhum dado válido de colaborador encontrado no arquivo após a filtragem pela IA.")
        else:
            st.sidebar.error(f"A IA não retornou as colunas esperadas. Esperado: 'Full Name', 'Timestamp', 'Action'. Encontrado: {list(df.columns)}")

    except Exception as e:
        st.sidebar.error(f"Erro ao processar o arquivo com a IA: {e}")
        st.sidebar.info("Este processo depende da capacidade da IA de interpretar o documento.")

def desenhar_formulario_colaboradores(total_oportunidades: int, total_check_ins: int):
    st.header("👤 Dados dos Colaboradores")
    if 'colaboradores' not in st.session_state or not st.session_state.colaboradores:
        st.info("Adicione colaboradores manualmente ou carregue uma lista de presença via IA.")
        return

    st.warning("Confira os dados importados e preencha o que falta para cada colaborador.")

    for i, colab in enumerate(st.session_state.colaboradores):
        st.markdown(f"---")
        # Criar uma chave única para o container ou expander, se necessário
        with st.container():
            cols = st.columns([3, 1, 1, 1, 1])
            
            # Use o nome do colaborador como parte da chave para garantir estabilidade
            colab_key_prefix = f"{colab.get('nome', '')}_{i}"

            st.session_state.colaboradores[i]['nome'] = cols[0].text_input(
                f"Nome do Colaborador {i+1}", 
                value=colab.get('nome', ''), 
                key=f"nome_{colab_key_prefix}"
            )
            
            st.session_state.colaboradores[i]['check_ins_pontuais'] = cols[1].number_input(
                "Check-ins Pontuais", 
                min_value=0, max_value=total_check_ins, step=1, 
                key=f"check_ins_{colab_key_prefix}", 
                value=colab.get('check_ins_pontuais', 0)
            )
            
            st.session_state.colaboradores[i]['interacoes'] = cols[2].number_input(
                "Interações Válidas", 
                min_value=0, max_value=total_oportunidades, step=1, 
                key=f"interacoes_{colab_key_prefix}",
                value=colab.get('interacoes', 0)
            )
            
            st.session_state.colaboradores[i]['acertos'] = cols[3].number_input(
                "Acertos na Prova", 
                min_value=0, max_value=10, step=1, 
                key=f"acertos_{colab_key_prefix}",
                value=colab.get('acertos', 0)
            )
            
            st.session_state.colaboradores[i]['frequencia'] = cols[4].checkbox(
                "Frequência OK?", 
                value=colab.get('frequencia', False), 
                key=f"frequencia_{colab_key_prefix}"
            )

def exibir_resultados(dados_processados: list, training_title: str):
    if not dados_processados:
        st.error("Nenhum colaborador com nome preenchido para calcular.")
        return
        
    st.header("🏆 Resultados Finais")
    df_resultados = pd.DataFrame(dados_processados)
    
    def highlight_status(row):
        if row['Status'] == 'Aprovado': return ['background-color: #d4edda'] * len(row)
        elif 'Reprovado' in row['Status']: return ['background-color: #f8d7da'] * len(row)
        return [''] * len(row)

    display_df = df_resultados[["Colaborador", "Nota Pontualidade", "Nota Interação", "Nota Avaliação", "Nota Final", "Status"]]
    st.dataframe(
        display_df.style.apply(highlight_status, axis=1).format({
            "Nota Pontualidade": "{:.2f}", "Nota Interação": "{:.2f}",
            "Nota Avaliação": "{:.2f}", "Nota Final": "{:.2f}",
        }), 
        use_container_width=True
    )

    st.markdown("---")
    logo_url = "https://www.vibraenergia.com.br/wp-content/themes/vibra/static/images/logo-vibra.svg"
    pdf_data = generate_pdf(df_resultados, logo_url, training_title)
    st.download_button(
        label="📄 Baixar Relatório Detalhado em PDF",
        data=pdf_data,
        file_name=f"relatorio_{training_title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf",
    )

def exibir_pdf_qa_interface():
    st.title("🤖 IA de PDF")
    st.markdown("Faça perguntas sobre seus documentos PDF ou extraia dados estruturados.")

    if 'pdf_qa_instance' not in st.session_state:
        st.session_state.pdf_qa_instance = PDFQA()

    pdf_qa = st.session_state.pdf_qa_instance

    st.header("📚 Perguntas e Respostas sobre Documentos")
    uploaded_qa_files = st.file_uploader("Envie um ou mais arquivos (PDF, CSV, TXT) para fazer perguntas", type=["pdf", "csv", "txt"], accept_multiple_files=True, key="qa_pdf_uploader")

    if uploaded_qa_files:
        question = st.text_area("Faça sua pergunta sobre os documentos:", key="pdf_question")
        if st.button("Obter Resposta", key="ask_pdf_button"):
            if question:
                with st.spinner("Buscando resposta..."):
                    answer, duration = pdf_qa.answer_question(uploaded_qa_files, question)
                    if answer:
                        st.subheader("Resposta:")
                        st.write(answer)
                        st.info(f"Tempo de resposta: {duration:.2f} segundos")
            else:
                st.warning("Por favor, digite uma pergunta.")

    st.header("📊 Extração de Dados Estruturados de um Arquivo")
    st.info("Esta função extrai dados específicos de um ÚNICO arquivo (PDF, CSV, etc.) e os retorna em formato JSON.")
    uploaded_extraction_file = st.file_uploader("Envie um ÚNICO arquivo para extração de dados", type=["pdf", "csv", "txt"], key="extraction_pdf_uploader")

    if uploaded_extraction_file:
        extraction_prompt = st.text_area(
            "Descreva os dados que você quer extrair (ex: 'Extraia o nome do cliente, o número da fatura e o valor total como JSON.').",
            key="extraction_prompt"
        )
        if st.button("Extrair Dados", key="extract_data_button"):
            if extraction_prompt:
                extracted_data = pdf_qa.extract_structured_data(uploaded_extraction_file, extraction_prompt)
                if extracted_data:
                    st.subheader("Dados Extraídos (JSON):")
                    st.json(extracted_data)
            else:
                st.warning("Por favor, forneça um prompt para a extração de dados.")
