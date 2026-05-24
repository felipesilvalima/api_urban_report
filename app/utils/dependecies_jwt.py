from datetime import timedelta,timezone,datetime
from app.main import ACESS_TOKEN_EXPIRE_MINUTES,SECRET_KEY,ALGORITHM
from jose import jwt

def generete_token(id_user, duration_expire = timedelta(minutes=ACESS_TOKEN_EXPIRE_MINUTES)):
    date_expire = datetime.now(timezone.utc) + duration_expire
    payload = {"sub" : str(id_user), "exp" : date_expire} # payload
    jwt_codificad = jwt.encode(payload,SECRET_KEY, ALGORITHM) # codificado 
    return jwt_codificad
