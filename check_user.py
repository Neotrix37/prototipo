from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Configuração da conexão
DATABASE_URL = "postgresql://postgres:PVVHzsCZDuQiwnuziBfcgukYLCuCxdau@interchange.proxy.rlwy.net:33939/railway"

# Cria o engine
engine = create_engine(DATABASE_URL)

# Cria uma sessão
Session = sessionmaker(bind=engine)
session = Session()

# Consulta os usuários
print("Usuários cadastrados no banco de dados:")
result = session.execute(text("SELECT id, usuario, nome, ativo FROM usuarios"))
users = result.fetchall()

if not users:
    print("Nenhum usuário cadastrado no banco de dados!")
else:
    for user in users:
        print(f"ID: {user[0]}, Usuário: {user[1]}, Nome: {user[2]}, Ativo: {user[3]}")

# Fecha a sessão
session.close()