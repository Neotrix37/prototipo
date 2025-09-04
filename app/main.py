from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

from .core.config import settings
from .api.api_v1.api import api_router
from .db.session import engine, Base

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cria as tabelas no banco de dados apenas em ambiente de desenvolvimento
if os.getenv("ENVIRONMENT") != "production":
    logger.info("Criando tabelas no banco de dados...")
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
    logger.info(f"Configurando CORS para origens: {cors_origins}")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in cors_origins],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Inclui as rotas da API
app.include_router(api_router, prefix=settings.API_V1_STR)

# Middleware para log de requisições
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Requisição recebida: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Resposta enviada: {response.status_code}")
    return response

# Rota de saúde
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "message": "API está funcionando corretamente",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "database_connected": True
    }

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
