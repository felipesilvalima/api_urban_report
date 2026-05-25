from typing import Optional

from app.domain.services.complaint_service import ComplaintService
from app.domain.services.minio_service import MinioService
from fastapi import APIRouter, Depends,HTTPException,UploadFile,File
from app.infrastructure.database.connect_database import get_session
from sqlalchemy.orm import Session
from app.middleware.verify_token import verify_token
from fastapi_throttle import RateLimiter
from app.main import SECONDS_PER_DAY,REQUEST_LIMITER,MINIO_BUCKET,minio_client

limiter = RateLimiter(times=REQUEST_LIMITER, seconds=SECONDS_PER_DAY)

minio_router = APIRouter(prefix="/api/minio", tags=['api/minio'], dependencies=[Depends(limiter)])

def instancia_minio():
    return MinioService(minio_client, MINIO_BUCKET)


@minio_router.post("/upload/image")
async def upload_image(
    file: UploadFile = File(...),
    complaint_id: Optional[str] = None,
    minio_service: MinioService = Depends(instancia_minio)
):
    """
    Endpoint para upload de imagem
    """
    # Usa o serviço para fazer upload
    result = await minio_service.upload_image(
        file=file,
        prefix="images",
        complaint_id=complaint_id
    )
    
    return {
        "message": "Upload realizado com sucesso",
        "object_name": result["object_name"],
        "size_bytes": result["size_bytes"]
    }