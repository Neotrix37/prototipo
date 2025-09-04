#!/bin/bash

# Configurações iniciais
set -e

# Configura a porta
PORT=${PORT:-8000}
export PORT

# Instala as dependências (apenas para garantir)
python -m ensurepip --upgrade
python -m pip install --upgrade pip
pip install -r requirements.txt

# Executa as migrações do banco de dados
echo "🔄 Executando migrações do banco de dados..."
alembic upgrade head

# Inicia a aplicação
echo "🚀 Iniciando aplicação na porta $PORT..."
exec gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:$PORT \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
