@'
#!/bin/bash
set -e

echo "🚀 Iniciando a aplicação..."

# Carregar variáveis de ambiente
if [ -f ".env.production" ]; then
    echo "📂 Carregando variáveis de .env.production..."
    export $(grep -v '^#' .env.production | xargs)
fi

# Configurações básicas
: ${HOST:="0.0.0.0"}
: ${PORT:=8000}
: ${ENVIRONMENT:="production"}

echo "⚙️  Configurações:"
echo "- ENVIRONMENT: ${ENVIRONMENT}"
echo "- HOST: ${HOST}"
echo "- PORT: ${PORT}"

# Instalar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# Executar migrações
echo "🔄 Executando migrações..."
alembic upgrade head

# Iniciar a aplicação
echo "🚀 Iniciando o servidor..."
exec uvicorn app.main:app --host $HOST --port $PORT
'@ | Out-File -FilePath .\start.sh -Encoding utf8 -NoNewline