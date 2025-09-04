#!/bin/bash
set -e

echo "Iniciando a aplicacao..."

# Carregar variáveis de ambiente
if [ -f ".env.production" ]; then
    echo "Carregando variaveis de .env.production..."
    export $(grep -v '^#' .env.production | xargs)
fi

# Configuracoes basicas
: ${HOST:="0.0.0.0"}
: ${PORT:=8000}
: ${ENVIRONMENT:="production"}

echo "Configuracoes:"
echo "- ENVIRONMENT: ${ENVIRONMENT}"
echo "- HOST: ${HOST}"
echo "- PORT: ${PORT}"

# Instalar dependencias
echo "Instalando dependencias..."
python -m pip install -r requirements.txt

# Instalar o alembic explicitamente
echo "Instalando alembic..."
python -m pip install alembic

# Executar migracoes
echo "Executando migracoes..."
cd /app
export PYTHONPATH=/app
python -m alembic upgrade head

# Iniciar a aplicacao
echo "Iniciando o servidor..."
python -m uvicorn app.main:app --host $HOST --port $PORT --workers 4