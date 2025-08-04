import streamlit as st
from .auth_utils import get_user_display_name, is_user_authorized

def show_login_page() -> bool:
    """
    Gerencia a exibição da página de login.
    Retorna True se o usuário está logado e autorizado, False caso contrário.
    """
    # Verifica se o usuário já está logado com o provedor OIDC
    if not hasattr(st.user, "is_logged_in") or not st.user.is_logged_in:
        st.markdown("### Acesso à Calculadora de Treinamento")
        st.write("Por favor, faça login para continuar.")
        
        if st.button("Fazer Login com a Conta Corporativa", type="primary"):
            st.login()
        return False # Usuário não está logado

    # Se está logado, verifica se está na lista de autorizados do secrets.toml
    if not is_user_authorized():
        st.warning(f"Acesso Negado para **{get_user_display_name()}**.")
        st.error("Seu e-mail não está na lista de usuários autorizados. Por favor, contate o administrador do sistema.")
        show_logout_button(location="main") # Oferece logout na página principal
        return False # Usuário logado, mas não autorizado

    # Se chegou aqui, o usuário está logado E autorizado.
    return True

def show_user_header():
    """Mostra o cabeçalho de boas-vindas na barra lateral."""
    with st.sidebar:
        st.markdown("---")
        st.write(f"Bem-vindo(a),")
        st.markdown(f"**{get_user_display_name()}**")

def show_logout_button(location="sidebar"):
    """Mostra o botão de logout na barra lateral (padrão) ou no corpo principal."""
    if location == "sidebar":
        container = st.sidebar
    else:
        container = st.container()

    with container:
        if st.button("Sair do Sistema"):
            st.logout()
