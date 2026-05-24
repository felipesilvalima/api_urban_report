from fastapi import APIRouter, Depends,HTTPException
from app.infrastructure.database.connect_database import get_session
from sqlalchemy.orm import Session
from app.schema.authSchema import AuthSchema,RegisterAuthSchema
from app.domain.services.auth_service import AuthService
from app.utils.dependecies_jwt import generete_token
from datetime import timedelta
from app.models.models import User
from app.middleware.verify_token import verify_token

auth_router = APIRouter(prefix="/api/auth", tags=['api/auth'])

def instancia_auth(session: Session = Depends(get_session)):
    return AuthService(session=session)

@auth_router.post("/login")
async def login(
    authSchema: AuthSchema,
    auth_service: AuthService = Depends(instancia_auth)
    
):
    user = auth_service.autentication(authSchema=authSchema)

    if user:

        access_token = generete_token(user.id)
        refresh_token = generete_token(user.id, duration_expire=timedelta(days=7))

        return {
            "access_token" : access_token,
            "refresh_token" : refresh_token,
            "type_token" : "Bearer"
        },200
    
    else:
        raise HTTPException(status_code=401, detail="Email ou Senha inválida")


@auth_router.post("/refresh_token")
async def refresh_token(
    user_loggin_in: User = Depends(verify_token)
):
   
    access_token = generete_token(user_loggin_in.id)

    return {
        "access_token" : access_token,
        "type_token" : "Bearer"
    },201
    
   
      
        
@auth_router.post("/register")
async def register_user(
    register_authSchema: RegisterAuthSchema,
    user_logged_in: User = Depends(verify_token),
    auth_service: AuthService = Depends(instancia_auth)
    
):

    user_registed = auth_service.register_user_service(
        register_authSchema=register_authSchema,
        user_logged_in=user_logged_in
    )
    
    return {"message": f"Usuário criado com sucesso. ID do usuário {user_registed.id}"},201