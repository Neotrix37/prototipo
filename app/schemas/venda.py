from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from enum import Enum

class FormaPagamento(str, Enum):
    DINHEIRO = "Dinheiro"
    MPESA = "M-PESA"
    EMOLA = "E-Mola"
    CARTAO = "Cartão"
    TRANSFERENCIA = "Transferência"
    MILLENNIUM_BIM = "Millennium BIM"
    BCI = "BCI"
    STANDARD_BANK = "Standard Bank"
    ABSA_BANK = "ABSA Bank"
    LETSHEGO = "Letshego"
    MYBUCKS = "MyBucks"

class StatusVenda(str, Enum):
    CONCLUIDA = "concluida"
    PENDENTE = "pendente"
    CANCELADA = "cancelada"
    ESTORNADA = "estornada"

class ItemVendaBase(BaseModel):
    produto_id: int = Field(..., description="ID do produto vendido")
    quantidade: float = Field(..., gt=0, description="Quantidade vendida")
    preco_unitario: float = Field(..., gt=0, description="Preço unitário no momento da venda")
    desconto: float = Field(0.0, ge=0, description="Desconto aplicado no item")
    total: Optional[float] = Field(None, gt=0, description="Total do item (quantidade * preco_unitario - desconto)")

    @validator('total', always=True)
    def validate_total(cls, v, values):
        if v is None:
            # Calcula o total se não for fornecido
            if 'quantidade' in values and 'preco_unitario' in values and 'desconto' in values:
                return values['quantidade'] * values['preco_unitario'] - values['desconto']
        else:
            # Valida o total se fornecido
            if 'quantidade' in values and 'preco_unitario' in values and 'desconto' in values:
                expected = values['quantidade'] * values['preco_unitario'] - values['desconto']
                if abs(v - expected) > 0.01:  # Permite pequenas diferenças de arredondamento
                    raise ValueError(f"O total do item deve ser igual a (quantidade * preco_unitario - desconto). Esperado: {expected}, Recebido: {v}")
        return v

class ItemVendaCreate(ItemVendaBase):
    pass

class ItemVendaUpdate(BaseModel):
    """Schema para atualização de itens de venda."""
    produto_id: Optional[int] = Field(None, description="ID do produto vendido")
    quantidade: Optional[float] = Field(None, gt=0, description="Quantidade vendida")
    preco_unitario: Optional[float] = Field(None, gt=0, description="Preço unitário no momento da venda")
    desconto: Optional[float] = Field(None, ge=0, description="Desconto aplicado no item")
    total: Optional[float] = Field(None, gt=0, description="Total do item (quantidade * preco_unitario - desconto)")
    
    class Config:
        from_attributes = True

class ItemVenda(ItemVendaBase):
    id: int
    venda_id: int
    criado_em: datetime
    
    class Config:
        from_attributes = True

class VendaBase(BaseModel):
    cliente_id: Optional[int] = Field(None, description="ID do cliente (opcional)")
    itens: List[ItemVendaCreate] = Field(..., min_items=1, description="Itens da venda")
    desconto: float = Field(0.0, ge=0, description="Desconto total da venda")
    forma_pagamento: FormaPagamento = Field(..., description="Forma de pagamento")
    valor_recebido: Optional[float] = Field(None, ge=0, description="Valor recebido (para cálculo de troco)")
    observacoes: Optional[str] = Field(None, max_length=500, description="Observações adicionais")

class VendaCreate(VendaBase):
    pass

class VendaUpdate(BaseModel):
    status: Optional[StatusVenda] = Field(None, description="Novo status da venda")
    observacoes: Optional[str] = Field(None, max_length=500, description="Observações adicionais")
    forma_pagamento: Optional[FormaPagamento] = Field(None, description="Forma de pagamento")
    valor_recebido: Optional[float] = Field(None, ge=0, description="Valor recebido (para cálculo de troco)")

class VendaInDBBase(VendaBase):
    id: int
    usuario_id: int
    total: float = Field(..., gt=0, description="Total da venda (soma dos itens - desconto)")
    troco: float = Field(0.0, ge=0, description="Troco para o cliente")
    status: StatusVenda = Field(StatusVenda.CONCLUIDA, description="Status atual da venda")
    data_venda: datetime
    data_atualizacao: Optional[datetime] = None
    itens: List[ItemVenda] = Field(..., description="Itens da venda")
    
    class Config:
        from_attributes = True

class Venda(VendaInDBBase):
    pass

class VendaInDB(VendaInDBBase):
    pass
