import google.generativeai as genai
from api_load import load_api
from AI_operations import RateLimiter
import time
import streamlit as st
import re
import json

class PDFQA:
    def __init__(self):
        load_api()
        # CORREÇÃO: Nome do modelo de IA corrigido para um válido.
        self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
        # CORREÇÃO: Instancia o RateLimiter com limites apropriados para o Gemini 1.5 Flash.
        # Os limites gratuitos são 15 RPM e 1,000,000 TPM.
        self.limiter = RateLimiter(rpm_limit=15, tpm_limit=1_000_000)

    def ask_gemini(self, pdf_files, question):
        try:
            inputs = []
            for pdf_file in pdf_files:
                pdf_file.seek(0) # Garante que o ponteiro do arquivo esteja no início
                pdf_bytes = pdf_file.read()
                part = {"mime_type": "application/pdf", "data": pdf_bytes}
                inputs.append(part)
            
            inputs.append({"text": question})
            
            # CORREÇÃO: Usa o limiter para fazer a chamada à API de forma segura.
            # Estima os tokens do prompt. Para uma precisão maior, use model.count_tokens().
            prompt_tokens_estimate = len(question) // 4 

            response = self.limiter.call_api(
                self.model.generate_content,
                inputs,
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

    def extract_structured_data(self, pdf_file, prompt):
        if not pdf_file:
            st.warning("Nenhum arquivo PDF fornecido para extração.")
            return None

        try:
            with st.spinner(f"Analisando '{pdf_file.name}' com IA para extrair dados..."):
                pdf_file.seek(0)
                pdf_bytes = pdf_file.read()

                part_pdf = {"mime_type": "application/pdf", "data": pdf_bytes}
                generation_config = genai.types.GenerationConfig(response_mime_type="application/json")

                # CORREÇÃO: Usa o limiter para fazer a chamada à API de forma segura.
                prompt_tokens_estimate = len(prompt) // 4
                
                response = self.limiter.call_api(
                    self.model.generate_content,
                    [prompt, part_pdf],
                    generation_config=generation_config,
                    prompt_tokens=prompt_tokens_estimate
                )
                
                cleaned_response = self._clean_json_string(response.text)
                extracted_data = json.loads(cleaned_response)
                
                st.success(f"Dados extraídos com sucesso de '{pdf_file.name}'!")
                return extracted_data
                
        except json.JSONDecodeError:
            st.error("Erro na extração: A IA não retornou um JSON válido.")
            # Tentativa de obter o texto da resposta para depuração
            try:
                st.text_area("Resposta recebida da IA (para depuração):", value=response.text, height=150)
            except NameError:
                st.text("Não foi possível obter a resposta da IA.")
            return None
        except Exception as e:
            st.error(f"Ocorreu um erro ao processar o PDF com a IA: {e}")
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
