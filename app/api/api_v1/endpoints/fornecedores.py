from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.fornecedor import Fornecedor as FornecedorModel
from app.schemas.fornecedor import Fornecedor, FornecedorCreate, FornecedorUpdate
from app.api.deps import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[Fornecedor])
def listar_fornecedores(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    ativo: Optional[bool] = None,
    current_user = Depends(get_current_active_user)
):
    """
    Lista todos os fornecedores com paginação e filtro por status ativo.
    """
    query = db.query(FornecedorModel)
    
    # Filtro por status ativo, se fornecido
    if ativo is not None:
        query = query.filter(FornecedorModel.ativo == ativo)
    
    # Ordena por nome e aplica paginação
    fornecedores = query.order_by(FornecedorModel.nome).offset(skip).limit(limit).all()
    return fornecedores

@router.post("/", response_model=Fornecedor, status_code=status.HTTP_201_CREATED)
def criar_fornecedor(
    *,
    db: Session = Depends(get_db),
    fornecedor_in: FornecedorCreate,
    current_user = Depends(get_current_active_user)
):
    """
    Cria um novo fornecedor.
    """
    # Verifica se já existe um fornecedor com o mesmo nome
    fornecedor_existente = (
        db.query(FornecedorModel)
        .filter(FornecedorModel.nome.ilike(fornecedor_in.nome))
        .first()
    )
    
    if fornecedor_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um fornecedor com este nome."
        )
    
    # Cria o novo fornecedor
    db_fornecedor = FornecedorModel(**fornecedor_in.model_dump())
    db.add(db_fornecedor)
    db.commit()
    db.refresh(db_fornecedor)
    
    return db_fornecedor

@router.get("/{fornecedor_id}", response_model=Fornecedor)
def obter_fornecedor(
    fornecedor_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Obtém os detalhes de um fornecedor pelo ID.
    """
    db_fornecedor = db.query(FornecedorModel).filter(FornecedorModel.id == fornecedor_id).first()
    
    if not db_fornecedor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fornecedor não encontrado."
        )
    
    return db_fornecedor

@router.put("/{fornecedor_id}", response_model=Fornecedor)
def atualizar_fornecedor(
    *,
    db: Session = Depends(get_db),
    fornecedor_id: int,
    fornecedor_in: FornecedorUpdate,
    current_user = Depends(get_current_active_user)
):
    """
    Atualiza os dados de um fornecedor existente.
    """
    db_fornecedor = db.query(FornecedorModel).filter(FornecedorModel.id == fornecedor_id).first()
    
    if not db_fornecedor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fornecedor não encontrado."
        )
    
    # Atualiza apenas os campos fornecidos
    update_data = fornecedor_in.model_dump(exclude_unset=True)
    
    # Verifica se o novo nome já está em uso por outro fornecedor
    if "nome" in update_data:
        fornecedor_existente = (
            db.query(FornecedorModel)
            .filter(
                FornecedorModel.nome.ilike(update_data["nome"]),
                FornecedorModel.id != fornecedor_id
            )
            .first()
        )
        
        if fornecedor_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe outro fornecedor com este nome."
            )
    
    # Atualiza os campos
    for field, value in update_data.items():
        setattr(db_fornecedor, field, value)
    
    db.commit()
    db.refresh(db_fornecedor)
    
    return db_fornecedor

@router.delete("/{fornecedor_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_fornecedor(
    *,
    db: Session = Depends(get_db),
    fornecedor_id: int,
    current_user = Depends(get_current_active_user)
):
    """
    Exclui um fornecedor (exclusão lógica - marca como inativo).
    """
    db_fornecedor = db.query(FornecedorModel).filter(FornecedorModel.id == fornecedor_id).first()
    
    if not db_fornecedor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fornecedor não encontrado."
        )
    
    # Verifica se existem produtos associados a este fornecedor
    if db_fornecedor.produtos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível excluir um fornecedor que possui produtos associados."
        )
    
    # Remove o fornecedor do banco de dados
    db.delete(db_fornecedor)
    db.commit()
    
    return None
