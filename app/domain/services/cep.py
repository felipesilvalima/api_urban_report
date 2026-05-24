import os
from re import search
from app.exeception.domain.api_cep_domain_exeception import CepNotFound
from dotenv import load_dotenv
from app.infrastructure.http.client_http import ClientHttp

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
            url
        )

        if not address:
            raise CepNotFound("Endereço não encontrado.")
        
        return address