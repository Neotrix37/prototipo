"""
Configuração centralizada do banco de dados.
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
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
    # Tenta usar a URL padrão para desenvolvimento local
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/posto"
    logger.warning(f"Usando URL padrão para desenvolvimento: {DATABASE_URL}")
else:
    # Garante que a URL use o formato postgresql:// em vez de postgres://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    logger.info(f"Usando DATABASE_URL: {DATABASE_URL.split('@')[-1]}")

# Configuração do engine do SQLAlchemy
try:
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
    
    # Cria uma fábrica de sessões
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Classe base para os modelos
    Base = declarative_base()
    
except Exception as e:
    logger.error(f"❌ Erro ao conectar ao banco de dados: {str(e)}")
    raise

def get_db():
    """
    Fornece uma sessão do banco de dados.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"❌ Erro na sessão do banco de dados: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()
