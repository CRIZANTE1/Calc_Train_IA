import streamlit as st
from end import calculos
from front import interface
from auth.login_ui import show_login_page, show_user_header, show_logout_button

def main():
    """Função principal que executa a aplicação Streamlit."""
    
    interface.configurar_pagina()

    # --- FLUXO DE LOGIN ---
    if not show_login_page():
        st.stop()
    
    show_user_header()
    show_logout_button()
    
    st.sidebar.markdown("---")
    page = st.sidebar.radio(
        "Navegação",
        ["Calculadora de Treinamento", "Administração"],
        key="page_selector"
    )
    
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
                    # Se a validação passar, executa o cálculo
                    st.session_state.dados_processados = calculos.processar_dados_colaboradores(
                        st.session_state.colaboradores, 
                        total_oportunidades,
                        total_check_ins
                    )
                    st.success("Cálculo realizado com sucesso! Veja os resultados abaixo.")
                # Se a validação falhar, a função validar_dados_colaboradores já exibiu o erro.

        if st.session_state.dados_processados is not None:
            interface.exibir_tabela_resultados(st.session_state.dados_processados)
            interface.exibir_botao_pdf(st.session_state.dados_processados, training_title)
    
    elif page == "Administração":
        interface.exibir_pagina_admin()

    st.sidebar.markdown("---")
    st.sidebar.caption(f'Desenvolvido por Cristian Ferreira Carlos\nCE9X,+551131038708\ncristiancarlos@vibraenergia.com.br')

if __name__ == "__main__":
    main()
