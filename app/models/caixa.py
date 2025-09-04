from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, Float, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .base import Base, CustomBase

class TipoMovimentacao(str, Enum):
    ENTRADA = "ENTRADA"
    SAIDA = "SAIDA"
    
    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            value = value.upper()
            for member in cls:
                if member.value == value:
                    return member
        return None

    def __str__(self):
        return self.value

class StatusRetirada(str, Enum):
    PENDENTE = "Pendente"
    APROVADO = "Aprovado"
    REJEITADO = "Rejeitado"
    CONCLUIDO = "Concluído"

class MovimentacaoCaixa(CustomBase, Base):
    __tablename__ = "movimentacoes_caixa"
    __table_args__ = {
        'extend_existing': True,
        'schema': 'public'
    }

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(10), nullable=False)  # 'ENTRADA' or 'SAIDA'
    valor = Column(Float, nullable=False)
    descricao = Column(String(255), nullable=False)
    observacao = Column(Text, nullable=True)
    data_movimentacao = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario = relationship("Usuario", back_populates="movimentacoes_caixa")

    def to_dict(self):
        return {
            "id": self.id,
            "tipo": self.tipo,
            "valor": self.valor,
            "descricao": self.descricao,
            "observacao": self.observacao,
            "data_movimentacao": self.data_movimentacao.isoformat() if self.data_movimentacao else None,
            "usuario_id": self.usuario_id,
            "usuario_nome": self.usuario.nome if self.usuario else None
        }

class RetiradaCaixa(CustomBase, Base):
    __tablename__ = "retiradas_caixa"
    
    id = Column(Integer, primary_key=True, index=True)
    valor = Column(Float, nullable=False)
    motivo = Column(String(255), nullable=False)
    observacao = Column(Text, nullable=True)
    origem = Column(String(100), default="vendas")
    status = Column(String(20), default="Pendente", nullable=False)  # 'Pendente', 'Aprovado', 'Rejeitado', 'Concluído'
    data_retirada = Column(DateTime(timezone=True), server_default=func.now())
    data_aprovacao = Column(DateTime(timezone=True), nullable=True)
    
    # Relacionamentos
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    aprovador_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    
    usuario = relationship("Usuario", foreign_keys=[usuario_id], back_populates="minhas_retiradas")
    aprovador = relationship("Usuario", foreign_keys=[aprovador_id])
    
    __table_args__ = {
        'extend_existing': True,
        'schema': 'public',
        'info': {'check_constraint': "status IN ('Pendente', 'Aprovado', 'Rejeitado', 'Concluído')"}
    }
    
    def to_dict(self):
        return {
            "id": self.id,
            "valor": self.valor,
            "motivo": self.motivo,
            "observacao": self.observacao,
            "origem": self.origem,
            "status": self.status,
            "data_retirada": self.data_retirada.isoformat() if self.data_retirada else None,
            "data_aprovacao": self.data_aprovacao.isoformat() if self.data_aprovacao else None,
            "usuario_id": self.usuario_id,
            "usuario_nome": self.usuario.nome if self.usuario else None,
            "aprovador_id": self.aprovador_id,
            "aprovador_nome": self.aprovador.nome if self.aprovador else None
        }
