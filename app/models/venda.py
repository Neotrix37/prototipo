from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, String, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base, CustomBase
from ..schemas.venda import StatusVenda, FormaPagamento

class Venda(Base, CustomBase):
    __tablename__ = "vendas"
    
    id = Column(Integer, primary_key=True, index=True)
    data_venda = Column(DateTime(timezone=True), server_default=func.now())
    data_atualizacao = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True)
    
    # Status e pagamento
    status = Column(Enum(StatusVenda), default=StatusVenda.CONCLUIDA, nullable=False)
    forma_pagamento = Column(Enum(FormaPagamento), nullable=False)
    
    # Valores
    subtotal = Column(Float, default=0.0, nullable=False)
    desconto = Column(Float, default=0.0, nullable=False)
    total = Column(Float, default=0.0, nullable=False)
    valor_recebido = Column(Float, default=0.0, nullable=True)
    troco = Column(Float, default=0.0, nullable=True)
    
    # Observações
    observacoes = Column(String(500), nullable=True)
    
    # Relacionamentos
    usuario = relationship("Usuario", back_populates="vendas")
    cliente = relationship("Cliente", back_populates="vendas")
    itens = relationship("ItemVenda", back_populates="venda", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Venda(id={self.id}, total={self.total}, status='{self.status}')>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "data_venda": self.data_venda.isoformat() if self.data_venda else None,
            "data_atualizacao": self.data_atualizacao.isoformat() if self.data_atualizacao else None,
            "usuario_id": self.usuario_id,
            "cliente_id": self.cliente_id,
            "status": self.status.value,
            "forma_pagamento": self.forma_pagamento.value,
            "subtotal": self.subtotal,
            "desconto": self.desconto,
            "total": self.total,
            "valor_recebido": self.valor_recebido,
            "troco": self.troco if self.troco is not None else 0.0,
            "observacoes": self.observacoes,
            "itens": [item.to_dict() for item in self.itens] if self.itens else []
        }
