from app.main import SECRET_KEY,ALGORITHM
from jose import jwt,JWTError
from fastapi import Depends,HTTPException
from sqlalchemy.orm import Session
from app.infrastructure.database.connect_database import get_session
from app.models.models import User
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), session: Session = Depends(get_session)): # função para verificar token
    try:
        token = credentials.credentials 
        dic_inf =  jwt.decode(token=token,key=SECRET_KEY,algorithms=ALGORITHM)
        user_id = int(dic_inf.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401,detail="Acesso negado, verifique a data de expiração do token")

    user = session.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=401, detail="Acesso inválido")
    return user