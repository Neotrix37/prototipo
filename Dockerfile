# Estágio de build
FROM python:3.9-slim as builder

WORKDIR /app

# Instala as dependências do sistema necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos de requisitos
COPY requirements.txt .

# Cria um ambiente virtual e instala as dependências
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Estágio final
FROM python:3.9-slim

WORKDIR /app

# Copia o ambiente virtual do estágio de build
COPY --from=builder /opt/venv /opt/venv

# Define o caminho do ambiente virtual
ENV PATH="/opt/venv/bin:$PATH"

# Copia o código da aplicação
COPY . .

# Expõe a porta que o FastAPI está rodando
EXPOSE 8000

# Comando para rodar a aplicação
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
