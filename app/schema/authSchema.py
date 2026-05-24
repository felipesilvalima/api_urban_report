from pydantic import BaseModel,field_validator
from fastapi import HTTPException
from typing import Optional


class RegisterAuthSchema(BaseModel):

    nome: str
    email: str
    senha: str
    ativo: Optional[bool] = True 
    admin: Optional[bool] = False 

    @field_validator("nome")
    def nome_validater(cls, nome):

        if len(nome) == 0:
            raise HTTPException(status_code=400, detail="Nome é Obrigatório!")
        
        if len(nome) > 38 or len(nome) < 2:
            raise HTTPException(status_code=400, detail="Nome deve conter entre 2 e 39 caracteres.")
        
        return nome.capitalize().strip()
    
    @field_validator("email")
    def email_validater(cls, email):

        if len(email) == 0:
            raise HTTPException(status_code=400, detail="Email é Obrigatório!")

        if '@' not in email:
            raise HTTPException(status_code=400, detail="Email inválido: formato incorreto")
        
        return email.lower().strip()
    
    @field_validator("senha")
    def senha_validater(cls, senha):

        if len(senha) == 0:
            raise HTTPException(status_code=400, detail="Senha é Obrigatório!")
        
        if len(senha) > 12:
            raise HTTPException(status_code=400,detail="Campo senha dever ter no máximo 12 caracteres")
        
        return senha.strip()
    
    class config:
        from_attributes = True


class AuthSchema(BaseModel):

    email: str
    password: str

    class config:
        from_attributes = True