import os
from app.exeception.domain.api_cep_domain_exeception import InternalError, LimitRate, ValidationError
from app.exeception.domain.api_cpf_doamin_exeception import CpfNotAuthorized, CpfNotFound
from dotenv import load_dotenv
from app.infrastructure.http.client_http import ClientHttp
from app.logs.config import logger

class Cpf:

    def __init__(self):

        load_dotenv()

        self.base_url = os.getenv("BASE_URL_CPF")
        self.token = os.getenv("TOKEN_HYDRA_CPF")

        headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.token
        }

        self.http = ClientHttp(
            base_url=self.base_url,
            headers=headers,
        )

        
    def search_cpf(self, cpf: str):

        url = f"cpf/{cpf}"

        result = self.http.get(
            url,
            self.__treatment_code
        )
  
        return result
    


    def __treatment_code(self,code: int):

        match code:
            case 429:
                logger.warning(f"Rate limit atingido")
                logger.info(f"Aguardando 60 segundos antes de nova tentativa")
                raise LimitRate("Limite de requisições atingida")
        
            case 400:
                logger.error(f"CPF inválido ou mal formatado. Status: 400")
                logger.debug(f"Headers enviados")
                raise ValidationError("O CPF fornecido não é válido.")
        
            case 404:
                logger.info(f"CPF não encontrado. Status: 404")
                logger.debug(f"Provedores consultados: HYDRACPF")
                raise CpfNotFound("O CPF não foi encontrado na base de dados.")

            case 403:
                logger.warning(f"Error de permisão")
                logger.debug(f"Token inválido ou expirado!")
                raise CpfNotAuthorized("Você não tem permissão para acessar este recurso.")
            
            case 500:
                logger.critical(f"Erro interno no serviço de CPF - Status: 500")
                logger.error(f"Possível problema no servidor da API de CPF")
                raise InternalError("Erro interno no serviço de CPF.", 500)
        
            case _:
                logger.warning(f"Status code não tratado: {code}")
                return True