from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ....core import security
from ....db.session import get_db
from ....models.item_venda import ItemVenda as ItemVendaModel
from ....models.venda import Venda as VendaModel
from ....models.produtos import Produto as ProdutoModel
from ....schemas.venda import ItemVenda, ItemVendaCreate, ItemVendaUpdate

router = APIRouter()

def atualizar_estoque_produto(db: Session, produto_id: int, quantidade: float, operacao: str = 'adicionar'):
    """Atualiza o estoque de um produto."""
    produto = db.query(ProdutoModel).filter(ProdutoModel.id == produto_id).first()
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produto com ID {produto_id} não encontrado."
        )
    
    if operacao == 'adicionar':
        produto.estoque += quantidade
    else:  # remover
        if produto.estoque < quantidade:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estoque insuficiente para o produto {produto.nome}. Estoque atual: {produto.estoque}"
            )
        produto.estoque -= quantidade
    
    db.add(produto)
    return produto

@router.post("/vendas/{venda_id}/itens", response_model=ItemVenda, status_code=status.HTTP_201_CREATED)
def adicionar_item_venda(
    venda_id: int,
    item_in: ItemVendaCreate,
    db: Session = Depends(get_db),
    current_user = Depends(security.get_current_active_user)
):
    """
    Adiciona um item a uma venda existente.
    """
    # Verifica se a venda existe e está em um estado válido
    venda = db.query(VendaModel).filter(VendaModel.id == venda_id).first()
    if not venda:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venda não encontrada."
        )
    
    if venda.status != 'pendente':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Só é possível adicionar itens a vendas pendentes."
        )
    
    # Verifica se o produto existe e tem estoque suficiente
    produto = db.query(ProdutoModel).filter(ProdutoModel.id == item_in.produto_id).first()
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produto com ID {item_in.produto_id} não encontrado."
        )
    
    if produto.estoque < item_in.quantidade:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estoque insuficiente para o produto {produto.nome}. Estoque atual: {produto.estoque}"
        )
    
    # Inicia uma transação
    try:
        db.begin()
        
        # Calcula o total do item
        total_item = item_in.quantidade * item_in.preco_unitario - item_in.desconto
        
        # Cria o item da venda
        item_dict = item_in.dict()
        item_dict.update({
            "venda_id": venda_id,
            "total": total_item
        })
        
        db_item = ItemVendaModel(**item_dict)
        db.add(db_item)
        
        # Atualiza o estoque
        produto.estoque -= item_in.quantidade
        db.add(produto)
        
        # Atualiza o total da venda
        venda.total += total_item
        db.add(venda)
        
        db.commit()
        db.refresh(db_item)
        
        return db_item
        
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao adicionar item à venda: {str(e)}"
        )

@router.put("/itens/{item_id}", response_model=ItemVenda)
def atualizar_item_venda(
    item_id: int,
    item_update: ItemVendaUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(security.get_current_active_user)
):
    """
    Atualiza um item de venda existente.
    """
    db_item = db.query(ItemVendaModel).filter(ItemVendaModel.id == item_id).first()
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item de venda não encontrado."
        )
    
    # Verifica se a venda está em um estado válido
    venda = db.query(VendaModel).filter(VendaModel.id == db_item.venda_id).first()
    if not venda or venda.status != 'pendente':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Só é possível atualizar itens de vendas pendentes."
        )
    
    # Inicia uma transação
    try:
        db.begin()
        
        # Armazena os valores antigos para ajuste de estoque
        old_quantidade = db_item.quantidade
        old_produto_id = db_item.produto_id
        
        # Atualiza os campos fornecidos
        update_data = item_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_item, field, value)
        
        # Recalcula o total do item
        if 'quantidade' in update_data or 'preco_unitario' in update_data or 'desconto' in update_data:
            db_item.total = db_item.quantidade * db_item.preco_unitario - db_item.desconto
        
        # Atualiza o estoque se a quantidade ou o produto foram alterados
        if 'quantidade' in update_data or 'produto_id' in update_data:
            # Estorna o estoque do produto antigo
            if old_produto_id != db_item.produto_id:
                # Estorna o produto antigo
                produto_antigo = db.query(ProdutoModel).filter(ProdutoModel.id == old_produto_id).first()
                if produto_antigo:
                    produto_antigo.estoque += old_quantidade
                    db.add(produto_antigo)
                
                # Busca o novo produto
                produto_novo = db.query(ProdutoModel).filter(ProdutoModel.id == db_item.produto_id).first()
                if not produto_novo:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Produto com ID {db_item.produto_id} não encontrado."
                    )
                
                # Verifica se há estoque suficiente no novo produto
                if produto_novo.estoque < db_item.quantidade:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Estoque insuficiente para o produto {produto_novo.nome}. Estoque atual: {produto_novo.estoque}"
                    )
                
                # Atualiza o estoque do novo produto
                produto_novo.estoque -= db_item.quantidade
                db.add(produto_novo)
            else:
                # Apenas a quantidade foi alterada
                diferenca = old_quantidade - db_item.quantidade
                produto = db.query(ProdutoModel).filter(ProdutoModel.id == db_item.produto_id).first()
                if produto:
                    if diferenca > 0:  # Aumenta o estoque
                        produto.estoque += diferenca
                    else:  # Diminui o estoque
                        if produto.estoque < abs(diferenca):
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Estoque insuficiente para o produto {produto.nome}. Estoque atual: {produto.estoque}"
                            )
                        produto.estoque -= abs(diferenca)
                    db.add(produto)
        
        # Atualiza o total da venda
        venda.total = sum(item.total for item in venda.itens)
        db.add(venda)
        
        db.commit()
        db.refresh(db_item)
        
        return db_item
        
    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar o item de venda: {str(e)}"
        )

@router.delete("/itens/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_item_venda(
    item_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(security.get_current_active_user)
):
    """
    Remove um item de venda existente.
    """
    db_item = db.query(ItemVendaModel).filter(ItemVendaModel.id == item_id).first()
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item de venda não encontrado."
        )
    
    # Verifica se a venda está em um estado válido
    venda = db.query(VendaModel).filter(VendaModel.id == db_item.venda_id).first()
    if not venda or venda.status != 'pendente':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Só é possível remover itens de vendas pendentes."
        )
    
    # Inicia uma transação
    try:
        db.begin()
        
        # Atualiza o estoque
        produto = db.query(ProdutoModel).filter(ProdutoModel.id == db_item.produto_id).first()
        if produto:
            produto.estoque += db_item.quantidade
            db.add(produto)
        
        # Remove o item
        db.delete(db_item)
        
        # Atualiza o total da venda
        venda.total = sum(item.total for item in venda.itens if item.id != item_id)
        db.add(venda)
        
        db.commit()
        return None
        
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao remover o item de venda: {str(e)}"
        )
