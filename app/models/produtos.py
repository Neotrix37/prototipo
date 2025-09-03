from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db.session import Base

class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo = Column(String(50), unique=True, nullable=False, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(String(500))
    preco_custo = Column(Float, nullable=False)
    preco_venda = Column(Float, nullable=False)
    estoque = Column(Float, nullable=False, default=0.0)
    estoque_minimo = Column(Float, nullable=False, default=0.0)
    ativo = Column(Boolean, nullable=False, default=True)
    venda_por_peso = Column(Boolean, default=False)
    unidade_medida = Column(String(10), default='un')
    
    # Relacionamentos
    categoria_id = Column(Integer, ForeignKey('categorias.id'))
    categoria = relationship("Categoria", back_populates="produtos")
    
    fornecedor_id = Column(Integer, ForeignKey('fornecedores.id'), default=1)
    fornecedor = relationship("Fornecedor", back_populates="produtos")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Produto(id={self.id}, codigo='{self.codigo}', nome='{self.nome}')>"

    def to_dict(self):
        return {
            "id": self.id,
            "codigo": self.codigo,
            "nome": self.nome,
            "descricao": self.descricao,
            "preco_custo": self.preco_custo,
            "preco_venda": self.preco_venda,
            "estoque": self.estoque,
            "estoque_minimo": self.estoque_minimo,
            "ativo": self.ativo,
            "venda_por_peso": self.venda_por_peso,
            "unidade_medida": self.unidade_medida,
            "categoria_id": self.categoria_id,
            "categoria": self.categoria.to_dict() if self.categoria else None,
            "fornecedor_id": self.fornecedor_id,
            "fornecedor": self.fornecedor.to_dict() if self.fornecedor else None,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
