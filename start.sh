#!/bin/bash

# Configurações iniciais
set -e
export PORT=${PORT:-8000}

# Navega para o diretório correto
cd /app  # Ajuste este caminho se necessário

# Logs iniciais
echo "=== Iniciando aplicação ==="
echo "Diretório atual: $(pwd)"
echo "Conteúdo do diretório:"
ls -la

# Verifica se o app/main.py existe
if [ ! -f "app/main.py" ]; then
    echo "❌ Erro: app/main.py não encontrado!"
    echo "Estrutura de diretórios:"
    find . -type f -name "*.py" | sort
    exit 1
fi

# Instala as dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# Testa a conexão com o banco de dados
echo "🔌 Testando conexão com o banco de dados..."
python -c "
import os
import sys
from sqlalchemy import create_engine

try:
    db_url = os.getenv('DATABASE_URL')
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
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --log-level debug --timeout-keep-alive 30
