import time
import collections
import logging

# Configuração do logging para o RateLimiter
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RateLimiter:
    """
    Gerencia e impõe limites de taxa para chamadas de API de IA (RPM e TPM).
    """
    def __init__(self, rpm_limit: int, tpm_limit: int):
        self.rpm_limit = rpm_limit
        self.tpm_limit = tpm_limit
        self.request_timestamps = collections.deque()
        self.token_usage = collections.deque()

    def _cleanup_old_requests(self):
        current_time = time.time()
        while self.request_timestamps and self.request_timestamps[0] <= current_time - 60:
            self.request_timestamps.popleft()

    def _cleanup_old_tokens(self):
        current_time = time.time()
        while self.token_usage and self.token_usage[0][0] <= current_time - 60:
            self.token_usage.popleft()

    def wait_for_rpm_slot(self):
        self._cleanup_old_requests()
        if len(self.request_timestamps) >= self.rpm_limit:
            time_to_wait = self.request_timestamps[0] - (time.time() - 60) + 0.1 # Adiciona margem
            if time_to_wait > 0:
                logging.warning(f"[RateLimiter] Limite de RPM ({self.rpm_limit}) atingido. Aguardando {time_to_wait:.2f} segundos.")
                time.sleep(time_to_wait)
        self.request_timestamps.append(time.time())

    def wait_for_tpm_slot(self, tokens_to_send: int):
        # MELHORIA: Lógica de espera do TPM mais inteligente.
        self._cleanup_old_tokens()
        current_tokens = sum(count for _, count in self.token_usage)

        while current_tokens + tokens_to_send > self.tpm_limit:
            if not self.token_usage:
                error_msg = f"[RateLimiter] A requisição única ({tokens_to_send} tokens) excede o limite total de TPM ({self.tpm_limit}). Não é possível prosseguir."
                logging.error(error_msg)
                raise ValueError(error_msg)

            time_to_wait = self.token_usage[0][0] - (time.time() - 60) + 0.1 # Adiciona margem
            if time_to_wait > 0:
                logging.warning(f"[RateLimiter] Limite de TPM seria excedido. Aguardando {time_to_wait:.2f}s para liberar tokens.")
                time.sleep(time_to_wait)
            
            self._cleanup_old_tokens()
            current_tokens = sum(count for _, count in self.token_usage)
        
        self.token_usage.append((time.time(), tokens_to_send))

    def call_api(self, api_function, *args, **kwargs):
        # O número de tokens deve ser passado como um argumento nomeado para esta função.
        prompt_tokens = kwargs.pop('prompt_tokens', 1000) # Remove 'prompt_tokens' de kwargs

        # Espera por um slot de RPM e TPM
        self.wait_for_rpm_slot()
        self.wait_for_tpm_slot(prompt_tokens)

        logging.info(f"[RateLimiter] Realizando chamada para a API com {prompt_tokens} tokens.")
        return api_function(*args, **kwargs)

if __name__ == '__main__':
    gemini_limiter = RateLimiter(rpm_limit=100, tpm_limit=5250000)

    def fake_gemini_api_call(prompt: str):
        print(f"  -> API: Processando prompt: {prompt}")
        time.sleep(0.2)
        return {"response": f"Resposta para: {prompt}"}

    print("Iniciando simulação de chamadas de API com Rate Limiting...")
    for i in range(110):
        print(f"Preparando chamada {i+1}...")
        gemini_limiter.call_api(
            fake_gemini_api_call, 
            prompt=f"Este é o prompt número {i+1}",
            prompt_tokens=50000
        )
    print("\nSimulação concluída.")
