import sys
from sqlalchemy import create_engine, text
from app.core.config import settings

def create_default_payment_methods():
    """Create default payment methods in the database using raw SQL."""
    # Database connection
    print("Conectando ao banco de dados...")
    engine = create_engine(settings.DATABASE_URL)
    
    # Default payment methods
    default_methods = [
        "Dinheiro",
        "M-PESA",
        "E-Mola",
        "Cartão",
        "Transferência",
        "Millennium BIM",
        "BCI",
        "Standard Bank",
        "ABSA Bank",
        "Letshego",
        "MyBucks"
    ]

    with engine.connect() as connection:
        try:
            # Start a transaction
            with connection.begin():
                # Check if each method exists and insert if it doesn't
                for method in default_methods:
                    # Check if the method already exists
                    result = connection.execute(
                        text("SELECT id FROM formas_pagamento WHERE nome = :nome"),
                        {"nome": method}
                    ).fetchone()
                    
                    if not result:
                        # Insert the new method
                        connection.execute(
                            text("""
                                INSERT INTO formas_pagamento (nome, ativo, created_at, updated_at)
                                VALUES (:nome, 1, NOW(), NOW())
                            """),
                            {"nome": method}
                        )
                        print(f"✅ Adicionado método de pagamento: {method}")
                    else:
                        print(f"ℹ️  Método já existe: {method}")
            
            print("✅ Métodos de pagamento atualizados com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro ao adicionar métodos de pagamento: {str(e)}")
            raise

if __name__ == "__main__":
    create_default_payment_methods()