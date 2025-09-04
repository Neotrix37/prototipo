import asyncio
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings

async def update_enum():
    # Create database URL from settings
    DATABASE_URL = str(settings.DATABASE_URL)
    
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    # SQL commands to update the enum
    sql_commands = [
        """
        -- Check if the table exists
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'movimentacoes_caixa') THEN
                -- Create a backup of the existing data
                CREATE TABLE IF NOT EXISTS movimentacoes_caixa_backup AS 
                SELECT * FROM movimentacoes_caixa;
                
                RAISE NOTICE 'Backup created: movimentacoes_caixa_backup';
            END IF;
        END $$;
        """,
        
        # Drop constraints that reference the enum
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'movimentacoes_caixa_tipo_check') THEN
                ALTER TABLE movimentacoes_caixa DROP CONSTRAINT movimentacoes_caixa_tipo_check;
            END IF;
        END $$;
        """,
        
        # Create a new type with the correct values
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipomovimentacao_new') THEN
                CREATE TYPE tipomovimentacao_new AS ENUM ('ENTRADA', 'SAIDA');
                RAISE NOTICE 'Created new enum type tipomovimentacao_new';
            END IF;
        END $$;
        """,
        
        # Update the column to use the new type
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'movimentacoes_caixa') THEN
                -- First convert to text
                ALTER TABLE movimentacoes_caixa ALTER COLUMN tipo TYPE text;
                
                -- Then to the new enum type
                ALTER TABLE movimentacoes_caixa 
                ALTER COLUMN tipo TYPE tipomovimentacao_new 
                USING (
                    CASE tipo
                        WHEN 'Entrada' THEN 'ENTRADA'::tipomovimentacao_new
                        WHEN 'Saída' THEN 'SAIDA'::tipomovimentacao_new
                        WHEN 'entrada' THEN 'ENTRADA'::tipomovimentacao_new
                        WHEN 'saida' THEN 'SAIDA'::tipomovimentacao_new
                        ELSE 'ENTRADA'::tipomovimentacao_new
                    END
                );
                
                RAISE NOTICE 'Updated column to use new enum type';
            END IF;
        END $$;
        """,
        
        # Drop the old type if it exists
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipomovimentacao') THEN
                DROP TYPE tipomovimentacao CASCADE;
                RAISE NOTICE 'Dropped old enum type tipomovimentacao with CASCADE';
            END IF;
        END $$;
        """,
        
        # Rename the new type
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipomovimentacao_new') THEN
                ALTER TYPE tipomovimentacao_new RENAME TO tipomovimentacao;
                RAISE NOTICE 'Renamed tipomovimentacao_new to tipomovimentacao';
            END IF;
        END $$;
        """
    ]
    
    try:
        with engine.connect() as conn:
            # Start a transaction
            trans = conn.begin()
            try:
                for cmd in sql_commands:
                    print("Executing:", cmd.split('\n')[1].strip() if '\n' in cmd else cmd[:100])
                    conn.execute(text(cmd))
                    conn.commit()
                
                # Verify the changes
                result = conn.execute(text("SELECT enum_range(NULL::tipomovimentacao);")).scalar()
                print(f"✅ Enum type updated successfully! Current values: {result}")
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Error during update: {e}")
                raise
            else:
                trans.commit()
                print("✅ Transaction committed successfully!")
                
    except SQLAlchemyError as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)
    finally:
        engine.dispose()

if __name__ == "__main__":
    print("🚀 Starting enum update process...")
    asyncio.run(update_enum())
    print("✨ Script completed!")
