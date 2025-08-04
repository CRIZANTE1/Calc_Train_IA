
import streamlit as st

@st.cache_data(ttl=300) # Cache por 5 minutos
def get_authorized_users() -> list:
    """Carrega a lista de usuários autorizados do st.secrets, convertendo para tipos Python puros."""
    try:
        if "users" in st.secrets and "credentials" in st.secrets.users:
         
            return [dict(user) for user in st.secrets.users.credentials]
            
        return []
    except Exception as e:
        # Adiciona um log de erro para depuração, caso o problema seja outro
        st.error(f"Erro inesperado ao carregar segredos dos usuários: {e}")
        return []

def get_user_info(email: str) -> dict | None:
    """Busca informações de um usuário na lista de autorizados pelo e-mail."""
    if not email:
        return None
    
    authorized_users = get_authorized_users()
    email_lower = email.lower()

    for user in authorized_users:
        if user.get("email", "").lower() == email_lower:
            return user
    return None

def is_user_authorized() -> bool:
    """Verifica se o usuário logado via st.user está na lista de autorizados."""
    if not hasattr(st.user, "email"):
        return False
        
    user_info = get_user_info(st.user.email)
    return user_info is not None

def get_user_role() -> str:
    """Retorna a role ('admin' ou 'user') do usuário logado."""
    if not hasattr(st.user, "email"):
        return "user" # Padrão seguro
        
    user_info = get_user_info(st.user.email)
    return user_info.get("role", "user") if user_info else "user"

def get_user_display_name() -> str:
    """Retorna o nome de exibição do usuário logado."""
    if not hasattr(st.user, "email"):
        return "Visitante"
        
    user_info = get_user_info(st.user.email)
    # Prioriza o nome do secrets, senão o nome do st.user, e por último o e-mail
    if user_info and user_info.get("name"):
        return user_info["name"]
    
    return getattr(st.user, "name", st.user.email)

def is_admin() -> bool:
    """Verifica se o usuário logado tem a role de 'admin'."""
    return get_user_role() == "admin"

def check_admin_permission():
    """Verifica se o usuário é admin e exibe uma mensagem de erro caso contrário."""
    if not is_admin():
        st.error("Acesso Negado. Você não tem permissão de administrador para realizar esta ação.")
        st.stop()
