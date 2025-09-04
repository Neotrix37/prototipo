from datetime import datetime
from typing import List, Optional, ForwardRef
from pydantic import BaseModel, Field, ConfigDict

from app.schemas.base import CustomBaseModel

# Forward reference for Usuario to avoid circular imports
Usuario = ForwardRef('Usuario')

class ItemCompraBase(CustomBaseModel):
    """Base schema for purchase items."""
    produto_id: int = Field(..., description="ID do produto")
    produto_nome: str = Field(..., max_length=255, description="Nome do produto")
    quantidade: float = Field(..., gt=0, description="Quantidade do item")
    preco_unitario: float = Field(..., gt=0, description="Preço unitário do item")
    preco_venda: float = Field(..., gt=0, description="Preço de venda do item")

    class Config:
        from_attributes = True

class ItemCompraCreate(ItemCompraBase):
    """Schema for creating a purchase item."""
    pass

class ItemCompraUpdate(CustomBaseModel):
    """Schema for updating a purchase item."""
    quantidade: Optional[float] = Field(None, gt=0, description="Nova quantidade do item")
    preco_unitario: Optional[float] = Field(None, gt=0, description="Novo preço unitário")
    preco_venda: Optional[float] = Field(None, gt=0, description="Novo preço de venda")

    class Config:
        from_attributes = True

class ItemCompra(ItemCompraBase):
    """Schema for a purchase item with additional calculated fields."""
    id: int
    lucro_unitario: float
    lucro_total: float

    class Config:
        from_attributes = True

class CompraBase(CustomBaseModel):
    """Base schema for purchases."""
    fornecedor_id: int = Field(..., description="ID do fornecedor")
    observacoes: Optional[str] = Field(None, description="Observações sobre a compra")
    itens: List[ItemCompraCreate] = Field(..., min_items=1, description="Itens da compra")

    class Config:
        from_attributes = True

class CompraCreate(CompraBase):
    """Schema for creating a purchase."""
    pass

class CompraUpdate(CustomBaseModel):
    """Schema for updating a purchase."""
    fornecedor_id: Optional[int] = None
    observacoes: Optional[str] = None
    itens: Optional[List[ItemCompraUpdate]] = None

    class Config:
        from_attributes = True

class Compra(CompraBase):
    """Schema for a complete purchase with all details."""
    id: int
    valor_total: float
    usuario_id: int
    data_compra: datetime
    itens: List[ItemCompra] = []

    class Config:
        from_attributes = True

class CompraListagem(CustomBaseModel):
    """Schema for listing purchases (without detailed items)."""
    id: int
    fornecedor_id: int
    fornecedor_nome: str
    valor_total: float
    data_compra: datetime
    usuario_nome: str

    class Config:
        from_attributes = True
