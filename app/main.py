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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui os roteadores da API
app.include_router(api_router, prefix="/api/v1")

# Middleware para log de requisições
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Requisição recebida: {request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.info(f"Resposta enviada: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Erro ao processar requisição: {str(e)}")
        raise

# Rota de saúde
@app.get("/health", tags=["health"])
async def health_check():
    """
    Rota de verificação de saúde da API
    Retorna o status da API e informações do ambiente
    """
    import os
    from datetime import datetime
    
    # Tenta conectar ao banco de dados
    db_status = "healthy"
    try:
        db = next(get_db())
        db.execute("SELECT 1")
        db.close()
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "database": db_status,
        "version": "1.0.0"
    }

# Rota raiz
@app.get("/", tags=["root"])
async def root():
    """
    Rota raiz da API
    Retorna informações básicas sobre a API
    """
    import os
    from datetime import datetime
    
    return {
        "message": "Bem-vindo à API do Sistema de Gestão de Posto",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "timestamp": datetime.utcnow().isoformat(),
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        }
    }

# Manipulador de erros global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Erro não tratado: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Ocorreu um erro interno no servidor"},
    )

# Log ao iniciar a aplicação
@app.on_event("startup")
async def startup_event():
    import socket
    hostname = socket.gethostname()
    port = os.getenv("PORT", 8000)
    logger.info(f"Iniciando aplicação em http://{hostname}:{port}")
    logger.info(f"Ambiente: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"Documentação disponível em: http://{hostname}:{port}/docs")

# Log ao encerrar a aplicação
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Encerrando aplicação...")
