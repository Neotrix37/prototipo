from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .base import Base, CustomBase

class FechamentoCaixa(CustomBase, Base):
    __tablename__ = "fechamentos_caixa"

    id = Column(Integer, primary_key=True, index=True)
    valor_sistema = Column(Float, nullable=False)
    valor_informado = Column(Float, nullable=False)
    diferenca = Column(Float, nullable=False)
    observacoes = Column(Text, nullable=True)
    status = Column(String(50), default="Pendente", nullable=False)
    data_fechamento = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario = relationship("Usuario", back_populates="fechamentos_caixa")
    
    # Relação com as formas de pagamento
    formas_pagamento = relationship("FechamentoFormaPagamento", back_populates="fechamento", cascade="all, delete-orphan")

    def to_dict(self):
        try:
            # Log para depuração
            print(f"\n=== DEBUG: Serializando FechamentoCaixa ID {self.id} ===")
            
            # Dados básicos
            result = {
                "id": self.id,
                "valor_sistema": float(self.valor_sistema) if self.valor_sistema is not None else 0.0,
                "valor_informado": float(self.valor_informado) if self.valor_informado is not None else 0.0,
                "diferenca": float(self.diferenca) if self.diferenca is not None else 0.0,
                "observacoes": self.observacoes or "",
                "status": self.status or "Pendente",
                "data_abertura": self.data_fechamento.isoformat() if self.data_fechamento else None,
                "data_fechamento": self.data_fechamento.isoformat() if self.data_fechamento else None,
                "usuario_id": self.usuario_id
            }
            
            # Dados do usuário
            try:
                usuario_data = {
                    "id": self.usuario.id if self.usuario else None,
                    "nome": self.usuario.nome if self.usuario else "",
                    "usuario": getattr(self.usuario, 'usuario', ''),
                    "nivel": getattr(self.usuario, 'nivel', 'basico'),
                    "ativo": bool(getattr(self.usuario, 'ativo', True)),
                    "is_admin": bool(getattr(self.usuario, 'is_admin', False)),
                    "salario": float(getattr(self.usuario, 'salario', 0.0)),
                    "pode_abastecer": bool(getattr(self.usuario, 'pode_abastecer', False)),
                    "created_at": getattr(self.usuario, 'created_at', None).isoformat() if hasattr(self.usuario, 'created_at') and self.usuario.created_at else None,
                    "updated_at": getattr(self.usuario, 'updated_at', None).isoformat() if hasattr(self.usuario, 'updated_at') and self.usuario.updated_at else None
                }
                result["usuario"] = usuario_data
                print("Dados do usuário processados com sucesso")
            except Exception as e:
                print(f"Erro ao processar dados do usuário: {str(e)}")
                result["usuario"] = {
                    "id": None,
                    "nome": "Erro ao carregar usuário",
                    "usuario": "",
                    "nivel": "basico",
                    "ativo": False,
                    "is_admin": False,
                    "salario": 0.0,
                    "pode_abastecer": False,
                    "error": str(e)
                }
            
            # Formas de pagamento
            try:
                formas_pagamento = []
                if hasattr(self, 'formas_pagamento') and self.formas_pagamento:
                    for fp in self.formas_pagamento:
                        try:
                            fp_dict = {
                                "id": fp.id,
                                "valor": float(fp.valor) if fp.valor is not None else 0.0,
                                "fechamento_id": fp.fechamento_id,
                                "forma_pagamento_id": fp.forma_pagamento_id,
                                "forma_pagamento": {
                                    "id": fp.forma_pagamento.id if fp.forma_pagamento else None,
                                    "nome": fp.forma_pagamento.nome if fp.forma_pagamento else "",
                                    "ativo": bool(fp.forma_pagamento.ativo) if fp.forma_pagamento and hasattr(fp.forma_pagamento, 'ativo') else False
                                }
                            }
                            formas_pagamento.append(fp_dict)
                        except Exception as fp_error:
                            print(f"Erro ao processar forma de pagamento {getattr(fp, 'id', 'unknown')}: {str(fp_error)}")
                            formas_pagamento.append({
                                "error": f"Erro ao processar forma de pagamento: {str(fp_error)}",
                                "id": getattr(fp, 'id', None),
                                "valor": 0.0
                            })
                
                result["formas_pagamento"] = formas_pagamento
                print(f"{len(formas_pagamento)} formas de pagamento processadas")
                
            except Exception as e:
                print(f"Erro ao processar formas de pagamento: {str(e)}")
                result["formas_pagamento"] = [{"error": f"Erro ao processar formas de pagamento: {str(e)}"}]
            
            print(f"Serialização concluída para FechamentoCaixa ID {self.id}")
            return result
            
        except Exception as e:
            print(f"\n=== ERRO CRÍTICO em to_dict() ===")
            print(f"Tipo do erro: {type(e).__name__}")
            print(f"Mensagem: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Retornar um dicionário de erro em caso de falha crítica
            return {
                "id": getattr(self, 'id', None),
                "error": "Erro ao serializar fechamento de caixa",
                "error_type": type(e).__name__,
                "error_message": str(e)
            }

class FormaPagamento(CustomBase, Base):
    __tablename__ = "formas_pagamento"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), unique=True, nullable=False)
    ativo = Column(Integer, default=1, nullable=False)
    
    # Relacionamento com fechamentos
    fechamentos = relationship("FechamentoFormaPagamento", back_populates="forma_pagamento")

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "ativo": bool(self.ativo)
        }

class FechamentoFormaPagamento(CustomBase, Base):
    __tablename__ = "fechamento_formas_pagamento"
    
    id = Column(Integer, primary_key=True, index=True)
    valor = Column(Float, nullable=False)
    
    # Relacionamentos
    fechamento_id = Column(Integer, ForeignKey("fechamentos_caixa.id", ondelete="CASCADE"), nullable=False)
    forma_pagamento_id = Column(Integer, ForeignKey("formas_pagamento.id"), nullable=False)
    
    fechamento = relationship("FechamentoCaixa", back_populates="formas_pagamento")
    forma_pagamento = relationship("FormaPagamento", back_populates="fechamentos")
    
    def to_dict(self):
        return {
            "id": self.id,
            "valor": float(self.valor) if self.valor is not None else 0.0,
            "fechamento_id": self.fechamento_id,
            "forma_pagamento_id": self.forma_pagamento_id,
            "forma_pagamento": {
                "id": self.forma_pagamento.id if self.forma_pagamento else None,
                "nome": self.forma_pagamento.nome if self.forma_pagamento else "",
                "ativo": bool(self.forma_pagamento.ativo) if self.forma_pagamento else False
            }
        }
