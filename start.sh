#!/bin/bash
set -e

echo "Iniciando a aplicacao..."

# Carregar variaveis de ambiente
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
pip install -r requirements.txt

# Executar migracoes
echo "Executando migracoes..."
alembic upgrade head

# Iniciar a aplicacao
echo "Iniciando o servidor..."
exec uvicorn app.main:app --host $HOST --port $PORT