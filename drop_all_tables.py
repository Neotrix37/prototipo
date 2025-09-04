import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/posto"
else:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

with engine.connect() as connection:
    # Desabilitar verificações de chave estrangeira temporariamente
    connection.execute(text("SET session_replication_role = 'replica';"))
    
    # Obter todas as tabelas, exceto alembic_version
    result = connection.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename != 'alembic_version';"))
    tables = [row[0] for row in result]

    # Dropar tabelas em ordem inversa para lidar com dependências
    for table in reversed(tables):
        print(f"Dropping table: {table}")
        connection.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE;"))
    
    # Reabilitar verificações de chave estrangeira
    connection.execute(text("SET session_replication_role = 'origin';"))
    connection.commit()

print("Todas as tabelas (exceto alembic_version) dropadas com sucesso.")