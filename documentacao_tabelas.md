# Documentação das Tabelas do Banco de Dados

## 1. Tabela `usuarios`

Esta tabela armazena informações sobre os usuários do sistema, incluindo funcionários e administradores.

```sql
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    usuario TEXT NOT NULL UNIQUE,
    senha TEXT NOT NULL,
    nivel INTEGER NOT NULL DEFAULT 1,
    ativo INTEGER NOT NULL DEFAULT 1,
    is_admin INTEGER NOT NULL DEFAULT 0,
    salario REAL DEFAULT 0,
    pode_abastecer INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Campos:**
- `id`: Chave primária auto-incrementável.
- `nome`: Nome completo do usuário.
- `usuario`: Nome de usuário para login (deve ser único).
- `senha`: Senha do usuário (armazenada como hash).
- `nivel`: Nível de acesso do usuário (padrão 1).
- `ativo`: Indica se o usuário está ativo (1) ou inativo (0).
- `is_admin`: Indica se o usuário é um administrador (1) ou não (0).
- `salario`: Salário do usuário (padrão 0).
- `pode_abastecer`: Indica se o usuário pode realizar abastecimentos (1) ou não (0).
- `created_at`: Carimbo de data/hora da criação do registro.
- `updated_at`: Carimbo de data/hora da última atualização do registro.

## 2. Tabela `clientes`

Esta tabela armazena informações sobre os clientes.

```sql
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    nuit TEXT,
    telefone TEXT,
    email TEXT,
    endereco TEXT,
    especial INTEGER DEFAULT 0,
    desconto_divida REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Campos:**
- `id`: Chave primária auto-incrementável.
- `nome`: Nome completo do cliente.
- `nuit`: Número Único de Identificação Tributária do cliente.
- `telefone`: Número de telefone do cliente.
- `email`: Endereço de e-mail do cliente.
- `endereco`: Endereço físico do cliente.
- `especial`: Indica se o cliente é especial (1) ou não (0).
- `desconto_divida`: Valor de desconto em dívida para o cliente.
- `created_at`: Carimbo de data/hora da criação do registro.
- `updated_at`: Carimbo de data/hora da última atualização do registro.

## 3. Tabela `compras`

Esta tabela registra as compras de produtos feitas a fornecedores.

```sql
CREATE TABLE IF NOT EXISTS compras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fornecedor TEXT NOT NULL,
    valor_total REAL NOT NULL,
    usuario_id INTEGER NOT NULL,
    observacoes TEXT,
    data_compra TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
);
```

**Campos:**
- `id`: Chave primária auto-incrementável.
- `fornecedor`: Nome do fornecedor da compra.
- `valor_total`: Valor total da compra.
- `usuario_id`: ID do usuário que registrou a compra (chave estrangeira para `usuarios`).
- `observacoes`: Observações adicionais sobre a compra.
- `data_compra`: Carimbo de data/hora da compra.

## 4. Tabela `compra_itens`

Esta tabela detalha os itens de cada compra.

```sql
CREATE TABLE IF NOT EXISTS compra_itens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    compra_id INTEGER NOT NULL,
    produto_id INTEGER,
    produto_nome TEXT NOT NULL,
    quantidade REAL NOT NULL,
    preco_unitario REAL NOT NULL,
    preco_venda REAL NOT NULL,
    lucro_unitario REAL NOT NULL,
    lucro_total REAL NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (compra_id) REFERENCES compras(id) ON DELETE CASCADE,
    FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE SET NULL
);
```

**Campos:**
- `id`: Chave primária auto-incrementável.
- `compra_id`: ID da compra à qual o item pertence (chave estrangeira para `compras`).
- `produto_id`: ID do produto (chave estrangeira para `produtos`). Pode ser NULL se o produto for excluído.
- `produto_nome`: Nome do produto no momento da compra.
- `quantidade`: Quantidade do produto comprado.
- `preco_unitario`: Preço unitário do produto na compra.
- `preco_venda`: Preço de venda do produto no momento da compra.
- `lucro_unitario`: Lucro unitário esperado do produto.
- `lucro_total`: Lucro total esperado do produto.
- `data_criacao`: Carimbo de data/hora da criação do registro do item.

## 5. Tabela `produtos`

Esta tabela armazena informações sobre os produtos disponíveis.

```sql
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL UNIQUE,
    nome TEXT NOT NULL,
    descricao TEXT,
    preco_custo REAL NOT NULL,
    preco_venda REAL NOT NULL,
    estoque REAL NOT NULL DEFAULT 0,
    estoque_minimo REAL NOT NULL DEFAULT 0,
    ativo INTEGER NOT NULL DEFAULT 1,
    venda_por_peso INTEGER DEFAULT 0,
    unidade_medida TEXT DEFAULT 'un',
    categoria_id INTEGER,
    fornecedor_id INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (categoria_id) REFERENCES categorias (id),
    FOREIGN KEY (fornecedor_id) REFERENCES fornecedores (id)
);
```

