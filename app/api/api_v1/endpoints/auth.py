from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ....core import security
from ....core.config import settings
from ....db.session import get_db
from ....models.usuario import Usuario as UsuarioModel
from ....schemas.usuario import Token, UsuarioLogin, Usuario

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Autentica um usuário e retorna um token de acesso.
    """
    # Busca o usuário no banco de dados
    user = db.query(UsuarioModel).filter(UsuarioModel.usuario == form_data.username).first()
    
    # Verifica se o usuário existe e a senha está correta
    if not user or not security.verify_password(form_data.password, user.senha):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verifica se o usuário está ativo
    if not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário inativo"
        )
    
    # Cria o token de acesso
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.usuario}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": Usuario.from_orm(user)
    }

@router.post("/login/test-token", response_model=dict)
async def test_token(
    current_user: Usuario = Depends(security.get_current_user)
):
    """
    Testa se o token de acesso é válido.
    """
    return {"message": "Token válido", "usuario": current_user.usuario}
