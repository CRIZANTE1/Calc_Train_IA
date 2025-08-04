import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta

from IA.pdf_qa import PDFQA
from utils.pdf_generator import generate_pdf_report


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
        st.info("Adicione colaboradores manualmente ou carregue uma lista de presença via IA na barra lateral.")
        return

    st.warning("Confira os dados importados e preencha o que falta para cada colaborador.")

    for i, colab in enumerate(st.session_state.colaboradores):
        st.markdown(f"---")
        with st.container():
            cols = st.columns([3, 1, 1, 1, 1])
            colab_key_prefix = f"{colab.get('nome', '')}_{i}"
            st.session_state.colaboradores[i]['nome'] = cols[0].text_input(f"Nome do Colaborador {i+1}", value=colab.get('nome', ''), key=f"nome_{colab_key_prefix}")
            st.session_state.colaboradores[i]['check_ins_pontuais'] = cols[1].number_input("Check-ins Pontuais", min_value=0, max_value=total_check_ins, step=1, key=f"check_ins_{colab_key_prefix}", value=colab.get('check_ins_pontuais', 0))
            st.session_state.colaboradores[i]['interacoes'] = cols[2].number_input("Interações Válidas", min_value=0, max_value=total_oportunidades, step=1, key=f"interacoes_{colab_key_prefix}", value=colab.get('interacoes', 0))
            st.session_state.colaboradores[i]['acertos'] = cols[3].number_input("Acertos na Prova", min_value=0, max_value=10, step=1, key=f"acertos_{colab_key_prefix}", value=colab.get('acertos', 0))
            st.session_state.colaboradores[i]['frequencia'] = cols[4].checkbox("Frequência OK?", value=colab.get('frequencia', False), key=f"frequencia_{colab_key_prefix}")


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
    
    with st.spinner("Gerando relatório em PDF..."):
        pdf_data = generate_pdf_report(df_resultados, logo_url, training_title)
    
    st.download_button(
        label="📄 Baixar Relatório Detalhado em PDF",
        data=pdf_data,
        file_name=f"relatorio_{training_title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf",
    )

# A função exibir_pdf_qa_interface() foi removida.
