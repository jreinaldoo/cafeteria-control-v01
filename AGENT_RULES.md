# Regras Estruturais de Segurança - Agent AI

## 🚨 Regras Críticas de Banco de Dados

### ❌ NUNCA fazer sem confirmação explícita do usuário:

1. **Deletar o banco de dados**
   - Antes de executar `rm instance/cafeteria.db` ou similar, SEMPRE perguntar ao usuário
   - Verificar se há dados importantes
   - Oferecer opção de backup antes de deletar

2. **Alterar estrutura do banco (models)**
   - Adicionar/remover colunas em models
   - Alterar tipos de dados em colunas
   - Renomear tabelas
   - Adicionar novos models que requerem migration
   - **AÇÃO**: Perguntar ao usuário: "Esta mudança vai alterar a estrutura do banco de dados. Deseja que eu faça backup antes? (sim/não)"

3. **Executar migrations que podem causar perda de dados**
   - ALTER TABLE com DROP COLUMN
   - Operações DDL destrutivas
   - **AÇÃO**: Perguntar ao usuário e fazer backup automático

### ✅ SEMPRE fazer antes de mudanças estruturais:

1. **Backup do banco de dados**
   ```bash
   cp instance/cafeteria.db instance/cafeteria.db.backup.$(date +%Y%m%d_%H%M%S)
   ```

2. **Verificar com o usuário**
   - "Esta mudança vai alterar a estrutura do banco. Você tem backup dos dados? Deseja prosseguir?"

3. **Usar migrations quando possível**
   - Em vez de deletar e recriar o banco, usar migrations do Flask-Migrate ou Alembic
   - Isso preserva os dados existentes

## 📋 Regras para Mudanças de Código

### ✅ Pode fazer sem perguntar:
- Adicionar novas rotas
- Modificar templates HTML
- Adicionar/alterar CSS
- Adicionar novos services
- Modificar lógica de negócio que não afeta o banco
- Adicionar/alterar validações

### ⚠️ Deve perguntar antes:
- Alterar models do SQLAlchemy
- Adicionar/remover colunas em models
- Mudar tipos de dados de colunas
- Alterar relações entre models
- Deletar arquivos importantes sem confirmação

## 🔍 Checklist Antes de Operações Críticas

Antes de executar qualquer comando que possa causar perda de dados:

1. [ ] O banco de dados tem backup recente?
2. [ ] O usuário foi informado da mudança?
3. [ ] O usuário confirmou explicitamente?
4. [ ] Existe alternativa menos destrutiva?
5. [ ] Os dados podem ser recuperados se algo der errado?

## 🎯 Regras Específicas do Projeto

### Banco de Dados SQLite:
- Localização: `instance/cafeteria.db`
- NÃO versionado no Git (está no .gitignore)
- Única fonte de verdade dos dados
- Perda = dados irrecuperáveis sem backup

### Produtos e Vendas:
- Produtos têm estoque que é alterado automaticamente
- Vendas baixam estoque
- Compras aumentam estoque e recalculam custo médio
- Estes dados são críticos para o funcionamento do sistema

## 📝 Lições Aprendidas

### Erro Cometido (2026-10-06):
- Deletado banco de dados sem fazer backup
- Sempre deletar `instance/cafeteria.db` para recriar banco
- Usuário perdeu todos os dados (vendas, compras, estoque)

### Correção:
- Adicionar documentação de backup no README
- Criar estas regras estruturais
- Nunca mais deletar banco sem confirmação explícita
- Usar migrations ao invés de deletar/recriar

## 🚀 Melhorias Futuras

1. Implementar Flask-Migrate ou Alembic para migrations
2. Adicionar script de backup automático
3. Considerar PostgreSQL/MySQL para produção (com backups automáticos)
4. Adicionar sistema de snapshots do banco
