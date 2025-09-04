#!/bin/bash

# Cores para formatação
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Iniciando configuração do ambiente de desenvolvimento...${NC}"

# Verifica se o Python está instalado
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Python 3 não encontrado. Por favor, instale o Python 3.8 ou superior.${NC}"
    exit 1
fi

# Cria e ativa o ambiente virtual
echo -e "${GREEN}Criando ambiente virtual...${NC}"
python -m venv venv

if [ "$OSTYPE" == "msys" ] || [ "$OSTYPE" == "cygwin" ]; then
    # Windows
    source venv/Scripts/activate
else
    # Linux/MacOS
    source venv/bin/activate
fi

# Atualiza o pip
echo -e "${GREEN}Atualizando pip...${NC}"
pip install --upgrade pip

# Instala as dependências
echo -e "${GREEN}Instalando dependências...${NC}"
pip install -r requirements.txt

# Configura o banco de dados
echo -e "${GREEN}Configurando banco de dados...${NC}"
python -m app.initial_data

# Cria a primeira migração do Alembic
echo -e "${GREEN}Criando migração inicial...${NC}"
alembic revision --autogenerate -m "Migração inicial"
alembic upgrade head

echo -e "\n${GREEN}✅ Configuração concluída com sucesso!${NC}"
echo -e "\nPara iniciar o servidor de desenvolvimento, execute:\n"
echo -e "  ${YELLOW}source venv/bin/activate  # Ativa o ambiente virtual (Linux/Mac)${NC}"
echo -e "  ${YELLOW}source venv/Scripts/activate  # Ativa o ambiente virtual (Windows)${NC}"
echo -e "  ${YELLOW}./start.sh  # Inicia o servidor${NC}\n"
echo -e "Acesse a documentação da API em: ${YELLOW}http://localhost:8000/api/docs${NC}\n"

# Get the port from the environment variable or use 8000 as default
PORT=${PORT:-8000}

# Start the application
uvicorn app.main:app --host 0.0.0.0 --port $PORT
