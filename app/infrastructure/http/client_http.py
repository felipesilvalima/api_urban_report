import requests
from requests.exceptions import RequestException, HTTPError, ConnectionError, Timeout
import time
import os
from app.logs.config import logger
class ClientHttp:

    def __init__(
            self,
            base_url: str,
            headers: dict,
            max_retries: int = 3,
            timeout: int = 5,
            timeout_delay: int = 4

        ):

        self.base_url = base_url
        self.headers = headers
        self.max_retries = max_retries
        self.timeout = timeout
        self.timeout_delay = timeout_delay

    

    def get(self,endpoint: str,handler_status_code = None, params = None):
        
        url = f"{self.base_url}/{endpoint}"
        
        #retry
        for attempt in range(self.max_retries):

            try:
                resp = requests.get(url,headers=self.headers,timeout=self.timeout,params=params)

                if handler_status_code:
                    handler_status_code(resp.status_code)

                return resp.json()
            except requests.exceptions.Timeout as e:
                logger.warning(f"Timeout na tentativa {attempt}/{self.max_retries} - URL: {url}")
                if attempt == self.max_retries:
                    logger.error(f"Timeout persistente após {self.max_retries} tentativas - URL: {url}")
                    raise RequestException("Serviço externo lento")
                time.sleep(self.timeout_delay)
        
            except requests.exceptions.ConnectionError as e:
                logger.error(f"Erro de conexão na tentativa {attempt}/{self.max_retries} - URL: {url} - Detalhe: {str(e)}")
                if attempt == self.max_retries:
                    logger.critical(f"Conexão falhou permanentemente - URL: {url}")
                    raise RequestException("Error de conexão com a api externa")
                time.sleep(self.timeout_delay)
        
            except requests.exceptions.RequestException as e:
                logger.exception(f"Erro inesperado na tentativa {attempt}/{self.max_retries} - URL: {url}")  # exception mostra stacktrace
                if attempt == self.max_retries:
                    logger.critical(f"Erro desconhecido persistente - URL: {url}")
                    raise RequestException("Error desconhecido")
                time.sleep(self.timeout_delay)

    


