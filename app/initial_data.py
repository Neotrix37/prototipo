import sys
import logging
from sqlalchemy.orm import Session
from sqlalchemy import text

from .db.session import engine, get_db
from .core.config import settings
from .core import security
from .models.usuario import Usuario

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def is_database_empty() -> bool:
    """Verifica se o banco de dados está vazio"""
    with engine.connect() as conn:
        tables = engine.dialect.get_table_names(conn)
        return len(tables) == 0

def init_db(db: Session) -> None:
    """Inicializa o banco de dados com dados iniciais"""
    
    # Cria as tabelas se não existirem
    from .db.base import Base
    Base.metadata.create_all(bind=engine)
    
    # Verifica se já existe um usuário administrador
    admin = db.query(Usuario).filter(Usuario.usuario == "admin37").first()
    
    if not admin:
        # Verifica se o banco está vazio (apenas para evitar mensagens desnecessárias)
        if is_database_empty():
            logger.info("Banco de dados vazio detectado. Criando usuário administrador...")
        
        # Cria o usuário administrador padrão
        admin_user = Usuario(
            nome="Administrador do Sistema",
            usuario="admin37",
            senha=security.get_password_hash("842384"),
            nivel=3,  # Nível de gerente
            ativo=True,
            is_admin=True,
            pode_abastecer=True
        )
        
        db.add(admin_user)
        db.commit()
        
        logger.info("\n" + "="*60)
        logger.info("USUÁRIO ADMINISTRADOR CRIADO COM SUCESSO")
        logger.info("Usuário: admin37")
        logger.info("Senha: 842384")
        logger.info("="*60 + "\n")
    else:
        logger.info("Usuário administrador já existe no banco de dados.")

if __name__ == "__main__":
    logger.info("Inicializando banco de dados...")
    db = next(get_db())
    try:
        init_db(db)
        logger.info("Inicialização concluída com sucesso!")
    except Exception as e:
        logger.error(f"Erro durante a inicialização do banco de dados: {str(e)}")
        sys.exit(1)
    finally:
        db.close()
