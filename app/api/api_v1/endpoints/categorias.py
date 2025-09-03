from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ....core import security
from ....db.session import get_db
from ....models.categorias import Categoria as CategoriaModel
from ....schemas.categoria import (
    Categoria as CategoriaSchema,
    CategoriaCreate,
    CategoriaUpdate,
    CategoriaInDB
)

router = APIRouter()

# Categorias padrão que serão criadas automaticamente
CATEGORIAS_PADRAO = [
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

def criar_categorias_padrao(db: Session):
    """Cria as categorias padrão no banco de dados."""
    for categoria_data in CATEGORIAS_PADRAO:
        # Verifica se a categoria já existe
        categoria = db.query(CategoriaModel).filter(
            CategoriaModel.nome == categoria_data["nome"]
        ).first()
        
        # Se não existir, cria a categoria
        if not categoria:
            categoria = CategoriaModel(**categoria_data)
            db.add(categoria)
    
    db.commit()

@router.get("/", response_model=List[CategoriaSchema])
async def listar_categorias(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: CategoriaModel = Depends(security.get_current_active_user)
):
    """
    Lista todas as categorias.
    """
    # Cria as categorias padrão se não existirem
    criar_categorias_padrao(db)
    
    categorias = db.query(CategoriaModel).offset(skip).limit(limit).all()
    return categorias

@router.post("/", response_model=CategoriaSchema, status_code=status.HTTP_201_CREATED)
async def criar_categoria(
    *,
    db: Session = Depends(get_db),
    categoria_in: CategoriaCreate,
    current_user: CategoriaModel = Depends(security.get_current_active_user)
):
    """
    Cria uma nova categoria.
    """
    # Verifica se já existe uma categoria com o mesmo nome
    db_categoria = db.query(CategoriaModel).filter(
        CategoriaModel.nome == categoria_in.nome
    ).first()
    
    if db_categoria:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe uma categoria com este nome"
        )
    
    categoria = CategoriaModel(**categoria_in.dict())
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    
    return categoria

@router.get("/{categoria_id}", response_model=CategoriaSchema)
async def obter_categoria(
    categoria_id: int,
    db: Session = Depends(get_db),
    current_user: CategoriaModel = Depends(security.get_current_active_user)
):
    """
    Obtém uma categoria pelo seu ID.
    """
    categoria = db.query(CategoriaModel).get(categoria_id)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada"
        )
    
    return categoria

@router.put("/{categoria_id}", response_model=CategoriaSchema)
async def atualizar_categoria(
    categoria_id: int,
    categoria_in: CategoriaUpdate,
    db: Session = Depends(get_db),
    current_user: CategoriaModel = Depends(security.get_current_active_user)
):
    """
    Atualiza uma categoria existente.
    """
    categoria = db.query(CategoriaModel).get(categoria_id)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada"
        )
    
    # Atualiza apenas os campos fornecidos
    update_data = categoria_in.dict(exclude_unset=True)
    
    # Verifica se está tentando atualizar o nome para um que já existe
    if 'nome' in update_data:
        existing_categoria = db.query(CategoriaModel).filter(
            CategoriaModel.nome == update_data['nome'],
            CategoriaModel.id != categoria_id
        ).first()
        if existing_categoria:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe outra categoria com este nome"
            )
    
    for field, value in update_data.items():
        setattr(categoria, field, value)
    
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    
    return categoria

@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
async def excluir_categoria(
    categoria_id: int,
    db: Session = Depends(get_db),
    current_user: CategoriaModel = Depends(security.get_current_active_user)
):
    """
    Exclui uma categoria.
    """
    # Verifica se a categoria existe
    categoria = db.query(CategoriaModel).get(categoria_id)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada"
        )
    
    # Verifica se existem produtos associados a esta categoria
    # (Você precisará importar o modelo de produtos aqui)
    from ....models.produtos import Produto
    produtos_com_categoria = db.query(Produto).filter(
        Produto.categoria_id == categoria_id
    ).count()
    
    if produtos_com_categoria > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível excluir uma categoria que possui produtos associados"
        )
    
    # Se não houver produtos associados, exclui a categoria
    db.delete(categoria)
    db.commit()
    
    return None
