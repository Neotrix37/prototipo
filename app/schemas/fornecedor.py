from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class FornecedorBase(BaseModel):
    nome: str = Field(..., max_length=100, description="Nome do fornecedor")
    telefone: Optional[str] = Field(None, max_length=20, description="Telefone para contato")
    email: Optional[str] = Field(None, max_length=100, description="E-mail para contato")
    endereco: Optional[str] = Field(None, description="Endereço completo do fornecedor")
    ativo: bool = Field(True, description="Indica se o fornecedor está ativo")

class FornecedorCreate(FornecedorBase):
    pass

class FornecedorUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=100, description="Nome do fornecedor")
    telefone: Optional[str] = Field(None, max_length=20, description="Telefone para contato")
    email: Optional[str] = Field(None, max_length=100, description="E-mail para contato")
    endereco: Optional[str] = Field(None, description="Endereço completo do fornecedor")
    ativo: Optional[bool] = Field(None, description="Indica se o fornecedor está ativo")

class FornecedorInDBBase(FornecedorBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Nova sintaxe do Pydantic v2
    model_config = ConfigDict(from_attributes=True)

class Fornecedor(FornecedorInDBBase):
    pass

class FornecedorInDB(FornecedorInDBBase):
    pass
