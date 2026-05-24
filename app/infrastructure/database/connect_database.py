from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    pool_size=5,  # Número de conexões mantidas no pool
    max_overflow=10,  # Conexões extras permitidas quando o pool está cheio
    pool_pre_ping=True,  # Verifica se a conexão está viva antes de usar
    echo=True  # Log das queries SQL (opcional, útil para debug)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Função para obter a sessão do banco de dados
def get_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e  
    finally:
        session.close()