from typing import List
from fastapi import HTTPException
from app.exeception.domain.user_domain_exeception import EmailInvalid

class EmailDomainValidator:
    """Validador compartilhado para domínio de email"""
    
    DOMINIOS_PERMITIDOS = ["gmail.com", "outlook.com", "hotmail.com", "empresa.com.br"]
    
    @classmethod
    def validar_dominio(cls, email: str, dominios_permitidos: List[str] = None) -> bool:
        if dominios_permitidos is None:
            dominios_permitidos = cls.DOMINIOS_PERMITIDOS
        
        dominio = email.split('@')[-1].lower()
        if dominio not in dominios_permitidos:
            raise EmailInvalid(f"Domínio '{dominio}' não permitido. Domínios válidos: {', '.join(dominios_permitidos)}",400)
        return True