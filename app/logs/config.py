import logging

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cep_errors.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
