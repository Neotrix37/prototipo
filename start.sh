#!/bin/bash

# Set default port if not provided
export PORT=${PORT:-8000}

# Debug info
echo "=== Iniciando aplicação na porta $PORT ==="
echo "URL do banco de dados: $DATABASE_URL"

# Extrai as credenciais do banco de dados
DB_USER=$(echo $DATABASE_URL | grep -oP "postgresql://\K[^:]+")
DB_PASS=$(echo $DATABASE_URL | grep -oP "[^:]:(.+?)" | cut -d: -f2 | cut -d@ -f1)
DB_HOST=$(echo $DATABASE_URL | grep -oP "@\K[^/]+\")
DB_NAME=$(echo $DATABASE_URL | grep -oP "\d+/\K[^?]+")

# Mostra informações de conexão (sem a senha)
echo "Conectando ao banco de dados: postgresql://${DB_USER}:***@${DB_HOST}/${DB_NAME}"

# Verifica se o psql está instalado
if ! command -v psql &> /dev/null; then
    echo "AVISO: O comando psql não está disponível. Instale o cliente PostgreSQL se precisar de verificação de conexão."
else
    # Tenta conectar ao banco de dados
    echo "Verificando conexão com o banco de dados..."
    if PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT 1" &> /dev/null; then
        echo "✅ Conexão com o banco de dados bem-sucedida!"
    else
        echo "❌ Falha ao conectar ao banco de dados. Verifique as credenciais e acessos."
        echo "Comando de teste: PGPASSWORD=*** psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c \"SELECT 1\""
        echo "Certifique-se de que o banco de dados está acessível e as credenciais estão corretas."
        exit 1
    fi
fi

# Executa as migrações do banco de dados
echo "Executando migrações do banco de dados..."
alembic upgrade head

# Inicia a aplicação FastAPI
echo "Iniciando aplicação FastAPI..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT --log-level debug
