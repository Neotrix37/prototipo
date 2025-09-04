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

# Testa a conexão com o banco de dados
echo "🔌 Testando conexão com o banco de dados..."
python -c "
import os
import sys
from sqlalchemy import create_engine

try:
    db_url = os.getenv('DATABASE_URL')
    print(f'Conectando a: {db_url}')
    engine = create_engine(db_url, connect_args={"connect_timeout": 5})
    with engine.connect() as conn:
        conn.execute('SELECT 1')
    print('✅ Conexão com o banco de dados bem-sucedida!')
except Exception as e:
    print(f'❌ Erro ao conectar ao banco de dados: {e}')
    sys.exit(1)
"

# Executa migrações
echo "🔄 Executando migrações..."
alembic upgrade head

# Inicia a aplicação
echo "🚀 Iniciando aplicação FastAPI..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT --log-level debug