**Campos:**
- `id`: Chave primária auto-incrementável.
- `codigo`: Código único do produto.
- `nome`: Nome do produto.
- `descricao`: Descrição detalhada do produto.
- `preco_custo`: Preço de custo do produto.
- `preco_venda`: Preço de venda do produto.
- `estoque`: Quantidade atual em estoque.
- `estoque_minimo`: Quantidade mínima em estoque para alerta.
- `ativo`: Indica se o produto está ativo (1) ou inativo (0).
- `venda_por_peso`: Indica se o produto é vendido por peso (1) ou por unidade (0).
- `unidade_medida`: Unidade de medida do produto (ex: 'kg', 'un').
- `categoria_id`: ID da categoria do produto (chave estrangeira para `categorias`).
- `fornecedor_id`: ID do fornecedor do produto (chave estrangeira para `fornecedores`).
- `created_at`: Carimbo de data/hora da criação do registro.
- `updated_at`: Carimbo de data/hora da última atualização do registro.

## 6. Tabela `vendas`

Esta tabela registra as vendas realizadas no sistema.

```sql
CREATE TABLE IF NOT EXISTS vendas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    total REAL NOT NULL,
    forma_pagamento TEXT NOT NULL,
    valor_recebido REAL,
    troco REAL,
    data_venda DATETIME NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
);
```

**Campos:**
- `id`: Chave primária auto-incrementável.
- `usuario_id`: ID do usuário que realizou a venda (chave estrangeira para `usuarios`).
- `total`: Valor total da venda.
- `forma_pagamento`: Forma de pagamento utilizada (ex: 'Dinheiro', 'M-PESA').
- `valor_recebido`: Valor recebido do cliente.
- `troco`: Valor do troco dado ao cliente.
- `data_venda`: Data e hora da venda.

## 7. Tabela `itens_venda`

Esta tabela detalha os itens de cada venda.

```sql
CREATE TABLE IF NOT EXISTS itens_venda (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venda_id INTEGER NOT NULL,
    produto_id INTEGER NOT NULL,
    quantidade INTEGER NOT NULL,
    preco_unitario REAL NOT NULL,
    preco_custo_unitario REAL NOT NULL,
    subtotal REAL NOT NULL,
    FOREIGN KEY (venda_id) REFERENCES vendas (id),
    FOREIGN KEY (produto_id) REFERENCES produtos (id)
);
```

**Campos:**
- `id`: Chave primária auto-incrementável.
- `venda_id`: ID da venda à qual o item pertence (chave estrangeira para `vendas`).
- `produto_id`: ID do produto vendido (chave estrangeira para `produtos`).
- `quantidade`: Quantidade do produto vendido.
- `preco_unitario`: Preço unitário do produto na venda.
- `preco_custo_unitario`: Preço de custo unitário do produto no momento da venda.
- `subtotal`: Subtotal do item (quantidade * preco_unitario).

## 8. Tabela `movimentacao_caixa`

Esta tabela registra todas as entradas e saídas de dinheiro do caixa.

```sql
CREATE TABLE IF NOT EXISTS movimentacao_caixa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_movimento DATETIME NOT NULL,
    tipo TEXT NOT NULL,  -- 'Entrada' ou 'Saída'
    valor REAL NOT NULL,
    descricao TEXT NOT NULL,
    categoria TEXT,
    usuario_id INTEGER,
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
);
```

**Campos:**
- `id`: Chave primária auto-incrementável.
- `data_movimento`: Data e hora da movimentação.
- `tipo`: Tipo de movimentação ('Entrada' ou 'Saída').
- `valor`: Valor da movimentação.
- `descricao`: Descrição da movimentação.
- `categoria`: Categoria da movimentação (opcional).
- `usuario_id`: ID do usuário que realizou a movimentação (chave estrangeira para `usuarios`).

## 9. Tabela `categorias_despesa`

Esta tabela armazena as categorias de despesas.

```sql
CREATE TABLE IF NOT EXISTS categorias_despesa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE
);
```

**Campos:**
- `id`: Chave primária auto-incrementável.
- `nome`: Nome da categoria de despesa (deve ser único).

## 10. Tabela `despesas_recorrentes`

Esta tabela armazena informações sobre despesas recorrentes.

