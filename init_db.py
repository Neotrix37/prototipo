import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Carrega as variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_database():
    """Inicializa o banco de dados com todas as tabelas e dados iniciais"""
    # Obtém a URL do banco de dados do arquivo .env
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        logger.error("ERRO: A variável DATABASE_URL não está definida no arquivo .env")
        return False
    
    try:
        # Cria a engine e a sessão
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Importa os modelos para garantir que todas as tabelas sejam criadas
        from app.models.usuario import Usuario
        from app.models.cliente import Cliente
        from app.models.fornecedor import Fornecedor
        from app.models.categorias import Categoria
        from app.models.produtos import Produto
        from app.db.base import Base
        
        # Cria todas as tabelas
        logger.info("Criando tabelas...")
        Base.metadata.create_all(bind=engine)
        
        # Verifica se já existe um usuário administrador
        admin = db.query(Usuario).filter(Usuario.usuario == "admin37").first()
        
        if not admin:
            # Cria o usuário administrador padrão
            from app.core import security
            
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
            logger.info("Usuário administrador criado com sucesso!")
        
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
            logger.info("Fornecedor padrão criado com sucesso!")
        
        # Verifica se existem categorias cadastradas
        categorias = db.query(Categoria).count()
        if categorias == 0:
            # Adiciona categorias padrão
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
            
            for cat_data in categorias_padrao:
                # Verifica se a categoria já existe
                if not db.query(Categoria).filter(Categoria.nome.ilike(cat_data["nome"])).first():
                    categoria = Categoria(**cat_data)
                    db.add(categoria)
            
            db.commit()
            logger.info(f"{len(categorias_padrao)} categorias padrão adicionadas.")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro ao inicializar o banco de dados: {str(e)}")
        if 'db' in locals():
            db.rollback()
        return False
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("INICIALIZAÇÃO DO BANCO DE DADOS")
    print("Este comando irá criar todas as tabelas e adicionar dados iniciais")
    print("="*60 + "\n")
    
    confirm = input("Tem certeza que deseja continuar? (s/n): ").strip().lower()
    
    if confirm == 's':
        if init_database():
            print("\nBanco de dados inicializado com sucesso!")
        else:
            print("\nFalha ao inicializar o banco de dados. Verifique os logs para mais informações.")
    else:
        print("\nOperação cancelada pelo usuário.")
    
    input("\nPressione Enter para sair...")
