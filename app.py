import streamlit as st
from end import calculos
from front import interface

def main():
    """Função principal que executa a aplicação Streamlit."""
    
    interface.configurar_pagina()

    page = st.sidebar.radio("Navegação", ["Calculadora de Treinamento", "IA de PDF"])

    if page == "Calculadora de Treinamento":
        if 'colaboradores' not in st.session_state:
            st.session_state.colaboradores = []

        interface.exibir_cabecalho()
        
        training_title, total_oportunidades, total_check_ins = interface.configurar_barra_lateral()
        
        interface.desenhar_formulario_colaboradores(total_oportunidades, total_check_ins)

        if st.session_state.colaboradores:
            if st.button("📊 Calcular Resultados Finais", type="primary"):
                dados_processados = calculos.processar_dados_colaboradores(
                    st.session_state.colaboradores, 
                    total_oportunidades,
                    total_check_ins
                )
                interface.exibir_resultados(dados_processados, training_title)
                
        st.caption('Desenvolvido por Cristian Ferreira Carlos, CE9X,+551131038708, cristiancarlos@vibraenergia.com.br')        

    elif page == "IA de PDF":
        interface.exibir_pdf_qa_interface()        

if __name__ == "__main__":
    main()
