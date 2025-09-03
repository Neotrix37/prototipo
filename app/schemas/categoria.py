from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CategoriaBase(BaseModel):
    nome: str = Field(..., max_length=100, description="Nome da categoria")
    descricao: Optional[str] = Field(None, description="Descrição detalhada da categoria")

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=100, description="Nome da categoria")
    descricao: Optional[str] = Field(None, description="Descrição detalhada da categoria")

class CategoriaInDBBase(CategoriaBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class Categoria(CategoriaInDBBase):
    pass

class CategoriaInDB(CategoriaInDBBase):
    pass
