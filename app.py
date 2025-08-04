import streamlit as st
from end import calculos
from front import interface

def main():
    """Função principal que executa a aplicação Streamlit."""
    
    interface.configurar_pagina()

    if 'colaboradores' not in st.session_state:
        st.session_state.colaboradores = []
    # Usaremos o session_state para armazenar os resultados após o cálculo
    if 'dados_processados' not in st.session_state:
        st.session_state.dados_processados = None

    interface.exibir_cabecalho()
    
    training_title, total_oportunidades, total_check_ins = interface.configurar_barra_lateral()
    
    interface.desenhar_formulario_colaboradores(total_oportunidades, total_check_ins)

    if st.session_state.colaboradores:
        # BOTÃO 1: Apenas calcula e armazena os resultados no session_state
        if st.button("📊 Calcular Resultados Finais", type="primary"):
            st.session_state.dados_processados = calculos.processar_dados_colaboradores(
                st.session_state.colaboradores, 
                total_oportunidades,
                total_check_ins
            )

    if st.session_state.dados_processados is not None:
        # Exibe a tabela de resultados na tela
        interface.exibir_tabela_resultados(st.session_state.dados_processados)
        # Exibe um BOTÃO 2, separado, para gerar e baixar o relatório em PDF
        interface.exibir_botao_pdf(st.session_state.dados_processados, training_title)
            
    st.caption('Desenvolvido por Cristian Ferreira Carlos, CE9X,+551131038708, cristiancarlos@vibraenergia.com.br')        

if __name__ == "__main__":
    main()
