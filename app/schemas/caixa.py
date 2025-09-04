from datetime import datetime
from enum import Enum
from typing import Optional, List, ForwardRef, Type, Any, Dict, Union, TYPE_CHECKING
from pydantic import Field, validator, ConfigDict, field_validator

from app.schemas.base import CustomBaseModel

# Import Usuario only for type checking
if TYPE_CHECKING:
    from app.schemas.usuario import Usuario

# Forward reference for Usuario
UsuarioModel = ForwardRef('Usuario')

class StatusRetirada(str, Enum):
    """Status de uma retirada de caixa."""
    PENDENTE = "pendente"
    APROVADO = "aprovado"
    REJEITADO = "rejeitado"
    CANCELADO = "cancelado"

class OrigemRetirada(str, Enum):
    """Origem de uma retirada de caixa."""
    CAIXA = "caixa"
    CONTA_BANCARIA = "conta_bancaria"
    OUTRO = "outro"

class MovimentacaoCaixaBase(CustomBaseModel):
    """Base schema para movimentações de caixa."""
    tipo: str = Field(..., description="Tipo de movimentação (ENTRADA/SAIDA)")
    valor: float = Field(..., gt=0, description="Valor da movimentação")
    descricao: str = Field(..., max_length=255, description="Descrição da movimentação")
    observacao: Optional[str] = Field(None, max_length=500, description="Observações adicionais")
    
    @field_validator('tipo')
    @classmethod
    def validate_tipo(cls, v: str) -> str:
        """Valida e normaliza o tipo de movimentação para maiúsculas."""
        if not isinstance(v, str):
            raise ValueError("O tipo deve ser uma string")
        v = v.upper().strip()
        if v not in ('ENTRADA', 'SAIDA'):
            raise ValueError("Tipo de movimentação deve ser 'ENTRADA' ou 'SAIDA'")
        return v
    
    model_config = ConfigDict(from_attributes=True)

class MovimentacaoCaixaCreate(MovimentacaoCaixaBase):
    """Schema para criação de uma nova movimentação de caixa."""
    pass

class MovimentacaoCaixaUpdate(CustomBaseModel):
    """Schema para atualização de uma movimentação de caixa."""
    descricao: Optional[str] = Field(None, max_length=255, description="Nova descrição da movimentação")
    observacao: Optional[str] = Field(None, max_length=500, description="Novas observações")
    
    model_config = ConfigDict(from_attributes=True)

class MovimentacaoCaixa(CustomBaseModel):
    """Schema completo para uma movimentação de caixa."""
    id: int
    tipo: str  # Will be "ENTRADA" or "SAIDA"
    valor: float
    descricao: str
    observacao: Optional[str] = None
    data_movimentacao: str  # ISO format string
    usuario_id: int
    usuario_nome: Optional[str] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "tipo": "ENTRADA",
                "valor": 100.0,
                "descricao": "Venda de produtos",
                "observacao": "Pagamento em dinheiro",
                "data_movimentacao": "2025-09-04T00:00:00",
                "usuario_id": 1,
                "usuario_nome": "Administrador do Sistema"
            }
        }
    )

class RetiradaCaixaBase(CustomBaseModel):
    """Base schema para retiradas de caixa."""
    valor: float = Field(..., gt=0, description="Valor da retirada")
    motivo: str = Field(..., max_length=255, description="Motivo da retirada")
    observacao: Optional[str] = Field(None, max_length=500, description="Observações adicionais")
    origem: OrigemRetirada = Field(default=OrigemRetirada.CAIXA, description="Origem dos recursos")
    
    model_config = ConfigDict(from_attributes=True)

class RetiradaCaixaCreate(RetiradaCaixaBase):
    """Schema para criação de uma nova retirada de caixa."""
    pass

class RetiradaCaixaAprovar(CustomBaseModel):
    """Schema para aprovação/rejeição de uma retirada de caixa."""
    aprovar: bool = Field(..., description="True para aprovar, False para rejeitar")
    motivo: Optional[str] = Field(None, max_length=500, description="Motivo da rejeição (obrigatório se aprovar=False)")
    
    @validator('motivo')
    def validate_motivo(cls, v, values):
        if not values.get('aprovar', True) and not v:
            raise ValueError("Motivo é obrigatório para rejeitar uma retirada")
        return v
    
    model_config = ConfigDict(from_attributes=True)

