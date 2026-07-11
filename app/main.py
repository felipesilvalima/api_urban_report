from app.cors.config import corsConfig
from fastapi import FastAPI
from dotenv import load_dotenv
import os
from app.exeception.handles.exeception_handlers import register_exception_handlers
load_dotenv()
from app.infrastructure.storage.minio_init import MinioInit


SECRET_KEY = str(os.getenv("SECRET_KEY")) # VARIVEIS DE AMBEINTES
ALGORITHM = os.getenv("ALGORITHM")
ACESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACESS_TOKEN_EXPIRE_MINUTES"))
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_BUCKET = os.getenv("MINIO_BUCKET")
MAX_COMPLAINTS_PER_CPF = int(os.getenv("MAX_COMPLAINTS_PER_CPF"))

app = FastAPI()

#config cors. Segurança de acesso de domains permitidos
corsConfig(app)

#exeções
register_exception_handlers(app=app)

#inicializar o minio
minio_init = MinioInit()
minio_client = minio_init.init_minio()
bucket_name = minio_init.get_bucket()


from app.api.v1.routers.auth_routers import auth_router
from app.api.v1.routers.complaint_routers import complaint_router
from app.api.v1.routers.minio_routers import minio_router

app.include_router(auth_router)
app.include_router(complaint_router)
app.include_router(minio_router)
