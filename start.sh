@'
#!/bin/bash
set -e

echo "ðŸš€ Iniciando a aplicaÃ§Ã£o..."

# Carregar variÃ¡veis de ambiente
if [ -f ".env.production" ]; then
    echo "ðŸ“‚ Carregando variÃ¡veis de .env.production..."
    export $(grep -v '^#' .env.production | xargs)
fi

# ConfiguraÃ§Ãµes bÃ¡sicas
: ${HOST:="0.0.0.0"}
: ${PORT:=8000}
: ${ENVIRONMENT:="production"}

echo "âš™ï¸  ConfiguraÃ§Ãµes:"
echo "- ENVIRONMENT: ${ENVIRONMENT}"
echo "- HOST: ${HOST}"
echo "- PORT: ${PORT}"

# Instalar dependÃªncias
echo "ðŸ“¦ Instalando dependÃªncias..."
pip install -r requirements.txt

# Executar migraÃ§Ãµes
echo "ðŸ”„ Executando migraÃ§Ãµes..."
alembic upgrade head

# Iniciar a aplicaÃ§Ã£o
echo "ðŸš€ Iniciando o servidor..."
exec uvicorn app.main:app --host $HOST --port $PORT
'@ | Out-File -FilePath .\start.sh -Encoding utf8 -NoNewline