# --- START OF FILE front/interface.py ---

import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta
import time as py_time # Importa o módulo time com um alias para evitar conflitos

# Importações dos pacotes do projeto
from IA.pdf_qa import PDFQA
from utils.pdf_generator import generate_pdf_report
from auth import auth_utils

# --- Funções de Interface do Streamlit ---

def configurar_pagina():
    """Configura as propriedades da página Streamlit."""
    st.set_page_config(page_title="Calculadora de Notas VIBRA", page_icon="⚡", layout="wide")

def exibir_cabecalho():
    """Exibe o logo e o título principal da aplicação."""
    st.image("https://www.movenews.com.br/wp-content/uploads/2022/11/handler.png", width=200)
    st.title("Calculadora de Notas de Treinamento")
    st.markdown("Ferramenta para calcular a nota final dos colaboradores com base nos critérios da Instrução de Trabalho `040.010.060.0999.IT`.")

def configurar_barra_lateral():
    """Cria e gerencia todos os widgets da barra lateral."""
    st.sidebar.header("⚙️ Configurações do Treinamento")
    training_title = st.sidebar.text_input("Título do Treinamento", "NR-35 Trabalho em Altura (Teórica)")
    total_oportunidades = st.sidebar.number_input("Total de Oportunidades de Interação", min_value=1, value=4, step=1)
    total_check_ins = st.sidebar.number_input("Total de Check-ins no Dia", min_value=1, value=2, step=1)
    start_time = st.sidebar.time_input("Horário de Início do Treinamento", value=time(9, 0))
    training_duration = st.sidebar.number_input("Duração Total (min)", min_value=1, value=240, step=10)
    min_presence = st.sidebar.slider("Mínimo de Presença (%)", min_value=1, max_value=100, value=60, step=1)

    st.sidebar.markdown("---")
    st.sidebar.header("📥 Carregar Lista de Presença")
    
    uploaded_file = st.sidebar.file_uploader("1. Selecione o arquivo (CSV ou PDF)", type=['csv', 'pdf'])
    
    if 'last_ia_call_time' not in st.session_state:
        st.session_state.last_ia_call_time = 0

    cooldown_seconds = 120
    time_since_last_call = py_time.time() - st.session_state.last_ia_call_time
    
    if time_since_last_call < cooldown_seconds:
        remaining_time = int(cooldown_seconds - time_since_last_call)
        st.sidebar.warning(f"Aguarde {remaining_time} segundos para usar a IA novamente.")
        st.sidebar.button("2. Processar Arquivo com IA", disabled=True)
    elif uploaded_file is not None:
        if st.sidebar.button("2. Processar Arquivo com IA"):
            # Passando os valores padrão para a função de processamento
            processar_arquivo_com_ia(uploaded_file, start_time, training_duration, min_presence, total_check_ins, total_oportunidades)
            st.session_state.dados_processados = None
    else:
        st.sidebar.button("2. Processar Arquivo com IA", disabled=True)

    st.sidebar.markdown("---")
    if st.sidebar.button("➕ Adicionar Colaborador Manualmente"):
        if 'colaboradores' not in st.session_state:
            st.session_state.colaboradores = []
        
        # Cria o dicionário já com os valores padrão
        novo_colaborador = {
            'check_ins_pontuais': total_check_ins,
            'interacoes': total_oportunidades,
            'acertos': 7
        }
        st.session_state.colaboradores.append(novo_colaborador)
        st.session_state.dados_processados = None
    
    return training_title, total_oportunidades, total_check_ins

