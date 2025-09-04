#!/bin/bash

# Configurações iniciais
set -e
export PORT=${PORT:-8000}

# Logs iniciais
echo "=== Iniciando aplicação ==="
echo "Diretório atual: $(pwd)"
echo "Conteúdo do diretório:"
ls -la

# Instala as dependências
echo "📦 Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

# Configura a variável de ambiente DATABASE_URL se não estiver definida
if [ -z "${DATABASE_URL}" ]; then
    echo "⚠️  DATABASE_URL não definida. Usando valor padrão."
    export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/posto"
fi

# Adiciona sslmode=disable à URL se não estiver presente
if [[ "$DATABASE_URL" != *"sslmode="* ]]; then
    echo "🔧 Adicionando sslmode=disable à URL do banco de dados"
    separator=$([[ "$DATABASE_URL" == *"?"* ]] && echo "&" || echo "?")
    export DATABASE_URL="${DATABASE_URL}${separator}sslmode=disable"
fi

# Exibe a URL do banco de dados (sem a senha para segurança)
DB_URL_FOR_LOG=$(echo "$DATABASE_URL" | sed -E 's/(:)[^@]*(@)/\1*****\2/')
echo "🔌 Usando banco de dados: $DB_URL_FOR_LOG"

# Testa a conexão com o banco de dados
echo "🔌 Testando conexão com o banco de dados..."
python -c "
import os
import sys
from sqlalchemy import create_engine, text

print(f'Conectando a: {os.getenv(\"DATABASE_URL\")}')

try:
    engine = create_engine(
        os.getenv('DATABASE_URL'),
        pool_pre_ping=True,
        connect_args={
            'connect_timeout': 5
        }
    )
    
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
        print(f'✅ Conexão com o banco de dados bem-sucedida! Resultado: {result.scalar()}')
        
except Exception as e:
    print(f'❌ Erro ao conectar ao banco de dados: {e}')
    print('Dica: Verifique se a variável de ambiente DATABASE_URL está configurada corretamente')
    sys.exit(1)
"

# Executa migrações
echo "🔄 Executando migrações..."
alembic upgrade head

# Inicia a aplicação
echo "🚀 Iniciando aplicação FastAPI..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT --reload --log-level debug
