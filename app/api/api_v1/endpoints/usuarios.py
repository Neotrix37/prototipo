from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ....core import security
from ....db.session import get_db
from ....models.usuario import Usuario
from ....schemas.usuario import (
    Usuario as UsuarioSchema,
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioInDB
)

router = APIRouter()

@router.get("/", response_model=List[UsuarioSchema])
async def listar_usuarios(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Usuario = Depends(security.get_current_active_user)
):
    """
    Lista todos os usuários (apenas para administradores).
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada"
        )
    
    usuarios = db.query(Usuario).offset(skip).limit(limit).all()
    return usuarios

@router.post("/", response_model=UsuarioSchema)
async def criar_usuario(
    *,
    db: Session = Depends(get_db),
    usuario_in: UsuarioCreate,
    current_user: Usuario = Depends(security.get_current_active_user)
):
    """
    Cria um novo usuário (apenas para administradores).
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada"
        )
    
    # Verifica se o usuário já existe
    usuario = db.query(Usuario).filter(Usuario.usuario == usuario_in.usuario).first()
    if usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um usuário com este nome de usuário"
        )
    
    # Cria o novo usuário
    hashed_password = security.get_password_hash(usuario_in.senha)
    db_usuario = Usuario(
        **usuario_in.dict(exclude={"senha"}),
        senha=hashed_password
    )
    
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    
    return db_usuario

@router.get("/{usuario_id}", response_model=UsuarioSchema)
async def obter_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(security.get_current_active_user)
):
    """
    Obtém informações de um usuário específico.
    """
    # Usuários comuns só podem ver seus próprios dados
    if not current_user.is_admin and current_user.id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada"
        )
    
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return usuario

@router.put("/{usuario_id}", response_model=UsuarioSchema)
async def atualizar_usuario(
    usuario_id: int,
    usuario_in: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(security.get_current_active_user)
):
    """
    Atualiza os dados de um usuário.
    """
    # Verifica permissões
    if not current_user.is_admin and current_user.id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada"
        )
    
    # Busca o usuário
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not db_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Atualiza os campos fornecidos
    update_data = usuario_in.dict(exclude_unset=True)
    
    # Se uma nova senha foi fornecida, faz o hash
    if "senha" in update_data and update_data["senha"]:
        hashed_password = security.get_password_hash(update_data["senha"])
        update_data["senha"] = hashed_password
    
    # Atualiza os campos
    for field, value in update_data.items():
        setattr(db_usuario, field, value)
    
    db.commit()
    db.refresh(db_usuario)
    
    return db_usuario

@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def excluir_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(security.get_current_active_superuser)
):
    """
    Exclui um usuário (apenas para superusuários).
    """
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not db_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Não permite excluir o próprio usuário
    if db_usuario.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível excluir seu próprio usuário"
        )
    
    db.delete(db_usuario)
    db.commit()
    
    return None
