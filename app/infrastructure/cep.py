import requests
from requests.exceptions import RequestException, HTTPError, ConnectionError, Timeout
import time
import os
import logging
from app.logs.config import logger

from app.exeception.domain.api_cep_domain_exeception import CepNotFound, InternalError, LimitRate, ValidationError
class Cep:

    attempts = 3
    max_retries = 3

    def get_cep(self,cep: str):
        
        base_url = os.getenv("BASE_URL_CEP")

        url = f"{base_url}/{cep}"

        headers = {
            "Content-Type": "application/json"
        }

        for attempt in range(self.attempts):
        
            try:
                resp = requests.get(url,headers=headers,timeout=5)

                self.__treatment_code(resp.status_code)
                
                return resp.json()
            except requests.exceptions.Timeout as e:
                logger.warning(f"Timeout na tentativa {attempt}/{self.max_retries} - URL: {url}")
                if attempt == self.max_retries:
                    logger.error(f"Timeout persistente após {max_retries} tentativas - URL: {url}")
                    raise RequestException("Serviço externo lento")
                time.sleep(5)
        
            except requests.exceptions.ConnectionError as e:
                logger.error(f"Erro de conexão na tentativa {attempt}/{self.max_retries} - URL: {url} - Detalhe: {str(e)}")
                if attempt == self.max_retries:
                    logger.critical(f"Conexão falhou permanentemente - URL: {url}")
                    raise RequestException("Error de conexão com a api externa")
                time.sleep(5)
        
            except requests.exceptions.RequestException as e:
                logger.exception(f"Erro inesperado na tentativa {attempt}/{self.max_retries} - URL: {url}")  # exception mostra stacktrace
                if attempt == self.max_retries:
                    logger.critical(f"Erro desconhecido persistente - URL: {url}")
                    raise RequestException("Error desconhecido")
                time.sleep(5)

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


