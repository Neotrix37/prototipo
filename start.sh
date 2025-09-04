#!/bin/bash

# Configura a porta padrão
export PORT=${PORT:-8000}

# Instala as dependências
pip install --upgrade pip
pip install -r requirements.txt

# Executa as migrações do banco de dados
alembic upgrade head

# Inicia a aplicação
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
