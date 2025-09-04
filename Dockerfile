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

# Instala as dependências
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia o restante da aplicação
COPY . .

# Expõe a porta padrão
EXPOSE 8000

# Define o comando de inicialização
CMD ["bash", "start.sh"]
