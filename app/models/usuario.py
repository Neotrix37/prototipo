from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Float, event
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property
from ..db.session import Base
from .base import CustomBase
from ..schemas.usuario import NivelUsuario  # Import the NivelUsuario enum

class Usuario(Base, CustomBase):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String, nullable=False)
    usuario = Column(String, unique=True, nullable=False, index=True)
    senha = Column(String, nullable=False)
    _nivel = Column('nivel', Integer, nullable=False, default=1)  # Private column
    ativo = Column(Boolean, nullable=False, default=True)
    is_admin = Column(Boolean, nullable=False, default=False)
    salario = Column(Float, default=0.0)
    pode_abastecer = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    vendas = relationship("Venda", back_populates="usuario")

    def __repr__(self):
        return f"<Usuario(id={self.id}, usuario='{self.usuario}', nome='{self.nome}')>"

    @hybrid_property
    def nivel(self):
        # Convert integer to NivelUsuario enum
        if self._nivel is None:
            return NivelUsuario.BASICO
        try:
            return list(NivelUsuario)[self._nivel - 1]
        except IndexError:
            return NivelUsuario.BASICO

    @nivel.setter
    def nivel(self, value):
        # Convert NivelUsuario enum or string to integer
        if isinstance(value, NivelUsuario):
            self._nivel = list(NivelUsuario).index(value) + 1
        elif isinstance(value, str):
            try:
                self._nivel = list(NivelUsuario).index(NivelUsuario(value)) + 1
            except ValueError:
                self._nivel = 1  # Default to Básico
        elif isinstance(value, int):
            self._nivel = value
        else:
            self._nivel = 1  # Default to Básico

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "usuario": self.usuario,
            "nivel": self.nivel.value,  # Use the enum value (string)
            "ativo": self.ativo,
            "is_admin": self.is_admin,
            "salario": float(self.salario) if self.salario is not None else None,
            "pode_abastecer": self.pode_abastecer,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
