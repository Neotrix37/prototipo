@"
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
uvicorn app.main:app --host $HOST --port $PORT --workers 4 --proxy-headers

echo "✅ Aplicação iniciada com sucesso!"

# Manter o container rodando
while true; do sleep 1; done
"@ | Out-File -FilePath .\start.sh -Encoding utf8