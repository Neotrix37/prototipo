"""
Módulo contendo os endpoints da API v1.
"""

from . import (
    auth, usuarios, produtos, categorias, 
    fornecedores, clientes, vendas, itens_venda,
    compras, caixa, fechamento_caixa, sync
)

__all__ = [
    'auth', 'usuarios', 'produtos', 'categorias',
    'fornecedores', 'clientes', 'vendas', 'itens_venda',
    'compras', 'caixa', 'fechamento_caixa', 'sync'
]
