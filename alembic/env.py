from logging.config import fileConfig
import os
import sys
from sqlalchemy import engine_from_config, pool
from alembic import context

# Adiciona o diretório raiz ao path para que possamos importar os módulos do projeto
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.config import settings
from app.db.base import Base  # noqa

# Configuração do Alembic
config = context.config

# Interpreta o arquivo de configuração para logging Python
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Define a URL do banco de dados a partir das configurações
config.set_main_option('sqlalchemy.url', str(settings.DATABASE_URL))

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Executa migrações no modo 'offline'."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Executa migrações no modo 'online'."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
