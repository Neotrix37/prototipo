#!/bin/bash

# Set default port if not provided
export PORT=${PORT:-8000}

# Debug info
echo "=== Iniciando aplicação na porta $PORT ==="
echo "URL do banco de dados: $DATABASE_URL"

# Extrai as credenciais do banco de dados de forma mais simples
DB_URL=$DATABASE_URL

# Mostra informações de conexão (sem a senha)
DB_URL_NO_PASS=$(echo $DB_URL | sed -E 's|:([^/]*)@|:****@|')
echo "Conectando ao banco de dados: $DB_URL_NO_PASS"

# Verifica se o psql está instalado
if ! command -v psql &> /dev/null; then
    echo "AVISO: O comando psql não está disponível. Instale o cliente PostgreSQL se precisar de verificação de conexão."
else
    # Tenta conectar ao banco de dados
    echo "Verificando conexão com o banco de dados..."
    if PGPASSWORD=$(echo $DB_URL | grep -oP ":[^:]+@" | cut -d: -f2 | cut -d@ -f1) psql -h $(echo $DB_URL | grep -oP "@[^:]+:" | cut -d@ -f2 | cut -d: -f1) -U $(echo $DB_URL | grep -oP "//[^:]+" | cut -d/ -f3) -d $(echo $DB_URL | grep -oP "[^/]+$" | cut -d? -f1) -c "SELECT 1" &> /dev/null; then
        echo "✅ Conexão com o banco de dados bem-sucedida!"
    else
        echo "❌ Falha ao conectar ao banco de dados. Verifique as credenciais e acessos."
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
