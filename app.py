import streamlit as st
from utils.google_sheets_handler import GoogleSheetsHandler
from IA.ai_operations import AIOperations
from about import show_about_page
# Esta importação agora funcionará, pois a pasta 'auth' será reconhecida como um pacote
from auth.login_page import show_login_page, show_logout_button
from auth.auth_utils import get_user_display_name, get_user_email 
from pages import calculator_page

def main():
    """Função principal que executa a aplicação Streamlit."""
    
    interface.configurar_pagina()

    # --- FLUXO DE LOGIN ---
    if not show_login_page():
        st.stop()
    
    show_user_header()
    show_logout_button()
    
    # --- NAVEGAÇÃO ENTRE PÁGINAS ---
    st.sidebar.markdown("---")
    # Adicionando a nova página à lista de opções
    page_options = ["Calculadora de Treinamento", "Administração", "Ajuda e Demonstração"]
    page = st.sidebar.radio(
        "Navegação",
        page_options,
        key="page_selector"
    )
    
    # --- ROTEAMENTO DAS PÁGINAS ---
    if page == "Calculadora de Treinamento":
        if 'colaboradores' not in st.session_state:
            st.session_state.colaboradores = []
        if 'dados_processados' not in st.session_state:
            st.session_state.dados_processados = None

        interface.exibir_cabecalho()
        training_title, total_oportunidades, total_check_ins = interface.configurar_barra_lateral()
        interface.desenhar_formulario_colaboradores(total_oportunidades, total_check_ins)

        if st.session_state.colaboradores:
            if st.button("📊 Calcular Resultados Finais", type="primary"):
                if interface.validar_dados_colaboradores():
                    st.session_state.dados_processados = calculos.processar_dados_colaboradores(
                        st.session_state.colaboradores, 
                        total_oportunidades,
                        total_check_ins
                    )
                    st.success("Cálculo realizado com sucesso! Veja os resultados abaixo.")

        if st.session_state.dados_processados is not None:
            interface.exibir_tabela_resultados(st.session_state.dados_processados)
            interface.exibir_botao_pdf(st.session_state.dados_processados, training_title)
    
    elif page == "Administração":
        interface.exibir_pagina_admin()

    elif page == "Ajuda e Demonstração":
        # Chama a nova função que desenha a página de ajuda
        interface.exibir_pagina_ajuda()

    st.sidebar.markdown("---")
    st.sidebar.caption(f'Desenvolvido por Cristian Ferreira Carlos\nCE9X,+551131038708\ncristiancarlos@vibraenergia.com.br')

if __name__ == "__main__":
    main()
