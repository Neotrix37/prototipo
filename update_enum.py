# update_enum.py
import asyncio
from sqlalchemy import create_engine, text
from app.core.config import settings

async def update_enum():
    # Create database URL from your settings
    DATABASE_URL = str(settings.DATABASE_URL)
    
    # Rest of the script remains the same...
    engine = create_engine(DATABASE_URL)
    
    sql_commands = [
        "CREATE TYPE tipomovimentacao_new AS ENUM ('ENTRADA', 'SAIDA')",
        """
        ALTER TABLE movimentacoes_caixa 
        ALTER COLUMN tipo TYPE tipomovimentacao_new 
        USING (
            CASE tipo::text
                WHEN 'Entrada' THEN 'ENTRADA'::tipomovimentacao_new
                WHEN 'Saída' THEN 'SAIDA'::tipomovimentacao_new
                ELSE 'ENTRADA'::tipomovimentacao_new
            END
        )
        """,
        "DROP TYPE tipomovimentacao",
        "ALTER TYPE tipomovimentacao_new RENAME TO tipomovimentacao"
    ]
    
    try:
        with engine.connect() as conn:
            for cmd in sql_commands:
                conn.execute(text(cmd))
                conn.commit()
            print("✅ Enum type updated successfully!")
    except Exception as e:
        print(f"❌ Error updating enum: {e}")
    finally:
        engine.dispose()

if __name__ == "__main__":
    asyncio.run(update_enum())