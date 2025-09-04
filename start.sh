#!/bin/bash

# Configurações iniciais
set -e  # Para o script em caso de erro
export PORT=${PORT:-8000}

# Logs iniciais
echo "=== Iniciando aplicação ==="
echo "Porta: $PORT"
echo "Ambiente: ${ENVIRONMENT:-development}"

# Verifica se o banco de dados está acessível
if [ -n "$DATABASE_URL" ]; then
    echo " Conectando ao banco de dados..."
    # Versão sem depender do psql
    if python -c "import sqlalchemy; from urllib.parse import urlparse; url = urlparse('$DATABASE_URL'); engine = sqlalchemy.create_engine('postgresql+psycopg2://{}:{}@{}:{}/{}'.format(url.username, url.password, url.hostname, url.port or 5432, url.path[1:])); conn = engine.connect(); conn.close(); print(' Banco de dados conectado!')"; then
        echo " Banco de dados conectado com sucesso!"
    else
        echo "  Aviso: Não foi possível conectar ao banco de dados"
    fi
fi

# Executa migrações
echo " Executando migrações..."
alembic upgrade head

# Inicia a aplicação
echo " Iniciando aplicação FastAPI na porta $PORT..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --log-level debug
