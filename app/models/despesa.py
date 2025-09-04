from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .base import Base, CustomBase

class DespesaRecorrente(CustomBase, Base):
    __tablename__ = "despesas_recorrentes"

    class TipoDespesa(str, Enum):
        MENSAL = "Mensal"
        TRIMESTRAL = "Trimestral"
        SEMESTRAL = "Semestral"
        ANUAL = "Anual"
    
    class StatusDespesa(str, Enum):
        PENDENTE = "Pendente"
        PAGO = "Pago"
        ATRASADO = "Atrasado"
        CANCELADO = "Cancelado"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(Enum(TipoDespesa), nullable=False)
    categoria = Column(String(100), nullable=False)
    descricao = Column(String(255), nullable=False)
    valor = Column(Float, nullable=False)
    data_vencimento = Column(DateTime, nullable=False)
    data_pagamento = Column(DateTime, nullable=True)
    status = Column(Enum(StatusDespesa), default=StatusDespesa.PENDENTE, nullable=False)
    observacoes = Column(Text, nullable=True)
    
    # Relacionamentos
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario = relationship("Usuario", back_populates="despesas")

    def to_dict(self):
        return {
            "id": self.id,
            "tipo": self.tipo.value,
            "categoria": self.categoria,
            "descricao": self.descricao,
            "valor": self.valor,
            "data_vencimento": self.data_vencimento.isoformat() if self.data_vencimento else None,
            "data_pagamento": self.data_pagamento.isoformat() if self.data_pagamento else None,
            "status": self.status.value,
            "observacoes": self.observacoes,
            "usuario_id": self.usuario_id,
            "usuario_nome": self.usuario.nome if self.usuario else None
        }
