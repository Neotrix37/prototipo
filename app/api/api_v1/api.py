from fastapi import APIRouter

from .endpoints import (
    auth, usuarios, produtos, categorias, fornecedores, 
    clientes, vendas, itens_venda, compras, caixa, fechamento_caixa, sync
)

api_router = APIRouter()

# Inclui os roteadores de cada módulo
api_router.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
api_router.include_router(usuarios.router, prefix="/usuarios", tags=["Usuários"])
api_router.include_router(produtos.router, prefix="/produtos", tags=["Produtos"])
api_router.include_router(categorias.router, prefix="/categorias", tags=["Categorias"])
api_router.include_router(fornecedores.router, prefix="/fornecedores", tags=["Fornecedores"])
api_router.include_router(clientes.router, prefix="/clientes", tags=["Clientes"])
api_router.include_router(vendas.router, prefix="/vendas", tags=["Vendas"])
api_router.include_router(itens_venda.router, prefix="/itens_venda", tags=["Itens de Venda"])

# Novos endpoints
api_router.include_router(compras.router, prefix="/compras", tags=["Compras"])
api_router.include_router(caixa.router, prefix="/caixa", tags=["Caixa"])
api_router.include_router(fechamento_caixa.router, prefix="/fechamento_caixa", tags=["Fechamento de Caixa"])
api_router.include_router(sync.router, tags=["Sincronização"])
