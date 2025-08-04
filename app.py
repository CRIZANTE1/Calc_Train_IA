import streamlit as st
from end import calculos
from front import interface

def main():
    """Função principal que executa a aplicação Streamlit."""
    
    interface.configurar_pagina()

    if 'colaboradores' not in st.session_state:
        st.session_state.colaboradores = []

    interface.exibir_cabecalho()
    
    # A barra lateral agora retorna mais configurações
    training_title, total_oportunidades, total_check_ins = interface.configurar_barra_lateral()
    
    # O formulário precisa do total de oportunidades e check-ins
    interface.desenhar_formulario_colaboradores(total_oportunidades, total_check_ins)

    if st.session_state.colaboradores:
        if st.button("📊 Calcular Resultados Finais", type="primary"):
            # A função de cálculo agora precisa do total de check-ins
            dados_processados = calculos.processar_dados_colaboradores(
                st.session_state.colaboradores, 
                total_oportunidades,
                total_check_ins
            )
            # A função de exibição precisa do título do treinamento para o PDF
            interface.exibir_resultados(dados_processados, training_title)
            
    st.caption('Desenvolvido por Cristian Ferreira Carlos, CE9X,+551131038708, cristiancarlos@vibraenergia.com.br')        

if __name__ == "__main__":
    main()
