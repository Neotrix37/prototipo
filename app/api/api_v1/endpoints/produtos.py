from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ....core import security
from ....db.session import get_db
from ....models.produtos import Produto as ProdutoModel
from ....models.fornecedor import Fornecedor as FornecedorModel
from ....schemas.produtos import (
    Produto as ProdutoSchema,
    ProdutoCreate,
    ProdutoUpdate,
    ProdutoInDB
)

router = APIRouter()

def get_fornecedor_padrao(db: Session) -> int:
    """Obtém o ID do fornecedor padrão ou o cria se não existir."""
    fornecedor_padrao = db.query(FornecedorModel).filter(
        FornecedorModel.nome.ilike("Fornecedor Padrão")
    ).first()
    
    if not fornecedor_padrao:
        # Cria um fornecedor padrão se não existir
        fornecedor_padrao = FornecedorModel(
            nome="Fornecedor Padrão",
            telefone="(00) 0000-0000",
            email="contato@fornecedorpadrao.com.br",
            endereco="Endereço não informado",
            ativo=True
        )
        db.add(fornecedor_padrao)
        db.commit()
        db.refresh(fornecedor_padrao)
    
    return fornecedor_padrao.id

@router.get("/", response_model=List[ProdutoSchema])
async def listar_produtos(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    ativo: Optional[bool] = True,
    incluir_inativos: bool = False,
    categoria_id: Optional[int] = None,
    fornecedor_id: Optional[int] = None,
    current_user: ProdutoModel = Depends(security.get_current_active_user)
):
    """
    Lista os produtos com filtros opcionais.
    Por padrão, mostra apenas produtos ativos.
    Use incluir_inativos=True para incluir produtos inativos.
    """
    query = db.query(ProdutoModel)
    
    # Se incluir_inativos for False, filtra por ativo=True
    if not incluir_inativos:
        query = query.filter(ProdutoModel.ativo == True)
    # Se ativo for especificado explicitamente, sobrepõe o comportamento padrão
    elif ativo is not None:
        query = query.filter(ProdutoModel.ativo == ativo)
    
    if categoria_id is not None:
        query = query.filter(ProdutoModel.categoria_id == categoria_id)
    
    if fornecedor_id is not None:
        query = query.filter(ProdutoModel.fornecedor_id == fornecedor_id)
    
    produtos = query.offset(skip).limit(limit).all()
    return produtos

@router.post("/", response_model=ProdutoSchema, status_code=status.HTTP_201_CREATED)
async def criar_produto(
    *,
    db: Session = Depends(get_db),
    produto_in: ProdutoCreate,
    current_user: ProdutoModel = Depends(security.get_current_active_user)
):
    """
    Cria um novo produto.
    """
    # Verifica se já existe um produto com o mesmo código
    db_produto = db.query(ProdutoModel).filter(ProdutoModel.codigo == produto_in.codigo).first()
    if db_produto:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um produto com este código."
        )
    
    # Obtém o ID do fornecedor padrão se não for fornecido
    produto_data = produto_in.model_dump()
    if produto_data.get('fornecedor_id') is None:
        produto_data['fornecedor_id'] = get_fornecedor_padrao(db)
    
    # Verifica se o fornecedor existe
    fornecedor = db.query(FornecedorModel).filter(
        FornecedorModel.id == produto_data['fornecedor_id']
    ).first()
    
    if not fornecedor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Fornecedor com ID {produto_data['fornecedor_id']} não encontrado."
        )
    
    # Cria o produto
    db_produto = ProdutoModel(**produto_data)
    db.add(db_produto)
    db.commit()
    db.refresh(db_produto)
    
    return db_produto

@router.get("/{produto_id}", response_model=ProdutoSchema)
async def obter_produto(
    produto_id: int,
    db: Session = Depends(get_db),
    current_user: ProdutoModel = Depends(security.get_current_active_user)
):
    """
    Obtém um produto pelo seu ID.
    """
    db_produto = db.query(ProdutoModel).filter(ProdutoModel.id == produto_id).first()
    
    if not db_produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado."
        )
    
    return db_produto

@router.put("/{produto_id}", response_model=ProdutoSchema)
async def atualizar_produto(
    produto_id: int,
    produto_in: ProdutoUpdate,
    db: Session = Depends(get_db),
    current_user: ProdutoModel = Depends(security.get_current_active_user)
):
    """
    Atualiza um produto existente.
    """
    db_produto = db.query(ProdutoModel).filter(ProdutoModel.id == produto_id).first()
    
    if not db_produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado."
        )
    
    # Atualiza apenas os campos fornecidos
    update_data = produto_in.model_dump(exclude_unset=True)
    
    # Verifica se o código já está em uso por outro produto
    if 'codigo' in update_data and update_data['codigo'] != db_produto.codigo:
        produto_existente = db.query(ProdutoModel).filter(
            ProdutoModel.codigo == update_data['codigo']
        ).first()
        
        if produto_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe outro produto com este código."
            )
    
    # Verifica se o fornecedor existe, se fornecido
    if 'fornecedor_id' in update_data and update_data['fornecedor_id'] is not None:
        fornecedor = db.query(FornecedorModel).filter(
            FornecedorModel.id == update_data['fornecedor_id']
        ).first()
        
        if not fornecedor:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Fornecedor com ID {update_data['fornecedor_id']} não encontrado."
            )
    
    # Atualiza os campos
    for field, value in update_data.items():
        setattr(db_produto, field, value)
    
    db.commit()
    db.refresh(db_produto)
    
    return db_produto

@router.delete("/{produto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def excluir_produto(
    produto_id: int,
    db: Session = Depends(get_db),
    current_user: ProdutoModel = Depends(security.get_current_active_user)
):
    """
    Exclui um produto (apenas marca como inativo).
    """
    db_produto = db.query(ProdutoModel).filter(ProdutoModel.id == produto_id).first()
    
    if not db_produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado."
        )
    
    # Marca como inativo em vez de excluir fisicamente
    db_produto.ativo = False
    db.commit()
    
    return None
