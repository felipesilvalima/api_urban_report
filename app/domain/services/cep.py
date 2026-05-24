import os
from re import search

from app.infrastructure.http.client_http import ClientHttp

class Cep:

    def __init__(self):
        self.base_url = os.getenv("BASE_URL_CEP")
        self.token = os.getenv("TOKEN_CEP_ABERTO")

        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.token
        }

        self.http = ClientHttp(
            base_url=self.base_url,
            default_headers=headers,
        )

        
    def search_cep(self, cep: str):

        url = f"cep?cep={cep}"

        result = self.http.get(
            url
        )