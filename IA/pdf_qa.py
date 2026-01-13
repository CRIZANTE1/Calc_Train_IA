from google import genai
from google.genai import types
from .api_load import load_api
from .AI_operations import RateLimiter
import time
import streamlit as st
import re
import json

class PDFQA:
    def __init__(self):
        # Agora self.client é a instância do genai.Client
        self.client = load_api()
        # Atualize o nome do modelo conforme necessário (ex: gemini-2.0-flash ou 1.5-flash)
        self.model_name = 'gemini-1.5-flash' 
        self.limiter = RateLimiter(rpm_limit=15, tpm_limit=1_000_000)

    def ask_gemini(self, pdf_files, question):
        try:
            contents = []
            for pdf_file in pdf_files:
                pdf_file.seek(0) # Garante que o ponteiro do arquivo esteja no início
                pdf_bytes = pdf_file.read()
                
                # Nova forma de passar arquivos binários (SDK v1.0+)
                part = types.Part.from_bytes(
                    data=pdf_bytes, 
                    mime_type="application/pdf"
                )
                contents.append(part)
            
            # Adiciona a pergunta (texto)
            contents.append(question)
            
            prompt_tokens_estimate = len(question) // 4 

            # Chamada atualizada para client.models.generate_content
            response = self.limiter.call_api(
                self.client.models.generate_content,
                model=self.model_name,
                contents=contents,
                prompt_tokens=prompt_tokens_estimate
            )

            return response.text
            
        except Exception as e:
            st.error(f"Erro ao obter resposta do modelo Gemini: {str(e)}")
            return None

    def _clean_json_string(self, text):
        match = re.search(r'```(?:json)?\s*({.*?}|\[.*?\])\s*```', text, re.DOTALL)
        if match:
            return match.group(1)
        return text.strip()

    def extract_structured_data(self, uploaded_file, prompt, csv_data=None):
        """
        Extrai dados estruturados de um arquivo (PDF, CSV, etc.) usando a IA.
        """
        if not uploaded_file and not csv_data:
            st.warning("Nenhum arquivo fornecido para extração.")
            return None

        try:
            with st.spinner(f"Analisando com IA para extrair dados..."):
                contents = [prompt]

                if csv_data:
                    file_bytes = csv_data.encode('utf-8')
                    mime_type = 'text/csv'
                else:
                    # Garantir que o arquivo está no início
                    uploaded_file.seek(0)
                    file_bytes = uploaded_file.read()
                    mime_type = uploaded_file.type
                    
                    st.info(f"Arquivo carregado: {len(file_bytes)} bytes")

                # Criar a parte do arquivo usando a nova SDK
                file_part = types.Part.from_bytes(
                    data=file_bytes,
                    mime_type=mime_type
                )
                contents.append(file_part)
                
                # Configuração atualizada para JSON mode
                config = types.GenerateContentConfig(
                    response_mime_type="application/json"
                )

                prompt_tokens_estimate = len(prompt) // 4
                
                response = self.limiter.call_api(
                    self.client.models.generate_content,
                    model=self.model_name,
                    contents=contents,
                    config=config,
                    prompt_tokens=prompt_tokens_estimate
                )
                
                if response and response.text:
                    cleaned_response = self._clean_json_string(response.text)
                    extracted_data = json.loads(cleaned_response)
                    
                    st.success(f"Dados extraídos com sucesso de '{uploaded_file.name if uploaded_file else 'CSV'}'!")
                    return extracted_data
                else:
                    st.error("A IA não retornou uma resposta válida. A resposta estava vazia.")
                    return None
                
        except json.JSONDecodeError:
            st.error("Erro na extração: A IA não retornou um JSON válido. Verifique o documento ou o prompt.")
            if 'response' in locals() and hasattr(response, 'text'):
                st.text_area("Resposta recebida da IA (para depuração):", value=response.text, height=150)
            return None
        except Exception as e:
            st.error(f"Ocorreu um erro ao processar o arquivo com a IA: {e}")
            if 'response' in locals() and hasattr(response, 'text'):
                st.text_area("Resposta recebida da IA (para depuração):", value=response.text, height=150)
            return None

    def answer_question(self, pdf_files, question):
        start_time = time.time()
        try:
            answer = self.ask_gemini(pdf_files, question)
            duration = time.time() - start_time
            if answer:
                return answer, duration
            else:
                st.error("Não foi possível obter uma resposta do modelo.")
                return None, duration
        except Exception as e:
            st.error(f"Erro inesperado ao processar a pergunta: {str(e)}")
            return None, 0
