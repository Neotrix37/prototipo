from sqlalchemy.orm import declared_attr
from sqlalchemy import Column, Integer, DateTime, func
from ..db.session import Base  # Importa Base da sessão para evitar duplicação

class CustomBase:
    """Classe base personalizada para todos os modelos."""
    
    # Gera automaticamente o nome da tabela em minúsculas baseado no nome da classe
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    
    # Colunas comuns a todas as tabelas
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def to_dict(self):
        """Converte o objeto para dicionário."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# A classe Base agora é importada de session.py
