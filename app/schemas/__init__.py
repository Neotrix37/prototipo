"""
Módulo contendo os schemas Pydantic para validação de dados.
"""

from .usuario import (
    UsuarioBase, UsuarioCreate, UsuarioUpdate,
    UsuarioInDB, Usuario, Token, TokenData, UsuarioLogin, NivelUsuario
)

from .produtos import (
    ProdutoBase, ProdutoCreate, ProdutoUpdate,
    ProdutoInDB, Produto
)

from .categoria import (
    CategoriaBase, CategoriaCreate, CategoriaUpdate,
    CategoriaInDB, Categoria
)

from .fornecedor import (
    FornecedorBase, FornecedorCreate, FornecedorUpdate,
    FornecedorInDB, Fornecedor
)

__all__ = [
    # Usuário
    'UsuarioBase', 'UsuarioCreate', 'UsuarioUpdate',
    'UsuarioInDB', 'Usuario', 'Token', 'TokenData', 'UsuarioLogin', 'NivelUsuario',
    
    # Produtos
    'ProdutoBase', 'ProdutoCreate', 'ProdutoUpdate',
    'ProdutoInDB', 'Produto',
    
    # Categorias
    'CategoriaBase', 'CategoriaCreate', 'CategoriaUpdate',
    'CategoriaInDB', 'Categoria',
    
    # Fornecedores
    'FornecedorBase', 'FornecedorCreate', 'FornecedorUpdate',
    'FornecedorInDB', 'Fornecedor'
]
