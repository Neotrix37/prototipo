Write-Host "Iniciando a aplicacao..."

# Carregar variáveis de ambiente
if (Test-Path ".env.production") {
    Write-Host "Carregando variaveis de .env.production..."
    Get-Content .env.production | ForEach-Object {
        $name, $value = $_.split('=')
        if ($name -and $name[0] -ne '#') {
            Set-Item -Path "env:$name" -Value $value
        }
    }
}

# Configuracoes basicas
if (-not $env:HOST) { $env:HOST = "0.0.0.0" }
if (-not $env:PORT) { $env:PORT = 8000 }
if (-not $env:ENVIRONMENT) { $env:ENVIRONMENT = "production" }

Write-Host "Configuracoes:"
Write-Host "- ENVIRONMENT: $env:ENVIRONMENT"
Write-Host "- HOST: $env:HOST"
Write-Host "- PORT: $env:PORT"

# Instalar dependencias
Write-Host "Instalando dependencias..."
python -m pip install -r requirements.txt

# Executar migracoes
Write-Host "Executando migracoes..."
$env:PYTHONPATH = $PSScriptRoot

# Verificar se o Alembic está instalado
if (-not (Get-Command alembic -ErrorAction SilentlyContinue)) {
    Write-Error "Alembic não encontrado. Instalando..."
    python -m pip install alembic
}

# Executar migracoes usando o Python diretamente
$env:PYTHONPATH = "C:\Users\saide\AppData\Local\Programs\Python\Python311\Lib\site-packages\alembic"
alembic upgrade head
if ($LASTEXITCODE -ne 0) {
    Write-Error "Falha ao executar migracoes. Verifique se o banco de dados está acessível e as configuracoes estao corretas."
    exit 1
}

# Iniciar a aplicacao
Write-Host "Iniciando o servidor..."
python -m uvicorn app.main:app --host $env:HOST --port $env:PORT --workers 4