class RetiradaCaixa(RetiradaCaixaBase):
    """Schema completo para uma retirada de caixa."""
    id: int
    status: StatusRetirada
    data_retirada: datetime
    data_aprovacao: Optional[datetime] = None
    usuario_id: int
    aprovador_id: Optional[int] = None
    usuario: 'UsuarioModel' = Field(..., description="Usuário que solicitou a retirada")
    aprovador: Optional['UsuarioModel'] = Field(None, description="Usuário que aprovou a retirada")
    
    model_config = ConfigDict(from_attributes=True)

class FormaPagamentoBase(CustomBaseModel):
    """Base schema para formas de pagamento."""
    nome: str = Field(..., max_length=100, description="Nome da forma de pagamento")
    ativo: bool = Field(default=True, description="Indica se a forma de pagamento está ativa")
    
    model_config = ConfigDict(from_attributes=True)

class FormaPagamentoCreate(FormaPagamentoBase):
    """Schema para criação de uma nova forma de pagamento."""
    pass

class FormaPagamentoUpdate(CustomBaseModel):
    """Schema para atualização de uma forma de pagamento."""
    nome: Optional[str] = Field(None, max_length=100, description="Novo nome da forma de pagamento")
    ativo: Optional[bool] = Field(None, description="Novo status de ativação")
    
    model_config = ConfigDict(from_attributes=True)

class FormaPagamento(FormaPagamentoBase):
    """Schema completo para uma forma de pagamento."""
    id: int
    
    model_config = ConfigDict(from_attributes=True)

class FechamentoFormaPagamentoBase(CustomBaseModel):
    """Base schema para formas de pagamento em um fechamento."""
    forma_pagamento_id: int = Field(..., description="ID da forma de pagamento")
    valor: float = Field(..., gt=0, description="Valor total da forma de pagamento")
    
    model_config = ConfigDict(from_attributes=True)

class FechamentoFormaPagamentoCreate(FechamentoFormaPagamentoBase):
    """Schema para criação de uma nova associação entre fechamento e forma de pagamento."""
    pass

class FechamentoFormaPagamento(FechamentoFormaPagamentoBase):
    """Schema completo para uma associação entre fechamento e forma de pagamento."""
    id: int
    fechamento_id: int
    forma_pagamento: FormaPagamento = Field(..., description="Forma de pagamento associada")
    
    model_config = ConfigDict(from_attributes=True)

class FechamentoCaixaBase(CustomBaseModel):
    """Base schema para fechamento de caixa."""
    valor_sistema: float = Field(..., gt=0, description="Valor total no sistema")
    valor_informado: float = Field(..., gt=0, description="Valor informado em espécie")
    observacoes: Optional[str] = Field(None, max_length=1000, description="Observações sobre o fechamento")
    
    model_config = ConfigDict(from_attributes=True)

class FechamentoCaixaCreate(FechamentoCaixaBase):
    """Schema para criação de um novo fechamento de caixa."""
    formas_pagamento: List[FechamentoFormaPagamentoCreate] = Field(
        ..., 
        min_items=1, 
        description="Formas de pagamento"
    )

class FechamentoCaixaUpdate(CustomBaseModel):
    """Schema para atualização de um fechamento de caixa."""
    observacoes: Optional[str] = Field(None, max_length=1000, description="Novas observações")
    status: Optional[str] = Field(None, description="Novo status do fechamento")
    
    model_config = ConfigDict(from_attributes=True)

class FechamentoCaixa(FechamentoCaixaBase):
    """Schema completo para um fechamento de caixa."""
    id: int
    diferenca: float
    status: str
    data_abertura: datetime
    data_fechamento: Optional[datetime] = None
    usuario_id: int
    usuario: 'UsuarioModel' = Field(..., description="Usuário responsável pelo fechamento")
    formas_pagamento: List[FechamentoFormaPagamento] = Field(
        default_factory=list, 
        description="Formas de pagamento"
    )
    
    model_config = ConfigDict(from_attributes=True)

# Update forward references after all classes are defined
try:
    from app.schemas.usuario import Usuario
    
    # Update the forward references
    MovimentacaoCaixa.model_rebuild()
    RetiradaCaixa.model_rebuild()
    FechamentoCaixa.model_rebuild()
    
    # Update the UsuarioModel reference
    UsuarioModel = Usuario
except ImportError:
    # This might happen during initial import, but the types will be updated later
    pass
