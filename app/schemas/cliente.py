from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional
from datetime import datetime

class ClienteBase(BaseModel):
    nome: str = Field(..., max_length=100, description="Nome completo do cliente")
    nuit: Optional[str] = Field(None, max_length=20, description="Número de Identificação Tributária")
    telefone: Optional[str] = Field(None, max_length=20, description="Número de telefone do cliente")
    email: Optional[EmailStr] = Field(None, description="Endereço de e-mail do cliente")
    endereco: Optional[str] = Field(None, max_length=300, description="Endereço do cliente")
    especial: bool = Field(default=False, description="Indica se o cliente é especial")
    desconto_divida: float = Field(default=0.0, ge=0, description="Valor de desconto em dívida para o cliente")

    @validator('nuit')
    def validate_nuit(cls, v):
        if v and not v.isdigit():
            raise ValueError("O NUIT deve conter apenas números")
        return v

class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=100, description="Nome completo do cliente")
    nuit: Optional[str] = Field(None, max_length=20, description="Número de Identificação Tributária")
    telefone: Optional[str] = Field(None, max_length=20, description="Número de telefone do cliente")
    email: Optional[EmailStr] = Field(None, description="Endereço de e-mail do cliente")
    endereco: Optional[str] = Field(None, max_length=300, description="Endereço do cliente")
    especial: Optional[bool] = Field(None, description="Indica se o cliente é especial")
    desconto_divida: Optional[float] = Field(None, ge=0, description="Valor de desconto em dívida para o cliente")

class ClienteInDBBase(ClienteBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Cliente(ClienteInDBBase):
    pass

class ClienteInDB(ClienteInDBBase):
    pass
