from sqlalchemy.ext.declarative import declarative_base

# Base para os modelos SQLAlchemy
Base = declarative_base()

# Exporta apenas o Base
__all__ = ['Base']
