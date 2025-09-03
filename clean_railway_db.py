import os
import logging
from dotenv import load_dotenv
from sqlalchemy import text, create_engine

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def limpar_banco():
    # Obtém a URL do banco de dados do arquivo .env
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        logger.error("ERRO: A variável DATABASE_URL não está definida no arquivo .env")
        return
    
    try:
        # Cria a conexão
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Desativa restrições de chave estrangeira
            conn.execute(text("SET session_replication_role = 'replica';"))
            
            # Obtém todas as tabelas
            tabelas = conn.execute(text("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public'
            """))
            
            # Remove cada tabela
            for tabela in tabelas:
                nome_tabela = tabela[0]
                conn.execute(text(f'DROP TABLE IF EXISTS \"{nome_tabela}\" CASCADE'))
                logger.info(f"Tabela {nome_tabela} removida.")
            
            # Reativa restrições
            conn.execute(text("SET session_replication_role = 'origin';"))
            conn.commit()
            
            logger.info("\nTodas as tabelas foram removidas com sucesso!")
            
    except Exception as e:
        logger.error(f"Erro: {str(e)}")
    finally:
        if 'engine' in locals():
            engine.dispose()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("ATENÇÃO: Este comando irá APAGAR TODAS AS TABELAS do banco de dados!")
    print("="*60 + "\n")
    
    confirm = input("Tem certeza que deseja continuar? (s/n): ").strip().lower()
    
    if confirm == 's':
        limpar_banco()
    else:
        print("Operação cancelada.")
