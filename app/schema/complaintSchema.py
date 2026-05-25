from pydantic import BaseModel,field_validator,validator
from app.domain.enums.category_enums import CategoryEnum
from fastapi import HTTPException, UploadFile
from typing import Optional
import re
import base64
from PIL import Image
from io import BytesIO
class ComaplaintSchema(BaseModel):

    cpf: str
    cep: str
    category: CategoryEnum
    image_path: str
    description: Optional[str]

    @field_validator("cpf")
    def cpf_validater(cls, cpf):

        if len(cpf) == 0:
            raise HTTPException(status_code=400, detail="Cpf é Obrigatório!")
        
        cpf = re.sub(r"\D", "", cpf)
        
        return cpf

    @field_validator("cep")
    def cep_validater(cls, cep):

        if len(cep) == 0:
            raise HTTPException(status_code=400, detail="Cep é Obrigatório!")
        
        if len(cep) != 8:
            raise HTTPException(status_code=400, detail="Cep inválido. Precisar conter 8 digitos")
        
        cep = re.sub(r"\D", "", cep)
        
        return cep
    

    @field_validator("category")
    def category_validater(cls, category):

        if len(category) == 0:
            raise HTTPException(status_code=400, detail="Categória é Obrigatório!")
        
        if not category in CategoryEnum.__members__:
            raise HTTPException(status_code=400, detail="Categória não encontrada!")
        
        return category
    

    @field_validator("description")
    def description_validater(cls, description):

        if len(description) != 0:
            if len(description) > 200:
                raise HTTPException(status_code=400, detail="Descrição atingiu o limite de (200) caracteres.")
        
        return description.title()

    @field_validator("image_path")
    def image_path_validater(cls, image_path):

        if len(image_path) == 0:
            raise HTTPException(status_code=400, detail="Caminho da imagem é Obrigatório!")
           
        return image_path 

    class config():
        from_attributes = True



class ImageUpload(BaseModel):

    image: UploadFile

    @field_validator("image")
    async def image_validater(cls, image):

        if image == None:
            raise HTTPException(status_code=400, detail="Imagem é Obrigatória")
        

        # VALIDAÇÃO DE EXTENSÃO
        extensoes_permitidas = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    
        # Verificar pelo filename
        if not any(image.filename.lower().endswith(ext) for ext in extensoes_permitidas):
            raise HTTPException(
                status_code=400,
                detail=f"Extensão não permitida. Use: {', '.join(extensoes_permitidas)}"
            )
        
        # VALIDAÇÃO DE TAMANHO
        MAX_SIZE_MB = 5
        MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024
    
        # Lê o conteúdo para verificar tamanho
        conteudo = await image.read()
        tamanho_bytes = len(conteudo)
    
        if tamanho_bytes > MAX_SIZE_BYTES:
            raise HTTPException(
                status_code=400,
                detail=f"Arquivo muito grande. Máximo {MAX_SIZE_MB}MB"
            )

        await image.seek(0)

        return image