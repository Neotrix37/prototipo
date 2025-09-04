from pydantic import BaseModel, Field, EmailStr, validator, ConfigDict
from typing import Optional, List, Any, Dict
from datetime import datetime
from enum import Enum

class NivelUsuario(str, Enum):
    BASICO = "basico"
    AVANCADO = "avancado"
    GERENTE = "gerente"

class UsuarioBase(BaseModel):
    """Base schema for user data."""
    nome: str = Field(..., max_length=100, description="Nome completo do usuário")
    usuario: str = Field(..., max_length=50, description="Nome de usuário para login")
    nivel: NivelUsuario = Field(default=NivelUsuario.BASICO, description="Nível de acesso do usuário")
    ativo: bool = Field(default=True, description="Indica se o usuário está ativo")
    is_admin: bool = Field(default=False, description="Indica se o usuário é administrador")
    salario: float = Field(default=0.0, ge=0, description="Salário do usuário")
    pode_abastecer: bool = Field(default=False, description="Indica se o usuário pode abastecer veículos")

    @validator('usuario')
    def usuario_maiusculo(cls, v):
        if v:
            return v.capitalize()
        return v
    
    model_config = ConfigDict(from_attributes=True)

class UsuarioCreate(UsuarioBase):
    """Schema for creating a new user."""
    senha: str = Field(..., min_length=6, max_length=100, description="Senha do usuário")

class UsuarioUpdate(BaseModel):
    """Schema for updating an existing user."""
    nome: Optional[str] = Field(None, max_length=100, description="Nome completo do usuário")
    usuario: Optional[str] = Field(None, max_length=50, description="Nome de usuário para login")
    senha: Optional[str] = Field(None, min_length=6, max_length=100, description="Nova senha do usuário")
    nivel: Optional[NivelUsuario] = Field(None, description="Nível de acesso do usuário")
    ativo: Optional[bool] = Field(None, description="Indica se o usuário está ativo")
    is_admin: Optional[bool] = Field(None, description="Indica se o usuário é administrador")
    salario: Optional[float] = Field(None, ge=0, description="Salário do usuário")
    pode_abastecer: Optional[bool] = Field(None, description="Indica se o usuário pode abastecer veículos")
    
    model_config = ConfigDict(from_attributes=True)

class UsuarioInDBBase(UsuarioBase):
    """Base schema for user data in the database."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def from_orm(cls, obj):
        # Make a copy of the object to avoid modifying the original
        obj_dict = {k: getattr(obj, k) for k in obj.__dict__ if not k.startswith('_')}
        return cls(**obj_dict)

class Usuario(UsuarioInDBBase):
    """Schema for returning user data (without sensitive information)."""
    pass

class UsuarioInDB(UsuarioInDBBase):
    """Schema for user data in the database (includes hashed password)."""
    hashed_password: str

# Authentication schemas
class Token(BaseModel):
    """Schema for authentication token."""
    access_token: str
    token_type: str
    user: Usuario
    
    model_config = ConfigDict(from_attributes=True)

class TokenData(BaseModel):
    """Schema for token data."""
    username: Optional[str] = None
    scopes: List[str] = []
    
    model_config = ConfigDict(from_attributes=True)

class UsuarioLogin(BaseModel):
    """Schema for user login."""
    username: str = Field(..., description="Nome de usuário")
    password: str = Field(..., description="Senha do usuário")
    
    model_config = ConfigDict(from_attributes=True)
