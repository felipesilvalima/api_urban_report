
from typing import Optional

import uuid
from io import BytesIO
from app.main import MINIO_BUCKET,MINIO_ENDPOINT
from fastapi import HTTPException,UploadFile
from datetime import datetime, timedelta
from minio import Minio


class MinioService:
    def __init__(self, minio_client: Minio, bucket_name: str):
        """
        Inicializa o serviço com o cliente MinIO e bucket
        
        Args:
            minio_client: Instância do cliente MinIO
            bucket_name: Nome do bucket para armazenar os arquivos
        """
        self.minio_client = minio_client
        self.bucket_name = bucket_name
    
    
    async def upload_image(
        self,
        file: UploadFile,
        prefix: str = "images",
        complaint_id: Optional[str] = None
    ) -> dict:
        """
        Upload de imagem e retorna informações do caminho
        
        Args:
            file: Arquivo enviado
            prefix: Pasta onde salvar (ex: "reports", "profiles")
            report_id: ID opcional para organizar
            
        Returns:
            Dict com caminho, URL e metadados
        """
        try:
            # 1. Validar tipo de arquivo
            if not file.content_type or not file.content_type.startswith('image/'):
                raise HTTPException(400, "Arquivo deve ser uma imagem")
            
            # 2. Gerar nome único para o arquivo usando UUID
            file_extension = file.filename.split('.')[-1].lower() if file.filename else 'jpg'
            unique_id = uuid.uuid4().hex  # Gera ID único ex: 'abc123def456...'
            
            # 3. Montar o caminho do objeto no MinIO
            if complaint_id:
                # Organiza por report_id: images/reports/{report_id}/{uuid}.jpg
                object_name = f"{prefix}/reports/{complaint_id}/{unique_id}.{file_extension}"
            else:
                # Organiza por data: images/2024/12/25/{uuid}.jpg
                now = datetime.now()
                object_name = f"{prefix}/{now.year}/{now.month}/{now.day}/{unique_id}.{file_extension}"
            
            # 4. Ler o conteúdo do arquivo
            content = await file.read()
            file_size = len(content)
            
            # 5. Criar stream em memória com BytesIO
            file_stream = BytesIO(content)
            
            # 6. Upload para o MinIO
            result = self.minio_client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=file_stream,
                length=file_size,
                content_type=file.content_type
            )
            
            # 7. Fechar o stream
            file_stream.close()
            
            # 8. Retornar informações do arquivo
            return {
                "success": True,
                "object_name": object_name,  # Caminho dentro do bucket
                "bucket": self.bucket_name,
                "etag": result.etag,
                "size_bytes": file_size,
                "content_type": file.content_type
            }
            
        except Exception as e:
            raise HTTPException(500, f"Erro no upload: {str(e)}")
    