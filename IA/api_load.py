import os
from google import genai
import streamlit as st
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_api():
    try:
        # Tentar carregar a chave API de múltiplas fontes
        api_key = None
        
        # 1. Tentar carregar de Streamlit secrets (produção)
        try:
            api_key = st.secrets["general"]["GOOGLE_API_KEY"]
            logging.info("API key loaded from Streamlit secrets.")
        except (KeyError, TypeError, AttributeError):
            logging.info("API key not found in Streamlit secrets, trying environment variables.")
        
        # 2. Se não encontrou nos secrets, tentar carregar do arquivo .env
        if not api_key:
            api_key = os.getenv('GOOGLE_API_KEY')
            if api_key:
                logging.info("API key loaded from .env file.")

        # 3. Verificar se uma chave foi encontrada
        if not api_key:
            error_msg = "Google API key not found. Please set the GOOGLE_API_KEY environment variable or in Streamlit secrets."
            logging.error(error_msg)
            st.error(error_msg)
            return None

        # Instanciar o Cliente da nova SDK
        client = genai.Client(api_key=api_key)
        logging.info("API Client loaded successfully.")
        return client

    except Exception as e:
        error_msg = f"Error loading API: {str(e)}"
        logging.exception(error_msg)
        st.error(error_msg)
        return None