```sql
CREATE TABLE IF NOT EXISTS despesas_recorrentes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL,
    categoria TEXT NOT NULL,
    descricao TEXT NOT NULL,
    valor REAL NOT NULL,
    data_vencimento DATE NOT NULL,
    data_pagamento DATE,
    status TEXT NOT NULL DEFAULT 'Pendente',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Campos:**
- `id`: Chave primária auto-incrementável.
- `tipo`: Tipo da despesa (ex: 'Mensal', 'Anual').
- `categoria`: Categoria da despesa.
- `descricao`: Descrição da despesa.
- `valor`: Valor da despesa.
- `data_vencimento`: Data de vencimento da despesa.
- `data_pagamento`: Data de pagamento da despesa (pode ser NULL).
- `status`: Status da despesa ('Pendente', 'Pago', etc.).
- `created_at`: Carimbo de data/hora da criação do registro.
- `updated_at`: Carimbo de data/hora da última atualização do registro.

## 11. Tabela `formas_pagamento`

Esta tabela armazena as formas de pagamento aceitas pelo sistema.

```sql
CREATE TABLE IF NOT EXISTS formas_pagamento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    ativo INTEGER DEFAULT 1
);
```

**Campos:**
- `id`: Chave primária auto-incrementável.
- `nome`: Nome da forma de pagamento (deve ser único).
- `ativo`: Indica se a forma de pagamento está ativa (1) ou inativa (0).

## 12. Tabela `fechamentos_caixa`

Esta tabela registra os fechamentos de caixa.

```sql
CREATE TABLE IF NOT EXISTS fechamentos_caixa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    data_fechamento DATETIME NOT NULL,
    valor_sistema REAL NOT NULL,
    valor_informado REAL NOT NULL,
    diferenca REAL NOT NULL,
    observacoes TEXT,
    status TEXT DEFAULT 'Pendente',
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
);
```

**Campos:**
- `id`: Chave primária auto-incrementável.
- `usuario_id`: ID do usuário que realizou o fechamento (chave estrangeira para `usuarios`).
- `data_fechamento`: Data e hora do fechamento do caixa.
- `valor_sistema`: Valor total registrado pelo sistema.
- `valor_informado`: Valor total informado pelo operador.
- `diferenca`: Diferença entre o valor do sistema e o valor informado.
- `observacoes`: Observações adicionais sobre o fechamento.
- `status`: Status do fechamento ('Pendente', 'Concluído', etc.).

## 13. Tabela `fechamentos_formas_pagamento`

Esta tabela detalha os valores de fechamento por forma de pagamento.

```sql
CREATE TABLE IF NOT EXISTS fechamentos_formas_pagamento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fechamento_id INTEGER NOT NULL,
    forma_pagamento TEXT NOT NULL,
    valor_sistema REAL NOT NULL,
    valor_informado REAL NOT NULL,
    diferenca REAL NOT NULL,
    FOREIGN KEY (fechamento_id) REFERENCES fechamentos_caixa (id)
);
```

**Campos:**
- `id`: Chave primária auto-incrementável.
- `fechamento_id`: ID do fechamento de caixa (chave estrangeira para `fechamentos_caixa`).
- `forma_pagamento`: Forma de pagamento (ex: 'Dinheiro', 'M-PESA').
- `valor_sistema`: Valor registrado pelo sistema para esta forma de pagamento.
- `valor_informado`: Valor informado pelo operador para esta forma de pagamento.
- `diferenca`: Diferença entre os valores do sistema e informado para esta forma de pagamento.

## 14. Tabela `vendas_fechamentos`

Esta tabela relaciona as vendas aos seus respectivos fechamentos de caixa.

```sql
CREATE TABLE IF NOT EXISTS vendas_fechamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venda_id INTEGER NOT NULL,
    fechamento_id INTEGER NOT NULL,
    FOREIGN KEY (venda_id) REFERENCES vendas (id),
    FOREIGN KEY (fechamento_id) REFERENCES fechamentos_caixa (id)
);
```

**Campos:**
- `id`: Chave primária auto-incrementável.
- `venda_id`: ID da venda (chave estrangeira para `vendas`).
- `fechamento_id`: ID do fechamento de caixa (chave estrangeira para `fechamentos_caixa`).

## 15. Tabela `retiradas_caixa`

Esta tabela registra as retiradas de dinheiro do caixa.

```sql
CREATE TABLE IF NOT EXISTS retiradas_caixa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    aprovador_id INTEGER,
    valor REAL NOT NULL,
    motivo TEXT NOT NULL,
    observacao TEXT,
    origem TEXT NOT NULL DEFAULT 'vendas',
    status TEXT NOT NULL DEFAULT 'pendente',
    data_retirada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_aprovacao TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (aprovador_id) REFERENCES usuarios(id)
);
```

**Campos:**
- `id`: Chave primária auto-incrementável.
- `usuario_id`: ID do usuário que solicitou a retirada (chave estrangeira para `usuarios`).
- `aprovador_id`: ID do usuário que aprovou a retirada (chave estrangeira para `usuarios`, pode ser NULL).
- `valor`: Valor da retirada.
- `motivo`: Motivo da retirada.
- `observacao`: Observações adicionais sobre a retirada.
- `origem`: Origem da retirada (ex: 'vendas').
- `status`: Status da retirada ('pendente', 'aprovado', 'rejeitado', etc.).
- `data_retirada`: Data e hora da solicitação da retirada.
- `data_aprovacao`: Data e hora da aprovação da retirada (pode ser NULL).
- `created_at`: Carimbo de data/hora da criação do registro.
- `updated_at`: Carimbo de data/hora da última atualização do registro.