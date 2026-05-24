import requests
from requests.exceptions import RequestException, HTTPError, ConnectionError, Timeout
import time
import os
import logging
from app.logs.config import logger

from app.exeception.domain.api_cep_domain_exeception import CepNotFound, InternalError, LimitRate, ValidationError

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

    

    def get(self,endpoint: str, params = None):
        
        url = f"{self.base_url}/{endpoint}"
        
        #retry
        for attempt in range(self.max_retries):

            try:
                resp = requests.get(url,headers=self.headers,timeout=self.timeout,params=params)

                self.__treatment_code(resp.status_code)

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

    def __treatment_code(self,code: int):

        match code:
            case 429:
                logger.warning(f"Rate limit atingido Tentativa: {self.attempt}")
                logger.info(f"Aguardando 60 segundos antes de nova tentativa")
                raise LimitRate("Limite de requisições atingida")
        
            case 400:
                logger.error(f"CEP inválido ou mal formatado. Status: 400")
                logger.debug(f"Headers enviados")
                raise ValidationError("CEP inválido ou mal formatado.")
        
            case 404:
                logger.info(f"CEP não encontrado. Status: 404")
                logger.debug(f"Provedores consultados: ViaCEP, OpenCEP, APICEP")
                raise CepNotFound("CEP não encontrado em nenhum provedor.")
        
            case 500:
                logger.critical(f"Erro interno no serviço de CEP - Status: 500")
                logger.error(f"Possível problema no servidor da API de CEP")
                raise InternalError("Erro interno no serviço de CEP.", 500)
        
            case _:
                logger.warning(f"Status code não tratado: {code}")
                return True


