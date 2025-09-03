# Sistema de Gestão de Posto - Backend

Este é o backend do Sistema de Gestão de Posto, desenvolvido com FastAPI, PostgreSQL e SQLAlchemy.

## 🚀 Funcionalidades

- Autenticação JWT
- Gerenciamento de Usuários
- Gerenciamento de Clientes
- E muito mais em breve...

## 🛠️ Pré-requisitos

- Python 3.8+
- PostgreSQL
- pip (gerenciador de pacotes do Python)

## 📦 Instalação

1. Clone o repositório:
   ```bash
   git clone [URL_DO_REPOSITÓRIO]
   cd prototipo
   ```

2. Crie um ambiente virtual e ative-o:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux/MacOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure as variáveis de ambiente:
   - Crie um arquivo `.env` na raiz do projeto com base no `.env.example`
   - Atualize as configurações do banco de dados conforme necessário

5. Inicialize o banco de dados:
   ```bash
   python -m app.initial_data
   ```

## 🚀 Executando a aplicação

```bash
uvicorn app.main:app --reload
```

A aplicação estará disponível em `http://localhost:8000`

## 📚 Documentação da API

- Documentação interativa: `http://localhost:8000/api/docs`
- Documentação alternativa: `http://localhost:8000/api/redoc`

## 🔒 Autenticação

A API usa autenticação JWT. Para autenticar, faça uma requisição POST para `/api/v1/auth/login` com:

```json
{
  "username": "admin",
  "password": "admin123"
}
```

Você receberá um token que deve ser incluído no cabeçalho das requisições subsequentes:

```
Authorization: Bearer <seu_token>
```

## 🧪 Testes

Para executar os testes (em desenvolvimento):

```bash
pytest
```

## 🐳 Docker (Opcional)

Para executar com Docker:

```bash
docker-compose up --build
```

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
