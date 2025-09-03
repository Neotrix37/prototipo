from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ....core import security
from ....db.session import get_db
from ....models.cliente import Cliente as ClienteModel
from ....schemas.cliente import Cliente, ClienteCreate, ClienteUpdate, ClienteInDB

router = APIRouter()

@router.get("/", response_model=List[Cliente])
def listar_clientes(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    nome: Optional[str] = None,
    nuit: Optional[str] = None,
    especial: Optional[bool] = None,
    current_user = Depends(security.get_current_active_user)
):
    """
    Lista os clientes com filtros opcionais.
    """
    query = db.query(ClienteModel)
    
    if nome:
        query = query.filter(ClienteModel.nome.ilike(f"%{nome}%"))
    if nuit:
        query = query.filter(ClienteModel.nuit == nuit)
    if especial is not None:
        query = query.filter(ClienteModel.especial == especial)
    
    return query.offset(skip).limit(limit).all()

@router.post("/", response_model=Cliente, status_code=status.HTTP_201_CREATED)
def criar_cliente(
    *,
    db: Session = Depends(get_db),
    cliente_in: ClienteCreate,
    current_user = Depends(security.get_current_active_user)
):
    """
    Cria um novo cliente.
    """
    # Verifica se já existe um cliente com o mesmo NUIT
    if cliente_in.nuit:
        db_cliente = db.query(ClienteModel).filter(
            ClienteModel.nuit == cliente_in.nuit
        ).first()
        if db_cliente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um cliente com este NUIT."
            )
    
    # Cria o cliente
    db_cliente = ClienteModel(**cliente_in.dict())
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

@router.get("/{cliente_id}", response_model=Cliente)
def obter_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(security.get_current_active_user)
):
    """
    Obtém um cliente pelo seu ID.
    """
    db_cliente = db.query(ClienteModel).filter(ClienteModel.id == cliente_id).first()
    if not db_cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado."
        )
    return db_cliente

@router.put("/{cliente_id}", response_model=Cliente)
def atualizar_cliente(
    cliente_id: int,
    cliente_in: ClienteUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(security.get_current_active_user)
):
    """
    Atualiza um cliente existente.
    """
    db_cliente = db.query(ClienteModel).filter(ClienteModel.id == cliente_id).first()
    if not db_cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado."
        )
    
    # Verifica se o NUIT já está em uso por outro cliente
    if cliente_in.nuit and cliente_in.nuit != db_cliente.nuit:
        existing_cliente = db.query(ClienteModel).filter(
            ClienteModel.nuit == cliente_in.nuit,
            ClienteModel.id != cliente_id
        ).first()
        if existing_cliente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe outro cliente com este NUIT."
            )
    
    # Atualiza os campos fornecidos
    update_data = cliente_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_cliente, field, value)
    
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(security.get_current_active_user)
):
    """
    Exclui um cliente.
    """
    db_cliente = db.query(ClienteModel).filter(ClienteModel.id == cliente_id).first()
    if not db_cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado."
        )
    
    # Verifica se o cliente tem vendas associadas
    if db_cliente.vendas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível excluir um cliente que possui vendas associadas."
        )
    
    db.delete(db_cliente)
    db.commit()
    return None
