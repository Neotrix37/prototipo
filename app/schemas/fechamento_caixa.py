from datetime import datetime
from typing import List, Optional, ForwardRef
from pydantic import Field, ConfigDict

from app.schemas.base import CustomBaseModel

# Forward reference for Usuario to avoid circular imports
Usuario = ForwardRef('Usuario')

class FechamentoFormaPagamentoBase(CustomBaseModel):
    """Base schema for payment methods in cash closing."""
    forma_pagamento_id: int = Field(..., description="ID da forma de pagamento")
    valor: float = Field(..., gt=0, description="Valor total da forma de pagamento")
    
    model_config = ConfigDict(from_attributes=True)

class FechamentoFormaPagamentoCreate(FechamentoFormaPagamentoBase):
    """Schema for creating a new payment method in cash closing."""
    pass

class FechamentoFormaPagamento(FechamentoFormaPagamentoBase):
    """Complete schema for a payment method in cash closing."""
    id: int
    fechamento_id: int
    forma_pagamento: 'FormaPagamento'
    
    model_config = ConfigDict(from_attributes=True)

class FechamentoCaixaBase(CustomBaseModel):
    """Base schema for cash closing."""
    valor_sistema: float = Field(..., gt=0, description="Valor total no sistema")
    valor_informado: float = Field(..., gt=0, description="Valor informado em espécie")
    observacoes: Optional[str] = Field(None, max_length=1000, description="Observações sobre o fechamento")
    
    model_config = ConfigDict(from_attributes=True)

class FechamentoCaixaCreate(FechamentoCaixaBase):
    """Schema for creating a new cash closing."""
    formas_pagamento: List[FechamentoFormaPagamentoCreate] = Field(
        ..., 
        min_items=1, 
        description="Formas de pagamento"
    )

class FechamentoCaixaUpdate(CustomBaseModel):
    """Schema for updating a cash closing."""
    observacoes: Optional[str] = Field(None, max_length=1000, description="Novas observações")
    status: Optional[str] = Field(None, description="Novo status do fechamento")
    
    model_config = ConfigDict(from_attributes=True)

class FechamentoCaixa(FechamentoCaixaBase):
    """Complete schema for a cash closing."""
    id: int
    diferenca: float
    status: str
    data_abertura: datetime
    data_fechamento: Optional[datetime] = None
    usuario_id: int
    usuario: Usuario
    formas_pagamento: List[FechamentoFormaPagamento] = []
    
    model_config = ConfigDict(from_attributes=True)

# Update forward references
FechamentoFormaPagamento.model_rebuild()
FechamentoCaixa.model_rebuild()
