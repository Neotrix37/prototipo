from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .base import Base, CustomBase

class Compra(CustomBase, Base):
    __tablename__ = "compras"

    id = Column(Integer, primary_key=True, index=True)
    fornecedor_id = Column(Integer, ForeignKey("fornecedores.id"), nullable=False)
    valor_total = Column(Float, nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    observacoes = Column(Text, nullable=True)
    data_compra = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    itens = relationship("ItemCompra", back_populates="compra", cascade="all, delete-orphan")
    fornecedor = relationship("Fornecedor", back_populates="compras")
    usuario = relationship("Usuario", back_populates="compras")

    def to_dict(self):
        return {
            "id": self.id,
            "fornecedor_id": self.fornecedor_id,
            "fornecedor_nome": self.fornecedor.nome if self.fornecedor else None,
            "valor_total": self.valor_total,
            "usuario_id": self.usuario_id,
            "usuario_nome": self.usuario.nome if self.usuario else None,
            "observacoes": self.observacoes,
            "data_compra": self.data_compra.isoformat() if self.data_compra else None,
            "itens": [item.to_dict() for item in self.itens] if self.itens else []
        }

class ItemCompra(CustomBase, Base):
    __tablename__ = "compra_itens"

    id = Column(Integer, primary_key=True, index=True)
    compra_id = Column(Integer, ForeignKey("compras.id", ondelete="CASCADE"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id", ondelete="SET NULL"), nullable=True)
    produto_nome = Column(String(255), nullable=False)
    quantidade = Column(Float, nullable=False)
    preco_unitario = Column(Float, nullable=False)
    preco_venda = Column(Float, nullable=False)
    lucro_unitario = Column(Float, nullable=False)
    lucro_total = Column(Float, nullable=False)
    
    # Relacionamentos
    compra = relationship("Compra", back_populates="itens")
    produto = relationship("Produto")

    def to_dict(self):
        return {
            "id": self.id,
            "compra_id": self.compra_id,
            "produto_id": self.produto_id,
            "produto_nome": self.produto_nome,
            "quantidade": self.quantidade,
            "preco_unitario": self.preco_unitario,
            "preco_venda": self.preco_venda,
            "lucro_unitario": self.lucro_unitario,
            "lucro_total": self.lucro_total
        }
