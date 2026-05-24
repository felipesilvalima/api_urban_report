from app.exeception.domain.user_domain_exeception import AuthNotAuthorized, AuthConflict
from sqlalchemy.orm import Session
from app.schema.authSchema import AuthSchema
from app.infrastructure.repository.authRepository import AuthRepository
from app.models.models import User
import logging

class AuthService:
    def __init__(self, session: Session):
        self.authRepository = AuthRepository(session=session)

    def autentication(self,authSchema: AuthSchema):

        user = self.authRepository.filter_repository([User.email == authSchema.email]).first()
        
        if not user:
            return False
        elif not user.verify_password(authSchema.password):
            return False
        else:
            return user
    
    def register_user_service(self, register_authSchema,user_logged_in: User ):

        logging.info("Registrando um usuário na base de dados")

        user = self.authRepository.filter_repository([User.email == register_authSchema.email]).first()

        #regras
        if user_logged_in.validate_is_admin() != True and register_authSchema.admin == True:
            raise AuthNotAuthorized("Você não tem permissão para criar um usuário administrativo",403)
        
        if user:
            raise AuthConflict("Email já existe na base de dados",409)
        
        #criptografar senha do usuário
        password_hash = user_logged_in.genereted_hash(register_authSchema.senha)
        
        #criar um objeto de usuário
        create_user = User(
            name=register_authSchema.nome,
            email=register_authSchema.email,
            password=password_hash,
            active=register_authSchema.ativo,
            admin=register_authSchema.admin
        )

        logging.info("Objeto Usuário criado com sucesso")
        
        #inserindo usuario na base de dados
        return self.authRepository.register_repository(new_object=create_user)
    