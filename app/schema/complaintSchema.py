from pydantic import BaseModel,field_validator,validator
from app.domain.enums.category_enums import CategoryEnum
from app.domain.enums.report_status_enums import ReportStatusEnum
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

        if category.name not in CategoryEnum.__members__:
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



# complaintSchema.py

class ImageValidator:
    """Validações para imagens"""
    
    MAX_SIZE_MB = 5
    MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024
    
    EXTENSOES_PERMITIDAS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    MIMES_PERMITIDOS = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}
    
    @classmethod
    def obter_extensao(cls, filename: str) -> str:
        """Extrai extensão do nome do arquivo"""
        if not filename or '.' not in filename:
            return ''
        
        # Pega a extensão (ex: .jpg, .png)
        extensao = f".{filename.rsplit('.', 1)[-1].lower()}"
        return extensao
    
    @classmethod
    async def validar_image(cls, file) -> tuple:
        """Valida a imagem e retorna (conteudo, extensao)"""
        
        # 1. Valida extensão
        if not file.filename:
            raise HTTPException(400, "Arquivo sem nome")
        
        extensao = cls.obter_extensao(file.filename)  # 👈 Agora funciona
        
        if extensao not in cls.EXTENSOES_PERMITIDAS:
            raise HTTPException(
                400,
                f"Extensão '{extensao}' não permitida. Use: {', '.join(cls.EXTENSOES_PERMITIDAS)}"
            )
        
        # 2. Valida MIME type
        if file.content_type not in cls.MIMES_PERMITIDOS:
            raise HTTPException(
                400,
                f"Tipo de arquivo '{file.content_type}' não permitido"
            )
        
        # 3. Valida tamanho
        conteudo = await file.read()
        tamanho_bytes = len(conteudo)
        
        if tamanho_bytes > cls.MAX_SIZE_BYTES:
            raise HTTPException(
                400,
                f"Arquivo muito grande. Máximo {cls.MAX_SIZE_MB}MB"
            )
        
        # 4. Reseta o cursor
        await file.seek(0)
        
        return conteudo, extensao


class ComplaintStatusSchema(BaseModel):
    status: ReportStatusEnum

    @field_validator("status")
    def status_validater(cls, status):
        if status.name == ReportStatusEnum.PENDING.name:
            raise HTTPException(status_code=400, detail=f"Status inválido. Não e permitido alterar para status {status.name}")
        return status.name

class ComplaintFilterSchema(BaseModel):

    category: Optional[CategoryEnum] = None
    status: Optional[ReportStatusEnum] = None
    page: Optional[int] = None
    limit: Optional[int] = None