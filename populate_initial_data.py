import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Adiciona o diretório raiz ao path para que possamos importar os módulos do projeto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Carrega as variáveis de ambiente
load_dotenv()

def populate_initial_data():
    """Popula o banco de dados com dados iniciais."""
    # Obtém a URL do banco de dados do arquivo .env
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("ERRO: A variável DATABASE_URL não está definida no arquivo .env")
        return False
    
    try:
        # Cria a engine e a sessão
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Importa os modelos necessários
        from app.models.usuario import Usuario
        from app.models.fornecedor import Fornecedor
        from app.models.categorias import Categoria
        from app.core import security
        
        print("Verificando e adicionando usuário administrador...")
        # Verifica se já existe um usuário administrador
        admin = db.query(Usuario).filter(Usuario.usuario == "admin37").first()
        
        if not admin:
            # Cria o usuário administrador padrão
            admin_user = Usuario(
                nome="Administrador do Sistema",
                usuario="admin37",
                senha=security.get_password_hash("842384"),
                nivel=3,  # Nível de gerente
                ativo=True,
                is_admin=True,
                pode_abastecer=True
            )
            db.add(admin_user)
            db.commit()
            print("Usuário administrador criado com sucesso!")
        else:
            print("Usuário administrador já existe.")
        
        print("\nVerificando e adicionando fornecedor padrão...")
        # Verifica se já existe um fornecedor padrão
        fornecedor_padrao = db.query(Fornecedor).filter(
            Fornecedor.nome.ilike("Fornecedor Padrão")
        ).first()
        
        if not fornecedor_padrao:
            # Cria o fornecedor padrão
            fornecedor = Fornecedor(
                nome="Fornecedor Padrão",
                telefone="(00) 0000-0000",
                email="contato@fornecedorpadrao.com.br",
                endereco="Endereço não informado",
                ativo=True
            )
            db.add(fornecedor)
            db.commit()
            print("Fornecedor padrão criado com sucesso!")
        else:
            print("Fornecedor padrão já existe.")
        
        print("\nVerificando e adicionando categorias padrão...")
        # Lista de categorias padrão
        categorias_padrao = [
            {"nome": "Alimentos", "descricao": "Produtos alimentícios em geral"},
            {"nome": "Bebidas", "descricao": "Bebidas em geral"},
            {"nome": "Limpeza", "descricao": "Produtos de limpeza"},
            {"nome": "Higiene", "descricao": "Produtos de higiene pessoal"},
            {"nome": "Congelados", "descricao": "Produtos congelados"},
            {"nome": "Mercearia", "descricao": "Produtos de mercearia em geral"},
            {"nome": "Padaria", "descricao": "Produtos de padaria"},
            {"nome": "Hortifruti", "descricao": "Frutas, legumes e verduras"},
            {"nome": "Açougue", "descricao": "Carnes em geral"},
            {"nome": "Laticínios", "descricao": "Leite e derivados"},
            {"nome": "Outros", "descricao": "Outros tipos de produtos"}
        ]
        
        categorias_adicionadas = 0
        for cat_data in categorias_padrao:
            # Verifica se a categoria já existe
            if not db.query(Categoria).filter(Categoria.nome.ilike(cat_data["nome"])).first():
                categoria = Categoria(**cat_data)
                db.add(categoria)
                categorias_adicionadas += 1
        
        if categorias_adicionadas > 0:
            db.commit()
            print(f"{categorias_adicionadas} categorias padrão adicionadas.")
        else:
            print("Todas as categorias padrão já existem.")
        
        return True
        
    except Exception as e:
        print(f"Erro ao popular os dados iniciais: {str(e)}")
        if 'db' in locals():
            db.rollback()
        return False
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("POPULAÇÃO INICIAL DO BANCO DE DADOS")
    print("Este comando irá adicionar dados iniciais ao banco de dados")
    print("="*60 + "\n")
    
    confirm = input("Tem certeza que deseja continuar? (s/n): ").strip().lower()
    
    if confirm == 's':
        if populate_initial_data():
            print("\nDados iniciais adicionados com sucesso!")
        else:
            print("\nFalha ao adicionar os dados iniciais. Verifique as mensagens de erro acima.")
    else:
        print("\nOperação cancelada pelo usuário.")
    
    input("\nPressione Enter para sair...")
