import os
from re import search
from app.exeception.domain.api_cep_domain_exeception import CepNotFound
from dotenv import load_dotenv
from app.infrastructure.http.client_http import ClientHttp
from app.logs.config import logger
from app.exeception.domain.api_cep_domain_exeception import CepNotFound, InternalError, LimitRate, ValidationError


class Cep:

    def __init__(self):

        load_dotenv()

        self.base_url = os.getenv("BASE_URL_CEP")
        self.token = os.getenv("TOKEN_CEP_ABERTO")

        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.token
        }

        self.http = ClientHttp(
            base_url=self.base_url,
            headers=headers,
        )

        
    def search_cep(self, cep: str):

        url = f"cep?cep={cep}"

        address = self.http.get(
            url,
            self.__treatment_code
        )

        if not address:
            raise CepNotFound("Endereço não encontrado.")
        
        return address
    

    def __treatment_code(self,code: int):

        match code:
            case 429:
                logger.warning(f"Rate limit atingido Tentativa")
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