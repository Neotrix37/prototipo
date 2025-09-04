from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
import sys
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import JSONResponse

from .core.config import settings
from .api.api_v1.api import api_router
from .db.session import engine, Base, get_db

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Tenta criar as tabelas no banco de dados apenas em ambiente de desenvolvimento
if os.getenv("ENVIRONMENT") != "production":
    try:
        logger.info("Tentando criar tabelas no banco de dados...")
        Base.metadata.create_all(bind=engine)
        logger.info("Tabelas criadas com sucesso ou já existentes.")
    except Exception as e:
        logger.error(f"Erro ao criar tabelas: {e}")
        logger.warning("Continuando sem criar tabelas. Verifique a conexão com o banco de dados.")

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
    try:
        response = await call_next(request)
        logger.info(f"Resposta enviada: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Erro ao processar requisição {request.url}: {str(e)}")
        raise

# Rota de saúde
@app.get("/health")
async def health_check():
    """
    Rota de verificação de saúde da API
    Retorna o status da API e informações do ambiente
    """
    try:
        # Testa a conexão com o banco de dados
        db = next(get_db())
        db.execute("SELECT 1")
        db_status = "conectado"
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco de dados: {e}")
        db_status = f"erro: {str(e)}"
    
    return {
        "status": "online",
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "database": db_status,
        "version": "1.0.0"
    }

# Rota raiz
@app.get("/")
async def root():
    """
    Rota raiz da API
    Retorna informações básicas sobre a API
    """
    return {
        "message": "Bem-vindo ao Sistema de Gestão de Posto",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG
    }

# Manipulador de erros global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Erro não tratado: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor"},
    )

# Log ao iniciar a aplicação
@app.on_event("startup")
async def startup_event():
    logger.info("Iniciando a aplicação...")
    logger.info(f"Ambiente: {settings.ENVIRONMENT}")
    logger.info(f"Debug: {settings.DEBUG}")
    logger.info(f"Documentação disponível em /docs")

# Log ao encerrar a aplicação
@app.on_event("shutdown")
def shutdown_event():
    logger.info("Encerrando a aplicação...")
