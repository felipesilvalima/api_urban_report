from app.cors.config import corsConfig
from fastapi import FastAPI
from dotenv import load_dotenv
import os
from app.exeception.handles.exeception_handlers import register_exception_handlers
load_dotenv()

SECRET_KEY = str(os.getenv("SECRET_KEY")) # VARIVEIS DE AMBEINTES
ALGORITHM = os.getenv("ALGORITHM")
ACESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACESS_TOKEN_EXPIRE_MINUTES"))
SECONDS_PER_DAY = int(os.getenv("SECONDS_PER_DAY"))
REQUEST_LIMITER = int(os.getenv("REQUEST_LIMITER"))


app = FastAPI()

#config cors. Segurança de acesso de domains permitidos
corsConfig(app)

#exeções
register_exception_handlers(app=app)

from app.api.v1.routers.auth_routers import auth_router
from app.api.v1.routers.complaint_routers import complaint_router

app.include_router(auth_router)
app.include_router(complaint_router)
