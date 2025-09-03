from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings  
from app.db.session import SessionLocal
from app.models import Usuario
from app.core import security  # Import security module

# Configuração do esquema OAuth2 para autenticação via token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def get_db() -> Generator:
    """
    Fornece uma sessão do banco de dados.
    
    Esta função é usada como dependência em rotas que precisam de acesso ao banco de dados.
    Garante que a sessão seja fechada corretamente após o uso.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_active_user(
    current_user: Usuario = Depends(security.get_current_user),
) -> Usuario:
    """
    Verifica se o usuário atual está ativo.
    
    Args:
        current_user: O usuário autenticado
        
    Returns:
        Usuario: O usuário se estiver ativo
        
    Raises:
        HTTPException: Se o usuário estiver inativo
    """
    if not current_user.ativo:
        raise HTTPException(status_code=400, detail="Usuário inativo")
    return current_user

def get_current_active_superuser(
    current_user: Usuario = Depends(security.get_current_user),
) -> Usuario:
    """
    Verifica se o usuário atual é um superusuário.
    
    Args:
        current_user: O usuário autenticado
        
    Returns:
        Usuario: O usuário se for superusuário
        
    Raises:
        HTTPException: Se o usuário não for superusuário
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="O usuário não tem privilégios suficientes"
        )
    return current_user
