from datetime import datetime
from typing import Any, Dict, List, Type, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import inspect

from ....core import security
from ....db.session import get_db
from ....models.base import CustomBase
from ....schemas.base import SyncRequest, SyncResponse

# Lista de tabelas habilitadas para sincronização
SYNC_ENABLED_TABLES = [
    "usuarios",
    "clientes",
    "produtos",
    "categorias",
    "fornecedores",
    "vendas",
    "itens_venda"
]

router = APIRouter(prefix="/sync", tags=["sincronizacao"])

# Dicionário de modelos sincronizáveis
SYNC_MODELS = {
    table: None for table in SYNC_ENABLED_TABLES  # Serão preenchidos dinamicamente
}

def validate_table_name(table_name: str) -> None:
    """Valida se o nome da tabela está na lista de tabelas habilitadas."""
    if table_name not in SYNC_ENABLED_TABLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Sincronização não suportada para a tabela '{table_name}'. "
                   f"Tabelas disponíveis: {', '.join(SYNC_ENABLED_TABLES)}"
        )

def get_model_by_table_name(table_name: str) -> Type[CustomBase]:
    """Obtém a classe do modelo pelo nome da tabela."""
    validate_table_name(table_name)
    model = SYNC_MODELS.get(table_name)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Modelo para a tabela '{table_name}' não encontrado"
        )
    return model

@router.get("/tables", response_model=Dict[str, Any])
async def list_tables(
    db: Session = Depends(get_db),
    current_user: Any = Depends(security.get_current_active_user)
):
    """
    Lista todas as tabelas disponíveis para sincronização com informações detalhadas.
    
    Retorna apenas as tabelas habilitadas para sincronização nesta versão do sistema.
    
    Retorna:
    - Nome da tabela
    - Descrição dos campos
    - Total de registros (se a tabela existir)
    
    Requer autenticação via token JWT.
    """
    from .... import models
    from sqlalchemy.inspection import inspect
    
    result = {
        "available_tables": [],
        "tables_info": {}
    }
    
    # Mapeia os nomes das tabelas para seus modelos
    table_to_model = {
        'usuarios': 'Usuario',
        'clientes': 'Cliente',
        'produtos': 'Produto',
        'categorias': 'Categoria',
        'fornecedores': 'Fornecedor',
        'vendas': 'Venda',
        'itens_venda': 'ItemVenda'
    }
    
    # Filtra apenas as tabelas habilitadas
    enabled_tables = {
        table: model for table, model in table_to_model.items() 
        if table in SYNC_ENABLED_TABLES and hasattr(models, model)
    }
    
    for table_name, model_name in enabled_tables.items():
        model = getattr(models, model_name)
        inspector = inspect(model)
        
        # Obtém informações das colunas
        columns_info = []
        for column in inspector.mapper.columns:
            columns_info.append({
                "name": column.name,
                "type": str(column.type),
                "primary_key": column.primary_key,
                "nullable": column.nullable,
                "default": str(column.default) if column.default is not None else None
            })
        
        # Conta o total de registros
        total = db.query(model).count()
        
        result["tables_info"][table_name] = {
            "model": model_name,
            "columns": columns_info,
            "total_records": total,
            "sync_columns": ["last_updated", "synced", "deleted"]
        }
        result["available_tables"].append(table_name)
    
    return result

@router.get("/{table_name}", response_model=SyncResponse)
async def get_updated_records(
    table_name: str,
    last_sync: Optional[datetime] = Query(None, description="Data da última sincronização"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Any = Depends(security.get_current_active_user)
):
    """
    Retorna registros atualizados desde a última sincronização.
    
    Apenas as tabelas listadas em SYNC_ENABLED_TABLES são suportadas.
    """
    model = get_model_by_table_name(table_name)
    
    # Filtra registros atualizados desde a última sincronização
    query = db.query(model).filter(model.synced == True)
    
    if last_sync:
        query = query.filter(model.last_updated >= last_sync)
    
    # Aplica paginação
    total = query.count()
    records = query.offset(skip).limit(limit).all()
    
    return {
        "table": table_name,
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": [record.to_dict() for record in records],
        "last_sync": datetime.utcnow()
    }

@router.post("/{table_name}", response_model=Dict[str, int])
async def sync_table(
    table_name: str,
    request: SyncRequest,
    db: Session = Depends(get_db),
    current_user: Any = Depends(security.get_current_active_user)
):
    """
    Sincroniza registros da tabela especificada.
    
    Apenas as tabelas listadas em SYNC_ENABLED_TABLES são suportadas.
    """
    model = get_model_by_table_name(table_name)
    return apply_changes(db, model, request.records)

def apply_changes(
    db: Session,
    model: Type[CustomBase],
    records: List[Dict[str, Any]]
) -> Dict[str, int]:
    """Aplica as alterações (inserção/atualização) nos registros."""
    created = updated = 0
    
    for record in records:
        # Verifica se o registro já existe
        db_record = db.query(model).get(record['id'])
        
        if db_record:
            # Atualiza registro existente
            for key, value in record.items():
                setattr(db_record, key, value)
            db_record.synced = True
            db_record.last_updated = datetime.utcnow()
            updated += 1
        else:
            # Cria novo registro
            db_record = model(**record)
            db_record.synced = True
            db.add(db_record)
            created += 1
    
    db.commit()
    return {"created": created, "updated": updated}

def register_sync_models():
    """Registra os modelos de sincronização dinamicamente."""
    from .... import models
    
    # Mapeia nomes de tabelas para classes de modelo
    table_to_model = {
        'usuarios': 'Usuario',
        'clientes': 'Cliente',
        'produtos': 'Produto',
        'categorias': 'Categoria',
        'fornecedores': 'Fornecedor',
        'vendas': 'Venda',
        'itens_venda': 'ItemVenda'
    }
    
    # Registra apenas os modelos habilitados
    for table, model_name in table_to_model.items():
        if table in SYNC_ENABLED_TABLES and hasattr(models, model_name):
            SYNC_MODELS[table] = getattr(models, model_name)

# Registra os modelos quando o módulo é carregado
register_sync_models()
