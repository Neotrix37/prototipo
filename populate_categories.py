import sys
import os
from typing import List, Dict

# Adiciona o diretório raiz ao path para garantir que os imports funcionem
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.categorias import Categoria

def init_db(db: Session) -> None:
    """Popula o banco de dados com categorias padrão."""
    
    # Categorias padrão
    categorias_padrao = [
        {"nome": "Alimentos", "descricao": "Produtos alimentícios em geral"},
        {"nome": "Bebidas", "descricao": "Bebidas em geral"},
        {"nome": "Limpeza", "descricao": "Produtos de limpeza"},
        {"nome": "Higiene", "descricao": "Produtos de higiene pessoal"},
        {"nome": "Congelados", "descricao": "Produtos congelados"},
        {"nome": "Mercearia", "descricao": "Produtos de mercearia em geral"},
        {"nome": "Padaria", "descricao": "Produtos de padaria"},
        {"nome": "Hortifruti", "descricao": "Frutas, legumes e verduras"},
        {"nome": "Açougue", "descricao": "Carnes em geral"},
        {"nome": "Laticínios", "descricao": "Leite e derivados"},
        {"nome": "Outros", "descricao": "Outros tipos de produtos"}
    ]
    
    # Adiciona cada categoria que ainda não existe
    for categoria_data in categorias_padrao:
        # Verifica se a categoria já existe
        categoria_existente = db.query(Categoria).filter(
            Categoria.nome == categoria_data["nome"]
        ).first()
        
        if not categoria_existente:
            # Cria a categoria
            db_categoria = Categoria(**categoria_data)
            db.add(db_categoria)
            print(f"Categoria adicionada: {categoria_data['nome']}")
    
    # Salva as alterações no banco de dados
    db.commit()

def init() -> None:
    """Inicializa o banco de dados com categorias padrão."""
    db = SessionLocal()
    try:
        init_db(db)
        print("\nBanco de dados populado com sucesso!")
    except Exception as e:
        print(f"\nErro ao popular o banco de dados: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Iniciando a população do banco de dados com categorias padrão...")
    init()
