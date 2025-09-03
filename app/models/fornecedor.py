from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db.session import Base

class Fornecedor(Base):
    __tablename__ = "fornecedores"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(100), nullable=False, index=True)
    telefone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    endereco = Column(Text, nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamento com produtos
    produtos = relationship("Produto", back_populates="fornecedor")

    def __repr__(self):
        return f"<Fornecedor(id={self.id}, nome='{self.nome}')>"

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "telefone": self.telefone,
            "email": self.email,
            "endereco": self.endereco,
            "ativo": self.ativo,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
