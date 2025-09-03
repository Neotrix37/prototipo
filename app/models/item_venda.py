from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .base import Base, CustomBase

class ItemVenda(CustomBase, Base):
    __tablename__ = "itens_venda"

    id = Column(Integer, primary_key=True, index=True)
    venda_id = Column(Integer, ForeignKey("vendas.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    quantidade = Column(Float, nullable=False)
    preco_unitario = Column(Float, nullable=False)
    desconto = Column(Float, default=0.0)
    total = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    venda = relationship("Venda", back_populates="itens")
    produto = relationship("Produto")

    def __repr__(self):
        return f"<ItemVenda(id={self.id}, produto_id={self.produto_id}, quantidade={self.quantidade})>"

    def to_dict(self):
        return {
            "id": self.id,
            "venda_id": self.venda_id,
            "produto_id": self.produto_id,
            "produto_nome": self.produto.nome if hasattr(self, 'produto') and self.produto else None,
            "quantidade": self.quantidade,
            "preco_unitario": self.preco_unitario,
            "desconto": self.desconto,
            "total": self.total,
            "criado_em": self.created_at.isoformat() if self.created_at else None
        }
