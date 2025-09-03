from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, event
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base, CustomBase

class Cliente(Base, CustomBase):
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    nuit = Column(String, nullable=True, index=True)
    telefone = Column(String(20))
    email = Column(String(100), unique=True, index=True)
    endereco = Column(String(200))
    especial = Column(Boolean, default=False)
    desconto_divida = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    vendas = relationship("Venda", back_populates="cliente")
    
    def __repr__(self):
        return f"<Cliente(id={self.id}, nome='{self.nome}')>"

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "nuit": self.nuit,
            "telefone": self.telefone,
            "email": self.email,
            "endereco": self.endereco,
            "especial": self.especial,
            "desconto_divida": float(self.desconto_divida) if self.desconto_divida is not None else 0.0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

# Hook para garantir que o email seja sempre em minúsculas
@event.listens_for(Cliente, 'before_insert')
@event.listens_for(Cliente, 'before_update')
def lower_email(mapper, connection, target):
    if target.email:
        target.email = target.email.lower()
