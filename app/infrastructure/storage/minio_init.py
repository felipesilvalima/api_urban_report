
import os
from minio import Minio
from app.logs.config import logger
from dotenv import load_dotenv
class MinioInit:
    def __init__(self, minio_endpoint=None, minio_access_key=None, minio_secret_key=None, minio_bucket=None):
        # Carrega variáveis do .env
        load_dotenv()
        
        # Usa os parâmetros ou pega do environment
        self.MINIO_ENDPOINT = minio_endpoint or os.getenv("MINIO_ENDPOINT")
        self.MINIO_ACCESS_KEY = minio_access_key or os.getenv("MINIO_ACCESS_KEY")
        self.MINIO_SECRET_KEY = minio_secret_key or os.getenv("MINIO_SECRET_KEY")
        self.MINIO_BUCKET = minio_bucket or os.getenv("MINIO_BUCKET")
        
        # Validação
        if not all([self.MINIO_ENDPOINT, self.MINIO_ACCESS_KEY, 
                    self.MINIO_SECRET_KEY, self.MINIO_BUCKET]):
            raise ValueError("❌ Todas as configurações do MinIO são obrigatórias")
        
        # Inicializa cliente
        self.minio_client = None
    
    def init_minio(self):
        """Inicializa o cliente MinIO e cria bucket se necessário"""
        try:
            # Cria cliente
            self.minio_client = Minio(
                self.MINIO_ENDPOINT,
                access_key=self.MINIO_ACCESS_KEY,
                secret_key=self.MINIO_SECRET_KEY,
                secure=False  # Mude para True se usar HTTPS
            )
            
            # Verifica/cria bucket
            if not self.minio_client.bucket_exists(self.MINIO_BUCKET):
                self.minio_client.make_bucket(self.MINIO_BUCKET)
                logger.info(f"✅ Bucket '{self.MINIO_BUCKET}' criado com sucesso!")
            else:
                logger.info(f"✅ Bucket '{self.MINIO_BUCKET}' já existe")
            
            return self.minio_client
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar MinIO: {e}")
            raise
    
    def get_client(self):
        """Retorna o cliente MinIO já inicializado"""
        if not self.minio_client:
            self.init_minio()
        return self.minio_client
    
    def get_bucket(self):
        """Retorna o nome do bucket"""
        return self.MINIO_BUCKET
    


    
