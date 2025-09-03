from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
import logging

from ..core.config import settings

# Cria a Base diretamente aqui para evitar importação circular
Base = declarative_base()

# Configuração de logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Usa a URL interna em produção, caso exista
DATABASE_URL = settings.DATABASE_URL_INTERNAL if settings.ENVIRONMENT == "production" else settings.DATABASE_URL

# Configuração do engine do SQLAlchemy com pool de conexões
try:
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=5,  # Número de conexões mantidas no pool
        max_overflow=10,  # Número máximo de conexões além do pool_size
        pool_timeout=30,  # Segundos para esperar por uma conexão do pool
        pool_recycle=1800,  # Recicla conexões após 30 minutos
        pool_pre_ping=True,  # Habilita verificação de conexão antes de usar
        connect_args={
            "connect_timeout": 10,
            "options": "-c timezone=utc -c statement_timeout=30000"  # 30 segundos de timeout por query
        }
    )
    
    # Testa a conexão imediatamente com uma query simples
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    
    print("✅ Conexão com o banco de dados estabelecida com sucesso!")
    
except Exception as e:
    print(f"❌ Erro ao conectar ao banco de dados: {e}")
    raise

# Sessão do banco de dados
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # Evita problemas com sessões expiradas
)

def get_db():
    """
    Fornece uma sessão do banco de dados.
    
    Uso:
    ```python
    db = next(get_db())
    try:
        # Use a sessão aqui
        pass
    finally:
        db.close()
    ```
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()

# Exporta os itens necessários
__all__ = ['engine', 'SessionLocal', 'get_db', 'Base']
