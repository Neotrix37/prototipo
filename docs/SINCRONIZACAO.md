# Documentação do Sistema de Sincronização

## Visão Geral
O sistema de sincronização permite que múltiplos dispositivos/clientes mantenham seus dados atualizados com o servidor central de forma eficiente, utilizando uma abordagem baseada em timestamps para minimizar a transferência de dados.

## Requisitos
- Python 3.7+
- FastAPI
- SQLAlchemy
- JWT para autenticação

## Configuração

### Variáveis de Ambiente
```env
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=sua_chave_secreta_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 horas
```

## Estrutura do Banco de Dados
Todas as tabelas sincronizáveis devem conter as seguintes colunas:
- `id`: Chave primária
- `last_updated`: Timestamp da última atualização
- `synced`: Booleano indicando se o registro foi sincronizado
- `deleted`: Booleano para remoção lógica

## Endpoints

### Listar Tabelas Sincronizáveis
```
GET /api/v1/sync/tables
```
**Resposta de Exemplo:**
```json
{
  "available_tables": ["usuarios", "produtos", "vendas"],
  "tables_info": {
    "usuarios": {
      "model": "Usuario",
      "columns": [
        {
          "name": "id",
          "type": "INTEGER",
          "primary_key": true,
          "nullable": false
        },
        {
          "name": "nome",
          "type": "VARCHAR",
          "primary_key": false,
          "nullable": false
        }
      ],
      "total_records": 10,
      "sync_columns": ["last_updated", "synced", "deleted"]
    }
  }
}
```

### Obter Registros Atualizados
```
GET /api/v1/sync/{table_name}?last_sync=2023-01-01T00:00:00&skip=0&limit=100
```

**Parâmetros:**
- `last_sync`: Filtra registros modificados após esta data (opcional)
- `skip`: Número de registros para pular (paginação)
- `limit`: Número máximo de registros por página

**Resposta de Exemplo:**
```json
{
  "table": "usuarios",
  "total": 15,
  "skip": 0,
  "limit": 100,
  "data": [
    {"id": 1, "nome": "Usuário 1", "last_updated": "2023-01-01T10:00:00"},
    {"id": 2, "nome": "Usuário 2", "last_updated": "2023-01-02T10:00:00"}
  ],
  "last_sync": "2023-01-03T12:00:00"
}
```

### Enviar Alterações
```
POST /api/v1/sync/{table_name}
```

**Corpo da Requisição:**
```json
{
  "records": [
    {"id": 1, "nome": "Usuário Atualizado", "last_updated": "2023-01-03T10:00:00"},
    {"nome": "Novo Usuário", "last_updated": "2023-01-03T10:00:00"}
  ]
}
```

**Resposta de Sucesso:**
```json
{
  "created": 1,
  "updated": 1
}
```

## Fluxo de Sincronização

1. **Inicialização**
   - Cliente obtém token de autenticação
   - Chama `/sync/tables` para obter metadados

2. **Sincronização Inicial (Pull)**
   - Para cada tabela, chama `GET /sync/{table_name}`
   - Armazena os dados localmente
   - Armazena o `last_sync` retornado

3. **Sincronizações Posteriores**
   - Chama `GET /sync/{table_name}?last_sync={ultima_sincronizacao}`
   - Atualiza apenas os registros modificados
   - Atualiza o `last_sync`

4. **Envio de Dados (Push)**
   - Envia alterações locais via `POST /sync/{table_name}`
   - Trata a resposta para confirmar o sucesso

## Tratamento de Conflitos
- Registros são identificados unicamente pelo `id`
- O timestamp `last_updated` determina a versão mais recente
- A remoção é feita através do campo `deleted` (remoção lógica)

## Boas Práticas
1. Sempre use paginação para tabelas grandes
2. Implemente retry com backoff exponencial
3. Valide os dados antes de enviar
4. Mantenha um log de operações de sincronização
5. Implemente tratamento de erros adequado

## Exemplo de Código do Cliente

```python
import requests
from datetime import datetime, timezone

BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "seu_token_jwt_aqui"
headers = {"Authorization": f"Bearer {TOKEN}"}

def sincronizar_tabela(nome_tabela, ultima_sincronizacao=None):
    params = {}
    if ultima_sincronizacao:
        params["last_sync"] = ultima_sincronizacao.isoformat()
    
    response = requests.get(
        f"{BASE_URL}/sync/{nome_tabela}",
        headers=headers,
        params=params
    )
    response.raise_for_status()
    return response.json()

def enviar_alteracoes(nome_tabela, registros):
    response = requests.post(
        f"{BASE_URL}/sync/{nome_tabela}",
        headers=headers,
        json={"records": registros}
    )
    response.raise_for_status()
    return response.json()
```

## Limitações Conhecidas
1. Não suporta transações distribuídas
2. Requer conexão com a internet para sincronização
3. Pode exigir ajustes para tabelas muito grandes

## Próximos Passos
1. Implementar suporte a operações em lote
2. Adicionar suporte a notificações em tempo real
3. Melhorar tratamento de conflitos
4. Adicionar suporte a sincronização parcial de colunas
