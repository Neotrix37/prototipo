"""
Módulo contendo os modelos de dados do banco de dados.
"""

from .base import Base
from .usuario import Usuario
from .cliente import Cliente
from .produtos import Produto
from .categorias import Categoria
from .fornecedor import Fornecedor
from .venda import Venda
from .item_venda import ItemVenda

# Importe aqui outros modelos conforme necessário

# Lista de todos os modelos para facilitar a importação
__all__ = [
    'Base',
    'Usuario',
    'Cliente',
    'Produto',
    'Categoria',
    'Fornecedor',
    'Venda',
    'ItemVenda'
]
