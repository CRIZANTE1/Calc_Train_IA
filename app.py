
import streamlit as st

# Importações de outros módulos
from utils.google_sheets_handler import GoogleSheetsHandler
from IA.ai_operations import AIOperations
from about import show_about_page
from pages import calculator_page

from auth.login_ui import (
    show_login_page,
    show_user_header,
    show_logout_button,
    get_user_email  # Garante que get_user_email também venha daqui
)


st.set_page_config(page_title="Cálculo de Brigadistas", page_icon="🔥", layout="wide")

@st.cache_resource
def initialize_services():
    """Inicializa e retorna os handlers de serviços (Sheets, IA)."""
    handler = GoogleSheetsHandler()
    ai_operator = AIOperations()
    return handler, ai_operator

def main():
    """
    Função principal que orquestra o aplicativo.
    """
    # A função show_login_page, importada de login_ui, controla todo o acesso.
    if not show_login_page():
        return

    # Se o fluxo continuar, o usuário está autorizado.
    show_user_header() # Função importada de login_ui
    show_logout_button() # Função importada de login_ui

    handler, ai_operator = initialize_services()

    st.sidebar.title("Navegação")
    page_options = {
        "Cálculo de Brigadistas": calculator_page.show_page,
        "Sobre": show_about_page
    }
    selected_page_name = st.sidebar.radio("Selecione uma página", page_options.keys())
    
    selected_page_function = page_options[selected_page_name]
    
    if selected_page_name == "Cálculo de Brigadistas":
        user_email = get_user_email() # Função importada de login_ui
        # Passa o e-mail para a página da calculadora
        selected_page_function(handler, ai_operator, user_email)
    else:
        selected_page_function()

if __name__ == "__main__":
    main()
