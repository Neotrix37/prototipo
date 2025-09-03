"""
Configuração centralizada do banco de dados.
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Obtém a URL do banco de dados das variáveis de ambiente
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("A variável de ambiente DATABASE_URL não está configurada")

# Configuração do engine do SQLAlchemy
try:
    print(f"Conectando ao banco de dados em: {DATABASE_URL.split('@')[-1]}")
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args={
            "connect_timeout": 10,
            "options": "-c timezone=utc -c client_encoding=utf8"
        },
        echo=True  # Habilita logs de SQL para debug
    )
    print("Conexão com o banco de dados configurada com sucesso!")
except Exception as e:
    print(f"Erro ao configurar a conexão com o banco de dados: {e}")
    raise

# Sessão do banco de dados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Fornece uma sessão do banco de dados.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
