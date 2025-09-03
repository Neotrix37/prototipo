import sys
import os

# Adiciona o diretório raiz ao path para garantir que os imports funcionem
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.fornecedor import Fornecedor

def init_db(db: Session) -> None:
    """Popula o banco de dados com um fornecedor padrão."""
    
    # Verifica se já existe um fornecedor padrão
    fornecedor_padrao = (
        db.query(Fornecedor)
        .filter(Fornecedor.nome.ilike("Fornecedor Padrão"))
        .first()
    )
    
    if not fornecedor_padrao:
        # Cria o fornecedor padrão
        db_fornecedor = Fornecedor(
            nome="Fornecedor Padrão",
            telefone="(00) 0000-0000",
            email="contato@fornecedorpadrao.com.br",
            endereco="Endereço não informado",
            ativo=True
        )
        
        db.add(db_fornecedor)
        db.commit()
        db.refresh(db_fornecedor)
        print(f"Fornecedor padrão criado com sucesso! ID: {db_fornecedor.id}")
    else:
        print(f"Fornecedor padrão já existe. ID: {fornecedor_padrao.id}")

def init() -> None:
    """Inicializa o banco de dados com o fornecedor padrão."""
    db = SessionLocal()
    try:
        init_db(db)
        print("\nBanco de dados verificado com sucesso!")
    except Exception as e:
        print(f"\nErro ao verificar o banco de dados: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Verificando e criando fornecedor padrão...")
    init()
