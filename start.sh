#!/bin/bash
set -e

echo "=== Iniciando aplicação ==="

# Carregar variáveis de ambiente do arquivo .env se existir
if [ -f ".env" ]; then
    echo "📄 Carregando variáveis de ambiente de .env..."
    export $(grep -v '^#' .env | xargs)
fi

# Configurações padrão
: ${HOST:="0.0.0.0"}
: ${PORT:=8000}
: ${ENVIRONMENT:="production"}
: ${DEBUG:="False"}

echo "🌍 Ambiente: $ENVIRONMENT"
echo "🐞 Modo Debug: $DEBUG"

# Verificar se a porta está disponível
if ! command -v lsof &> /dev/null || ! lsof -i :"$PORT" > /dev/null; then
    echo "✅ Porta $PORT está disponível"
else
    echo "⚠️  Aviso: A porta $PORT já está em uso"
    echo "🔍 Tentando encontrar uma porta disponível..."
    PORT=$(($PORT + 1))
    echo "🔄 Usando a porta alternativa: $PORT"
fi

# Verificar se o virtualenv está ativado
if [ -z "$VIRTUAL_ENV" ]; then
    echo "ℹ️  Virtualenv não detectado. Verificando se precisa ativar..."
    if [ -d "venv" ]; then
        echo "🔌 Ativando virtualenv..."
        source venv/bin/activate
    fi
fi

# Instalar dependências
echo "📦 Instalando/Atualizando dependências..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# Executar migrações do banco de dados
echo "🔄 Executando migrações do banco de dados..."
alembic upgrade head

# Iniciar a aplicação
echo "🚀 Iniciando aplicação em $HOST:$PORT..."
exec gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind $HOST:$PORT \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
