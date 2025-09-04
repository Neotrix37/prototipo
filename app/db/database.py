"""
Configuração centralizada do banco de dados.
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Obtém a URL do banco de dados das variáveis de ambiente
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    logger.error("❌ A variável de ambiente DATABASE_URL não está configurada")
    raise ValueError("A variável de ambiente DATABASE_URL não está configurada")

# Configuração do engine do SQLAlchemy
try:
    # Adiciona sslmode=require à URL se não estiver presente
    if 'sslmode=' not in DATABASE_URL:
        separator = '&' if '?' in DATABASE_URL else '?'
        DATABASE_URL = f"{DATABASE_URL}{separator}sslmode=require"
    
    logger.info(f"Conectando ao banco de dados em: {DATABASE_URL.split('@')[-1]}")
    
    # Configura o engine do SQLAlchemy
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=5,
        max_overflow=10,
        connect_args={
            "connect_timeout": 10,
            "options": "-c timezone=utc -c statement_timeout=30000"
        },
        echo=True  # Habilita logs de SQL para debug
    )
    
    # Testa a conexão
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        logger.info(f"✅ Conexão com o banco de dados estabelecida com sucesso! Resultado: {result.scalar()}")
    
except Exception as e:
    logger.error(f"❌ Erro ao configurar a conexão com o banco de dados: {e}")
    logger.error("Verifique se a variável DATABASE_URL está correta e se o banco de dados está acessível")
    raise

# Sessão do banco de dados
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine,
    expire_on_commit=False
)

def get_db():
    """
    Fornece uma sessão do banco de dados.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Erro na sessão do banco de dados: {e}")
        db.rollback()
        raise
    finally:
        db.close()