def processar_arquivo_com_ia(uploaded_file, start_time, training_duration, min_presence, total_check_ins, total_oportunidades):
    """Processa um arquivo (PDF ou CSV) e preenche os colaboradores com valores padrão."""
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
        """
        
        with st.spinner("A IA está analisando o arquivo..."):
            extracted_data = pdf_qa.extract_structured_data(uploaded_file, extraction_prompt)

        st.session_state.last_ia_call_time = py_time.time()

        if not extracted_data:
            st.sidebar.warning(f"A IA não encontrou dados de colaborador no arquivo '{uploaded_file.name}'.")
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
                        'nome': name, 
                        'frequencia': frequencia_ok,
                        'check_ins_pontuais': total_check_ins,
                        'interacoes': total_oportunidades,
                        'acertos': 7
                    })
                st.sidebar.success(f"{len(st.session_state.colaboradores)} colaboradores processados via IA!")
            else:
                st.sidebar.warning("Nenhum dado válido de colaborador encontrado no arquivo após a filtragem pela IA.")
        else:
            st.sidebar.error(f"A IA não retornou as colunas esperadas. Esperado: 'Full Name', 'Timestamp', 'Action'. Encontrado: {list(df.columns)}")
    except Exception as e:
        st.sidebar.error(f"Erro ao processar com a IA: {e}")

def desenhar_formulario_colaboradores(total_oportunidades: int, total_check_ins: int):
    """Desenha a área principal com o formulário para cada colaborador."""
    st.header("👤 Dados dos Colaboradores")
    if not st.session_state.get('colaboradores'):
        st.info("Adicione colaboradores manualmente ou carregue uma lista de presença na barra lateral.")
        return

    st.warning("Confira os dados. A maioria dos campos já está preenchida com valores padrão. Altere apenas o necessário.")

    def on_change_callback():
        """Callback para limpar os resultados calculados sempre que um dado do formulário for alterado."""
        st.session_state.dados_processados = None

    for i, colab in enumerate(st.session_state.colaboradores):
        st.markdown(f"---")
        with st.container():
            cols = st.columns([3, 1, 1, 1, 1])
            colab_key_prefix = f"{colab.get('nome', '')}_{i}"
            
            st.session_state.colaboradores[i]['nome'] = cols[0].text_input(f"Nome do Colaborador {i+1}", value=colab.get('nome', ''), key=f"nome_{colab_key_prefix}", on_change=on_change_callback, placeholder="Nome completo do colaborador")
            st.session_state.colaboradores[i]['check_ins_pontuais'] = cols[1].number_input("Check-ins Pontuais", min_value=0, max_value=total_check_ins, step=1, key=f"check_ins_{colab_key_prefix}", value=colab.get('check_ins_pontuais'), on_change=on_change_callback)
            st.session_state.colaboradores[i]['interacoes'] = cols[2].number_input("Interações Válidas", min_value=0, max_value=total_oportunidades, step=1, key=f"interacoes_{colab_key_prefix}", value=colab.get('interacoes'), on_change=on_change_callback)
            st.session_state.colaboradores[i]['acertos'] = cols[3].number_input("Acertos na Prova", min_value=0, max_value=10, step=1, key=f"acertos_{colab_key_prefix}", value=colab.get('acertos'), on_change=on_change_callback)
            st.session_state.colaboradores[i]['frequencia'] = cols[4].checkbox("Frequência OK?", value=colab.get('frequencia', False), key=f"frequencia_{colab_key_prefix}", on_change=on_change_callback)

def validar_dados_colaboradores() -> bool:
    """Verifica se todos os campos obrigatórios para cada colaborador foram preenchidos."""
    if not st.session_state.get('colaboradores'):
        st.error("Não há colaboradores na lista para validar.")
        return False

    dados_incompletos = []
    for i, colab in enumerate(st.session_state.colaboradores):
        nome = colab.get('nome', '').strip()
        check_ins = colab.get('check_ins_pontuais')
        interacoes = colab.get('interacoes')
        acertos = colab.get('acertos')

        if not nome or check_ins is None or interacoes is None or acertos is None:
            dados_incompletos.append(f"Colaborador {i+1} (Nome: {nome or 'Vazio'})")
    
    if dados_incompletos:
        st.error("**Dados Incompletos!** Por favor, preencha todos os campos para os seguintes colaboradores antes de calcular:")
        for item in dados_incompletos:
            st.warning(f"- {item}")
        return False
        
    return True

def exibir_tabela_resultados(dados_processados: list):
    """Mostra o DataFrame com os resultados na tela."""
    if not dados_processados:
        st.error("Nenhum dado para exibir.")
        return
        
    st.header("🏆 Resultados Finais")
    df_resultados = pd.DataFrame(dados_processados)
    
    def highlight_status(row):
        if row['Status'] == 'Aprovado': return ['background-color: #d4edda'] * len(row)
        elif 'Reprovado' in row['Status']: return ['background-color: #f8d7da'] * len(row)
        return [''] * len(row)

    display_df = df_resultados[["Colaborador", "Nota Pontualidade", "Nota Interação", "Nota Avaliação", "Nota Final", "Status"]]
    st.dataframe(display_df.style.apply(highlight_status, axis=1).format({ "Nota Pontualidade": "{:.2f}", "Nota Interação": "{:.2f}", "Nota Avaliação": "{:.2f}", "Nota Final": "{:.2f}", }), use_container_width=True)

def exibir_botao_pdf(dados_processados: list, training_title: str):
    """Mostra o botão para gerar e baixar o relatório em PDF."""
    st.markdown("---")
    
    df_resultados = pd.DataFrame(dados_processados)
    logo_url = "https://drive.google.com/uc?export=download&id=1AABdw4iGBJ7tsQ7fR1WGTP5cML3Jlfx_"
    
    with st.spinner("Preparando dados do relatório..."):
        pdf_data = generate_pdf_report(df_resultados, logo_url, training_title)
    
    st.download_button(label="📄 Baixar Relatório Detalhado em PDF", data=pdf_data, file_name=f"relatorio_{training_title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf", mime="application/pdf")

def exibir_pagina_admin():
    """Desenha a interface da página de administração."""
    auth_utils.check_admin_permission()
    
    st.header("⚙️ Painel de Administração")
    st.info("Esta área é restrita para administradores do sistema.")
    
    tab1, tab2 = st.tabs(["Gerenciar Usuários", "Outras Configurações"])
    
    with tab1:
        st.subheader("Usuários Autorizados")
        st.markdown("A lista abaixo é carregada diretamente do arquivo de segredos (`secrets.toml`) da aplicação. Para adicionar, remover ou alterar permissões, você deve editar este arquivo e reiniciar a aplicação.")
        try:
            users_df = auth_utils.get_users_for_display()
            st.dataframe(users_df, use_container_width=True)
        except Exception as e:
            st.error(f"Não foi possível carregar a lista de usuários: {e}")

    with tab2:
        st.subheader("Configurações Futuras")
        st.write("Esta área pode ser usada para outras configurações do sistema.")
        if st.button("Limpar Cache de Dados"):
            st.cache_data.clear()
            st.success("O cache de dados foi limpo com sucesso!")
