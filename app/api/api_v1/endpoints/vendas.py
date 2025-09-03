from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.exc import SQLAlchemyError

from ....core import security
from ....db.session import get_db
from ....models.venda import Venda as VendaModel
from ....models.item_venda import ItemVenda as ItemVendaModel
from ....models.produtos import Produto as ProdutoModel
from ....models.cliente import Cliente as ClienteModel
from ....schemas.venda import (
    Venda, VendaCreate, VendaUpdate, VendaInDB,
    ItemVenda, ItemVendaCreate, StatusVenda, FormaPagamento
)

router = APIRouter()

def calcular_troco(total: float, valor_recebido: float) -> float:
    """Calcula o troco com base no total e no valor recebido."""
    if valor_recebido is None:
        return 0.0
    return max(0.0, round(valor_recebido - total, 2))

@router.get("/", response_model=List[Venda])
def listar_vendas(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[StatusVenda] = None,
    cliente_id: Optional[int] = None,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    current_user = Depends(security.get_current_active_user)
):
    """
    Lista as vendas com filtros opcionais.
    """
    query = db.query(VendaModel).options(
        joinedload(VendaModel.itens).joinedload(ItemVendaModel.produto),
        joinedload(VendaModel.cliente),
        joinedload(VendaModel.usuario)
    )
    
    # Aplicar filtros
    if status:
        query = query.filter(VendaModel.status == status)
    if cliente_id:
        query = query.filter(VendaModel.cliente_id == cliente_id)
    if data_inicio:
        query = query.filter(VendaModel.data_venda >= data_inicio)
    if data_fim:
        # Adiciona 1 dia para incluir o dia final
        query = query.filter(VendaModel.data_venda <= f"{data_fim} 23:59:59")
    
    # Ordenar e paginar
    vendas = query.order_by(VendaModel.data_venda.desc()).offset(skip).limit(limit).all()
    
    # Converter para dicionário usando o método to_dict() de cada venda
    return [venda.to_dict() for venda in vendas]

@router.post("/", response_model=Venda, status_code=status.HTTP_201_CREATED)
def criar_venda(
    *,
    db: Session = Depends(get_db),
    venda_in: VendaCreate,
    current_user = Depends(security.get_current_active_user)
):
    """
    Cria uma nova venda.
    """
    try:
        db.begin()
        
        # Verifica se o cliente existe
        if venda_in.cliente_id:
            cliente = db.query(ClienteModel).filter(ClienteModel.id == venda_in.cliente_id).first()
            if not cliente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cliente não encontrado."
                )
        
        # Calcula o total da venda
        total_itens = 0.0
        itens_venda = []
        
        for item_in in venda_in.itens:
            # Verifica se o produto existe e tem estoque suficiente
            produto = db.query(ProdutoModel).filter(ProdutoModel.id == item_in.produto_id).first()
            if not produto:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Produto com ID {item_in.produto_id} não encontrado."
                )
            
            if produto.estoque < item_in.quantidade:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Estoque insuficiente para o produto {produto.nome}. Estoque atual: {produto.estoque}"
                )
            
            # Atualiza o estoque
            produto.estoque -= item_in.quantidade
            db.add(produto)
            
            # Adiciona ao total
            total_item = item_in.quantidade * item_in.preco_unitario - item_in.desconto
            total_itens += total_item
            
            # Prepara o item para ser salvo
            item_dict = item_in.dict()
            item_dict["total"] = total_item
            itens_venda.append(item_dict)
        
        # Aplica desconto geral, se houver
        total_venda = max(0, total_itens - venda_in.desconto)
        
        # Calcula o troco
        troco = 0.0
        if venda_in.forma_pagamento == FormaPagamento.DINHEIRO and venda_in.valor_recebido:
            troco = calcular_troco(total_venda, venda_in.valor_recebido)
        
        # Cria a venda
        venda_dict = venda_in.dict(exclude={"itens"})
        venda_dict.update({
            "usuario_id": current_user.id,
            "total": total_venda,
            "troco": troco,
            "status": StatusVenda.CONCLUIDA
        })
        
        db_venda = VendaModel(**venda_dict)
        db.add(db_venda)
        db.flush()  # Para obter o ID da venda
        
        # Cria os itens da venda
        for item in itens_venda:
            item["venda_id"] = db_venda.id
            # Garante que o total está presente no item antes de criar o ItemVendaModel
            if "total" not in item:
                item["total"] = item["quantidade"] * item["preco_unitario"] - item["desconto"]
            db_item = ItemVendaModel(**item)
            db.add(db_item)
        
        db.commit()
        
        # Recarrega a venda com todos os relacionamentos
        db_venda = (
            db.query(VendaModel)
            .options(
                joinedload(VendaModel.itens)
                .joinedload(ItemVendaModel.produto)
            )
            .filter(VendaModel.id == db_venda.id)
            .first()
        )
        
        if not db_venda:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao recuperar os dados da venda."
            )
            
        # Usa o método to_dict() do modelo para serializar
        return db_venda.to_dict()
        
    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar a venda: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro inesperado ao processar a venda: {str(e)}"
        )

@router.get("/{venda_id}", response_model=Venda)
def obter_venda(
    venda_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(security.get_current_active_user)
):
    """
    Obtém uma venda pelo seu ID.
    """
    db_venda = db.query(VendaModel).filter(VendaModel.id == venda_id).first()
    if not db_venda:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venda não encontrada."
        )
    return db_venda

@router.put("/{venda_id}/status", response_model=Venda)
def atualizar_status_venda(
    venda_id: int,
    venda_update: VendaUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(security.get_current_active_user)
):
    """
    Atualiza o status de uma venda.
    """
    db_venda = db.query(VendaModel).filter(VendaModel.id == venda_id).first()
    if not db_venda:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venda não encontrada."
        )
    
    # Atualiza os campos fornecidos
    update_data = venda_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_venda, field, value)
    
    db.commit()
    db.refresh(db_venda)
    return db_venda

@router.delete("/{venda_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancelar_venda(
    venda_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(security.get_current_active_user)
):
    """
    Cancela uma venda e estorna os itens ao estoque.
    """
    db_venda = db.query(VendaModel).filter(VendaModel.id == venda_id).first()
    if not db_venda:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venda não encontrada."
        )
    
    if db_venda.status == StatusVenda.CANCELADA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta venda já foi cancelada."
        )
    
    # Inicia uma transação
    try:
        db.begin()
        
        # Estorna os itens ao estoque
        for item in db_venda.itens:
            produto = db.query(ProdutoModel).filter(ProdutoModel.id == item.produto_id).first()
            if produto:
                produto.estoque += item.quantidade
                db.add(produto)
        
        # Atualiza o status da venda
        db_venda.status = StatusVenda.CANCELADA
        db.add(db_venda)
        
        db.commit()
        return None
        
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao cancelar a venda: {str(e)}"
        )
