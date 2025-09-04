import sys
from sqlalchemy import create_engine, text
from app.core.config import settings

def add_sync_columns():
    """Adiciona as colunas de sincronização a todas as tabelas."""
    # Configura a conexão com o banco de dados
    engine = create_engine(str(settings.DATABASE_URL))
    
    # Lista de tabelas para atualizar
    tables = [
        'usuarios', 'clientes', 'produtos', 'categorias',
        'fornecedores', 'vendas', 'itens_venda', 'compras',
        'compra_itens', 'movimentacoes_caixa', 'fechamentos_caixa',
        'retiradas_caixa',  # Adicionando a tabela retiradas_caixa
        'formas_pagamento', 'fechamento_formas_pagamento'  # Outras tabelas que podem existir
    ]
    
    with engine.connect() as connection:
        # Para cada tabela, adiciona as colunas se elas não existirem
        for table in tables:
            try:
                # Verifica se a tabela existe
                result = connection.execute(
                    text(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = :table_name
                    )"""),
                    {'table_name': table}
                )
                
                if not result.scalar():
                    print(f"Tabela {table} não encontrada, pulando...")
                    continue
                
                # Adiciona as colunas
                print(f"Verificando/Atualizando tabela {table}...")
                
                # Lista de colunas a serem adicionadas
                columns_to_add = [
                    ('last_updated', 'TIMESTAMP WITH TIME ZONE', 'DEFAULT CURRENT_TIMESTAMP'),
                    ('synced', 'BOOLEAN', 'DEFAULT TRUE'),
                    ('deleted', 'BOOLEAN', 'DEFAULT FALSE')
                ]
                
                for column_name, column_type, default_value in columns_to_add:
                    # Verifica se a coluna já existe
                    result = connection.execute(
                        text("""
                        SELECT EXISTS (
                            SELECT 1 
                            FROM information_schema.columns 
                            WHERE table_schema = 'public' 
                            AND table_name = :table_name 
                            AND column_name = :column_name
                        )
                        """),
                        {'table_name': table, 'column_name': column_name}
                    )
                    
                    if not result.scalar():
                        print(f"  Adicionando coluna {column_name}...")
                        try:
                            connection.execute(
                                text(f"ALTER TABLE {table} ADD COLUMN {column_name} {column_type} {default_value}")
                            )
                            print(f"  Coluna {column_name} adicionada com sucesso!")
                        except Exception as e:
                            print(f"  Erro ao adicionar coluna {column_name}: {str(e)}")
                    else:
                        print(f"  Coluna {column_name} já existe, pulando...")
                
                print(f"Tabela {table} verificada/atualizada com sucesso!\n")
                
            except Exception as e:
                print(f"Erro ao processar tabela {table}: {str(e)}")
                continue
        
        # Confirma as alterações
        connection.commit()

if __name__ == "__main__":
    print("Iniciando atualização das tabelas...\n")
    add_sync_columns()
    print("\nAtualização concluída!")
