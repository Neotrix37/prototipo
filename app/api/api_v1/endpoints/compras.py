from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from app.db.database import get_db
from app.models.compra import Compra, ItemCompra
from app.models.produtos import Produto
from app.schemas.compra import (
    CompraCreate, CompraUpdate, Compra as CompraSchema,
    ItemCompra as ItemCompraSchema, CompraListagem
)
from app.core.security import get_current_active_user
from app.models.usuario import Usuario

router = APIRouter()

@router.post("/", response_model=CompraSchema, status_code=status.HTTP_201_CREATED)
def criar_compra(
    compra: CompraCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Cria uma nova compra com seus itens e atualiza o estoque.
    """
    try:
        # Cria a compra
        db_compra = Compra(
            fornecedor_id=compra.fornecedor_id,
            valor_total=sum(item.quantidade * item.preco_unitario for item in compra.itens),
            usuario_id=current_user.id,
            observacoes=compra.observacoes
        )
        
        db.add(db_compra)
        db.flush()  # Para obter o ID da compra
        
        # Adiciona os itens da compra e atualiza o estoque
        for item in compra.itens:
            # Atualiza o estoque do produto
            produto = db.query(Produto).filter(Produto.id == item.produto_id).first()
            if not produto:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Produto com ID {item.produto_id} não encontrado"
                )
            
            # Atualiza o estoque
            produto.estoque += item.quantidade
            
            # Cria o item da compra
            db_item = ItemCompra(
                compra_id=db_compra.id,
                produto_id=item.produto_id,
                produto_nome=item.produto_nome,
                quantidade=item.quantidade,
                preco_unitario=item.preco_unitario,
                preco_venda=item.preco_venda,
                lucro_unitario=item.preco_venda - item.preco_unitario,
                lucro_total=(item.preco_venda - item.preco_unitario) * item.quantidade
            )
            db.add(db_item)
        
        db.commit()
        db.refresh(db_compra)
        return db_compra.to_dict()
        
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar compra: {str(e)}"
        )

@router.get("/", response_model=List[CompraSchema])
def listar_compras(
    skip: int = 0,
    limit: int = 100,
    fornecedor_id: Optional[int] = None,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Lista as compras com filtros opcionais.
    """
    query = db.query(Compra).options(
        joinedload(Compra.itens),
        joinedload(Compra.fornecedor),
        joinedload(Compra.usuario)
    )
    
    # Aplicar filtros
    if fornecedor_id:
        query = query.filter(Compra.fornecedor_id == fornecedor_id)
    if data_inicio:
        query = query.filter(Compra.data_compra >= data_inicio)
    if data_fim:
        query = query.filter(Compra.data_compra <= f"{data_fim} 23:59:59")
    
    # Ordenar e paginar
    compras = query.order_by(Compra.data_compra.desc()).offset(skip).limit(limit).all()
    return [compra.to_dict() for compra in compras]

@router.get("/{compra_id}", response_model=CompraSchema)
def obter_compra(
    compra_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtém os detalhes de uma compra específica.
    """
    compra = db.query(Compra).options(
        joinedload(Compra.itens),
        joinedload(Compra.fornecedor),
        joinedload(Compra.usuario)
    ).filter(Compra.id == compra_id).first()
    
    if not compra:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compra não encontrada"
        )
    
    return compra.to_dict()

@router.get("/itens/{item_id}", response_model=ItemCompraSchema)
def obter_item_compra(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtém os detalhes de um item de compra específico.
    """
    item = db.query(ItemCompra).filter(ItemCompra.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item de compra não encontrado"
        )
    return item.to_dict()
