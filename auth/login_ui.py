import streamlit as st
import pandas as pd


@st.cache_data(ttl=300)
def get_authorized_users() -> list:
    """Carrega a lista de usuários autorizados do st.secrets."""
    try:
        if "users" in st.secrets and "credentials" in st.secrets.users:
            return [dict(user) for user in st.secrets.users.credentials]
        return []
    except Exception as e:
        st.error(f"Erro ao carregar os segredos dos usuários: {e}")
        return []

def get_user_info(email: str) -> dict | None:
    """Busca as informações de um usuário pelo e-mail (case-insensitive)."""
    if not email: return None
    authorized_users = get_authorized_users()
    email_lower = email.lower()
    for user in authorized_users:
        if user.get("email", "").lower() == email_lower:
            return user
    return None

def is_user_authorized() -> bool:
    """Verifica se o usuário está logado E na lista de autorizados."""
    if hasattr(st, "user") and hasattr(st.user, "email") and st.user.email:
        return get_user_info(st.user.email) is not None
    return False

def get_user_display_name() -> str:
    """Retorna o nome de exibição do usuário."""
    if hasattr(st, "user") and hasattr(st.user, "email") and st.user.email:
        user_info = get_user_info(st.user.email)
        if user_info and user_info.get("name"):
            return user_info["name"]
        return getattr(st.user, "name", st.user.email)
    return "Visitante"

def get_user_email() -> str | None:
    """Retorna o e-mail do usuário logado."""
    if hasattr(st, "user") and hasattr(st.user, "email") and st.user.email:
        return st.user.email
    return None


def show_login_page() -> bool:
    """
    Gerencia a exibição da página de login.
    Retorna True se o usuário está logado e autorizado, False caso contrário.
    """
    if not hasattr(st, "user") or not hasattr(st.user, "is_logged_in") or not st.user.is_logged_in:
        st.markdown("### Acesso à Calculadora de Brigada")
        st.write("Por favor, faça login para continuar.")
        
        if st.button("Fazer Login", type="primary"):
            st.login()
        return False

    if not is_user_authorized():
        st.warning(f"Acesso Negado para **{get_user_display_name()}**.")
        st.error("Seu e-mail não está na lista de usuários autorizados. Contate o administrador.")
        show_logout_button(location="main")
        return False

    return True

def show_user_header():
    """Mostra o cabeçalho de boas-vindas na barra lateral."""
    with st.sidebar:
        st.markdown("---")
        st.write(f"Bem-vindo(a),")
        st.markdown(f"**{get_user_display_name()}**")

def show_logout_button(location="sidebar"):
    """Mostra o botão de logout."""
    container = st.sidebar if location == "sidebar" else st.container()
    if container.button("Sair do Sistema"):
        st.logout()
