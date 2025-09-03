from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional
from datetime import datetime

class ProdutoBase(BaseModel):
    codigo: str = Field(..., max_length=50, description="Código único do produto")
    nome: str = Field(..., max_length=100, description="Nome do produto")
    descricao: Optional[str] = Field(None, max_length=500, description="Descrição detalhada do produto")
    preco_custo: float = Field(..., gt=0, description="Preço de custo do produto")
    preco_venda: float = Field(..., gt=0, description="Preço de venda do produto")
    estoque: float = Field(0.0, ge=0, description="Quantidade atual em estoque")
    estoque_minimo: float = Field(0.0, ge=0, description="Quantidade mínima em estoque para alerta")
    ativo: bool = Field(True, description="Indica se o produto está ativo")
    venda_por_peso: bool = Field(False, description="Indica se o produto é vendido por peso")
    unidade_medida: str = Field('un', max_length=10, description="Unidade de medida (ex: 'un', 'kg', 'g', 'l')")
    categoria_id: Optional[int] = Field(None, description="ID da categoria do produto")
    fornecedor_id: int = Field(1, description="ID do fornecedor do produto")

    @validator('preco_venda')
    def preco_venda_maior_que_custo(cls, v, values):
        if 'preco_custo' in values and v < values['preco_custo']:
            raise ValueError('O preço de venda não pode ser menor que o preço de custo')
        return v

class ProdutoCreate(ProdutoBase):
    pass

class ProdutoUpdate(BaseModel):
    codigo: Optional[str] = Field(None, max_length=50, description="Código único do produto")
    nome: Optional[str] = Field(None, max_length=100, description="Nome do produto")
    descricao: Optional[str] = Field(None, max_length=500, description="Descrição detalhada do produto")
    preco_custo: Optional[float] = Field(None, gt=0, description="Preço de custo do produto")
    preco_venda: Optional[float] = Field(None, gt=0, description="Preço de venda do produto")
    estoque: Optional[float] = Field(None, ge=0, description="Quantidade atual em estoque")
    estoque_minimo: Optional[float] = Field(None, ge=0, description="Quantidade mínima em estoque para alerta")
    ativo: Optional[bool] = Field(None, description="Indica se o produto está ativo")
    venda_por_peso: Optional[bool] = Field(None, description="Indica se o produto é vendido por peso")
    unidade_medida: Optional[str] = Field(None, max_length=10, description="Unidade de medida (ex: 'un', 'kg', 'g', 'l')")
    categoria_id: Optional[int] = Field(None, description="ID da categoria do produto")
    fornecedor_id: Optional[int] = Field(None, description="ID do fornecedor do produto")

class ProdutoInDBBase(ProdutoBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Nova sintaxe do Pydantic v2
    model_config = ConfigDict(from_attributes=True)

class Produto(ProdutoInDBBase):
    pass

class ProdutoInDB(ProdutoInDBBase):
    pass
