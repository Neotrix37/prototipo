import psycopg2
from urllib.parse import urlparse

# Configuração da conexão
db_url = "postgresql://postgres:PVVHzsCZDuQiwnuziBfcgukYLCuCxdau@interchange.proxy.rlwy.net:33939/railway"

# Extrai os parâmetros da URL
result = urlparse(db_url)
username = result.username
password = result.password
database = result.path[1:]  # Remove a barra inicial
hostname = result.hostname
port = result.port

try:
    # Conecta ao banco de dados
    conn = psycopg2.connect(
        dbname=database,
        user=username,
        password=password,
        host=hostname,
        port=port
    )
    
    # Cria um cursor
    cursor = conn.cursor()
    
    # Instala a extensão pgcrypto
    cursor.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    conn.commit()
    print("Extensão pgcrypto instalada com sucesso!")
    
    # Fecha a conexão
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Erro ao instalar a extensão pgcrypto: {str(e)}")