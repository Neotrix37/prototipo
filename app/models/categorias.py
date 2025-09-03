from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db.session import Base

class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(100), nullable=False, unique=True, index=True)
    descricao = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamento com produtos
    produtos = relationship("Produto", back_populates="categoria")

    def __repr__(self):
        return f"<Categoria(id={self.id}, nome='{self.nome}')>"

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "total_produtos": len(self.produtos) if hasattr(self, 'produtos') else 0
        }
