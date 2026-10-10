# Cafeteria Control — V0.1

Aplicação local para controle de produtos, custos, vendas, compras e estoque de uma cafeteria.

## Stack

- Python 3.11+
- Flask
- Flask-SQLAlchemy
- Flask-Migrate (para versionamento do banco)
- SQLite
- Jinja2
- HTML/CSS/JavaScript

## Rodando no MacBook M1

No Terminal, dentro da pasta do projeto:

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
python run.py
```

Abra no navegador:

`http://127.0.0.1:5000`

O banco será criado automaticamente em:

`instance/cafeteria.db`

Na primeira execução, os produtos informados no projeto são cadastrados automaticamente.

## Regras da V0.1

- Produtos têm custo atual, preço de venda, estoque e estoque mínimo.
- Venda aceita Pix ou SumUp.
- O custo vigente é copiado para cada item da venda para preservar o histórico.
- Venda baixa estoque.
- Compra aumenta estoque.
- Compra recalcula o custo médio ponderado.
- Ajuste de estoque cria movimentação histórica.
- Dashboard mostra vendas, custo e lucro bruto.
- Produtos com margem abaixo de 30% são destacados.

## Próximos passos

1. Melhorar lançamento de compras para múltiplos itens.
2. Relatórios por período.
3. Fechamento diário.
4. Importação/integração SumUp.
5. Controle de fornecedores.
6. Backup automático do SQLite.
7. Ficha técnica para produtos produzidos pela cafeteria.

## Sistema de Migrations (Flask-Migrate)

⚠️ **IMPORTANTE**: O projeto usa Flask-Migrate para versionar o banco de dados. SEMPRE use migrations para mudanças estruturais - NUNCA delete o banco de dados para recriar tabelas.

### Como usar migrations:

**1. Após alterar models (adicionar/remover colunas, tabelas):**
```bash
source .venv/bin/activate
flask db migrate -m "Descrição da mudança"
```

**2. Aplicar migration ao banco:**
```bash
flask db upgrade
```

**3. Verificar status das migrations:**
```bash
flask db current    # Mostra migration atual
flask db history     # Mostra histórico de migrations
```

**4. Reverter migration (se necessário):**
```bash
flask db downgrade
```

### Quando criar migrations:
- Sempre que alterar qualquer model (add/remove colunas, tabelas)
- Sempre que mudar tipos de dados
- Sempre que adicionar/alterar relações entre models

### Vantagens do sistema de migrations:
- ✅ Preserva todos os dados existentes
- ✅ Histórico completo de mudanças
- ✅ Pode reverter mudanças se necessário
- ✅ Equipes podem manter bancos sincronizados
- ✅ Nenhuma perda de dados ao evoluir o schema

## Backup do Banco de Dados

⚠️ **IMPORTANTE**: O banco de dados (`instance/cafeteria.db`) NÃO é versionado no Git (está no `.gitignore`). Com Flask-Migrate, as migrations (versões do schema) são versionadas, mas os DADOS não.

### Como fazer backup:

```bash
# Criar backup
cp instance/cafeteria.db instance/cafeteria.db.backup.$(date +%Y%m%d_%H%M%S)

# Ou para uma pasta específica
cp instance/cafeteria.db ~/backups/cafeteria.db.$(date +%Y%m%d_%H%M%S)
```

### Quando fazer backup:

- Antes de migrations complexas ou arriscadas
- Periodicamente (recomendado: diário ou semanal)
- Antes de grandes alterações nos dados

### Restaurar backup:

```bash
# Parar a aplicação
# Restaurar o backup
cp instance/cafeteria.db.backup.YYYYMMDD_HHMMSS instance/cafeteria.db
# Reiniciar a aplicação
```
