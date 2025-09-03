from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from .core.config import settings
from .api.api_v1.api import api_router
from .db.session import engine, Base

# Cria as tabelas no banco de dados apenas em ambiente de desenvolvimento
if os.getenv("ENVIRONMENT") != "production":
    Base.metadata.create_all(bind=engine)

# Configuração do FastAPI com documentação
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="""
    API para o Sistema de Gestão de Posto
    
    ## Documentação
    - **Swagger UI**: [/docs](/docs)
    - **ReDoc**: [/redoc](/redoc)
    - **OpenAPI JSON**: [/openapi.json](/openapi.json)
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configuração de CORS
cors_origins = getattr(settings, 'BACKEND_CORS_ORIGINS', []) or []
if cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in cors_origins],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Inclui as rotas da API
app.include_router(api_router, prefix=settings.API_V1_STR)

# Rota de saúde
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "API está funcionando corretamente"}

# Rota raiz
@app.get("/")
async def root():
    return {
        "message": "Bem-vindo à API do Sistema de Gestão de Posto",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "api_version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }
