import streamlit as st
from end import calculos
from front import interface

def main():
    """Função principal que executa a aplicação Streamlit."""
    
    interface.configurar_pagina()


    # Inicializa o session_state se necessário
    if 'colaboradores' not in st.session_state:
        st.session_state.colaboradores = []

    # Exibe o cabeçalho padrão da página
    interface.exibir_cabecalho()
    
    # A barra lateral configura os parâmetros do treinamento
    training_title, total_oportunidades, total_check_ins = interface.configurar_barra_lateral()
    
    # O formulário principal para inserir dados dos colaboradores
    interface.desenhar_formulario_colaboradores(total_oportunidades, total_check_ins)

    # Se houver colaboradores na lista, exibe o botão de cálculo
    if st.session_state.colaboradores:
        if st.button("📊 Calcular Resultados Finais", type="primary"):
            # Processa os dados inseridos
            dados_processados = calculos.processar_dados_colaboradores(
                st.session_state.colaboradores, 
                total_oportunidades,
                total_check_ins
            )
            # Exibe os resultados e o botão de download do PDF
            interface.exibir_resultados(dados_processados, training_title)
            
    st.caption('Desenvolvido por Cristian Ferreira Carlos, CE9X,+551131038708, cristiancarlos@vibraenergia.com.br')        

if __name__ == "__main__":
    main()

