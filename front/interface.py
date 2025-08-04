import streamlit as st
import pandas as pd
from end.calculos import processar_dados_colaboradores
import io
import csv
import requests
import base64
from weasyprint import HTML
from datetime import datetime, time, timedelta

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
    st.sidebar.header("📥 Carregar Lista de Presença")
    uploaded_file = st.sidebar.file_uploader("Selecione o arquivo CSV do Teams", type=['csv'])
    if uploaded_file is not None:
        processar_arquivo_csv(uploaded_file, start_time, training_duration, min_presence)

    st.sidebar.markdown("---")
    if st.sidebar.button("➕ Adicionar Colaborador Manualmente"):
        if 'colaboradores' not in st.session_state:
            st.session_state.colaboradores = []
        st.session_state.colaboradores.append({})
    
    return training_title, total_oportunidades, total_check_ins

def processar_arquivo_csv(uploaded_file, start_time, training_duration, min_presence):
    try:
        content_as_string = uploaded_file.getvalue().decode('utf-16')
        lines = content_as_string.splitlines()

        header_row_index = -1
        # Itera pelas linhas para encontrar o cabeçalho real
        for i, line in enumerate(lines):
            # Critérios para identificar a linha de cabeçalho
            if 'Full Name' in line or 'Nome Completo' in line or 'Timestamp' in line or 'User Action' in line:
                header_row_index = i
                break
        
        if header_row_index == -1:
            st.sidebar.error("Cabeçalho do CSV não encontrado. Verifique o arquivo.")
            return

        # Use o conteúdo do CSV a partir da linha de cabeçalho
        csv_content_from_header = "\n".join(lines[header_row_index:])
        csv_file_like_object = io.StringIO(csv_content_from_header)

        # Detecta o dialeto e lê o CSV
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(lines[header_row_index])
        df = pd.read_csv(csv_file_like_object, sep=dialect.delimiter)

        # O resto do processamento continua aqui...
        df.columns = df.columns.str.strip()

        column_mapping = {
            'Nome Completo': 'Full Name',
            'Timestamp': 'Timestamp',
            'User Action': 'Action',
            'Action': 'Action'
        }
        # Remove 'Full Name' do mapeamento se já existir para evitar problemas
        if 'Full Name' in df.columns:
            column_mapping.pop('Full Name', None)

        df.rename(columns=column_mapping, inplace=True)

        if 'Full Name' in df.columns and 'Timestamp' in df.columns and 'Action' in df.columns:
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%m/%d/%Y, %I:%M:%S %p')
            df = df.sort_values(by=['Full Name', 'Timestamp'])

            st.session_state.colaboradores = []
            training_start_datetime = datetime.combine(df['Timestamp'].iloc[0].date(), start_time)

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
                    # Se a pessoa entrou e não saiu, considera que ficou até o final da gravação
                    total_duration += df['Timestamp'].max() - last_join_time

                presence_percentage = (total_duration.total_seconds() / (training_duration * 60)) * 100
                frequencia_ok = presence_percentage >= min_presence

                st.session_state.colaboradores.append({
                    'nome': name,
                    'frequencia': frequencia_ok,
                    'check_ins_pontuais': 0,
                })
            st.sidebar.success(f"{len(st.session_state.colaboradores)} colaboradores processados!")
        else:
            st.sidebar.error(f"Colunas necessárias não encontradas. Esperado: 'Full Name', 'Timestamp', 'Action'. Encontrado: {list(df.columns)}")

    except Exception as e:
        st.sidebar.error(f"Erro ao processar o arquivo: {e}")

def desenhar_formulario_colaboradores(total_oportunidades: int, total_check_ins: int):
    st.header("👤 Dados dos Colaboradores")
    if 'colaboradores' not in st.session_state or not st.session_state.colaboradores:
        st.info("Adicione colaboradores manualmente ou carregue uma lista de presença.")
        return

    st.warning("Preencha os dados restantes para cada colaborador.")

    for i, colab in enumerate(st.session_state.colaboradores):
        st.markdown(f"---")
        cols = st.columns([3, 1, 1, 1, 1])
        
        cols[0].text_input(f"Nome do Colaborador {i+1}", value=colab.get('nome', ''), key=f"nome_{i}", disabled=True)
        st.session_state.colaboradores[i]['nome'] = colab.get('nome', '')

        st.session_state.colaboradores[i]['check_ins_pontuais'] = cols[1].number_input("Check-ins Pontuais", min_value=0, max_value=total_check_ins, step=1, key=f"check_ins_{i}", value=colab.get('check_ins_pontuais', 0))
        st.session_state.colaboradores[i]['interacoes'] = cols[2].number_input("Interações Válidas", min_value=0, max_value=total_oportunidades, step=1, key=f"interacoes_{i}")
        st.session_state.colaboradores[i]['acertos'] = cols[3].number_input("Acertos na Prova", min_value=0, max_value=10, step=1, key=f"acertos_{i}")
        cols[4].checkbox("Frequência OK?", value=colab.get('frequencia', False), key=f"frequencia_{i}", disabled=True)
        st.session_state.colaboradores[i]['frequencia'] = colab.get('frequencia', False)

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

    # Selecionar e formatar colunas para exibição na tela
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
