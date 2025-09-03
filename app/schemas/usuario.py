from pydantic import BaseModel, Field, EmailStr, validator, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum

class NivelUsuario(str, Enum):
    BASICO = "basico"
    AVANCADO = "avancado"
    GERENTE = "gerente"

class UsuarioBase(BaseModel):
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

class UsuarioCreate(UsuarioBase):
    senha: str = Field(..., min_length=6, max_length=100, description="Senha do usuário")

class UsuarioUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=100, description="Nome completo do usuário")
    usuario: Optional[str] = Field(None, max_length=50, description="Nome de usuário para login")
    senha: Optional[str] = Field(None, min_length=6, max_length=100, description="Nova senha do usuário")
    nivel: Optional[NivelUsuario] = Field(None, description="Nível de acesso do usuário")
    ativo: Optional[bool] = Field(None, description="Indica se o usuário está ativo")
    is_admin: Optional[bool] = Field(None, description="Indica se o usuário é administrador")
    salario: Optional[float] = Field(None, ge=0, description="Salário do usuário")
    pode_abastecer: Optional[bool] = Field(None, description="Indica se o usuário pode abastecer veículos")

class UsuarioInDBBase(UsuarioBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Nova sintaxe do Pydantic v2
    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def from_orm(cls, obj):
        # Make a copy of the object to avoid modifying the original
        obj_dict = {k: getattr(obj, k) for k in obj.__dict__ if not k.startswith('_')}
        
        # Handle the nivel field
        if hasattr(obj, 'nivel') and obj.nivel is not None:
            if isinstance(obj.nivel, NivelUsuario):
                obj_dict['nivel'] = obj.nivel
            elif isinstance(obj.nivel, int):
                try:
                    obj_dict['nivel'] = list(NivelUsuario)[obj.nivel - 1]
                except IndexError:
                    obj_dict['nivel'] = NivelUsuario.BASICO
        
        return cls.model_validate(obj_dict)

class Usuario(UsuarioInDBBase):
    pass

class UsuarioInDB(UsuarioInDBBase):
    hashed_password: str

# Esquema para autenticação
class Token(BaseModel):
    access_token: str
    token_type: str
    user: Usuario

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []

class UsuarioLogin(BaseModel):
    username: str = Field(..., description="Nome de usuário")
    password: str = Field(..., description="Senha do usuário")
