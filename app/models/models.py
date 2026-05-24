from sqlalchemy.sql import func
from app.domain.enums.category_enums import CategoryEnum
from app.domain.enums.report_status_enums import ReportStatusEnum
from app.domain.rules.email_domain_validator import EmailDomainValidator
from app.exeception.domain.user_domain_exeception import CpfInvalid, PasswordInvalid
from app.infrastructure.database.connect_database import Base
from sqlalchemy import Column,String,Boolean,Integer,Text,Enum,DateTime,Float,ForeignKey
import re
from passlib.context import CryptContext
from validate_docbr import CPF
from datetime import datetime
from sqlalchemy.orm import relationship, declarative_base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String(80), nullable=False)
    email = Column(String(80), nullable=False)
    password = Column(String(90), nullable=False)
    active = Column(Boolean, default=True)
    admin = Column(Boolean, default=False)
  
    def __init__(self, name, email, password, active=True, admin=False):
        self.name = name
        self.email = email
        self.password = password
        self.active = active
        self.admin = admin

        EmailDomainValidator.validar_dominio(self.email)
        self.__validate_password()

    def __validate_password(self):
        VALID_PASSWORD = r"^(?=.*[A-Z])(?=(?:.*\d){2,}).+$"
        
        if not re.match(VALID_PASSWORD,self.password):
            raise PasswordInvalid("Campo senha deve ter no minimo um caracter maiúsculo e dois números inteiros",400)
        
    def verify_password(self,password: str):
        return self.__cryptContext().verify(password, self.password)
    
    def genereted_hash(self,password):
        return self.__cryptContext().hash(password)
    
    def __cryptContext(self):
        return CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def validate_is_admin(self):
        if not self.admin:
            return
        
        return True

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    cpf = Column(String(13), nullable=False, unique=True)
    category = Column(Enum(CategoryEnum, name="category"), nullable=False)
    status = Column(Enum(ReportStatusEnum, name="report_status"), nullable=True, server_default=ReportStatusEnum.PENDING.value)
    
    longitude = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    image_url = Column(String(80), nullable=False)
    description = Column(Text, nullable=True)
    
    created_at = Column(DateTime,nullable=False,server_default=func.now())
    updated_at = Column(DateTime,nullable=False,server_default=func.now(),onupdate=func.now())
    
    address = relationship("Address", back_populates="complaint", uselist=False, cascade="all, delete-orphan")
 

    def __init__(
            self,
            cpf: str,
            category: CategoryEnum,
            longitude: float,
            latitude:float,
            image_url: str,
            description: str | None = None,
            status: ReportStatusEnum = ReportStatusEnum.PENDING.value
        ):

        self.__validateCPf(cpf)
        self.category = category
        self.status = status
        self.longitude = longitude
        self.latitude = latitude
        self.image_url = image_url
        self.description = description


         # auditoria
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


    def __validateCPf(self,cpf: str) -> None:

        #validar cpf
        cpfValidator = CPF()

        if not cpfValidator.validate(cpf):
            raise CpfInvalid("CPF inválido",400)
        
        self.cpf = str(cpf)

    # auditoria #
    def _touch(self):
        self.updated_at = datetime.utcnow()


    
class Address(Base):
    __tablename__ = "addresses"
 
    id = Column(Integer, primary_key=True, autoincrement=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id"), nullable=False, unique=True)
    street = Column(String(150), nullable=True)
    city = Column(String(100), nullable=False)
    state = Column(String(2),   nullable=False)
 
    complaint = relationship("Complaint", back_populates="address")
 
    def __init__(self, report_id: int, city: str, state: str, street: str | None = None):
        self.report_id = report_id
        self.street = street
        self.city = city
        self.state = state       

# 1. Gerar nova migração com as alterações
 #alembic revision --autogenerate -m "first migration"

# 2. Aplicar a migração no banco
 #alembic upgrade head