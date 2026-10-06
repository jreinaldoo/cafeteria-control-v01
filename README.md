# Cafeteria Control — V0.1

Aplicação local para controle de produtos, custos, vendas, compras e estoque de uma cafeteria.

## Stack

- Python 3.11+
- Flask
- Flask-SQLAlchemy
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
