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
| **AGORA versionado no Git** (removido do .gitignore após perda de dados de 10/10)
|- Isso permite rollback via Git em caso de problemas
- Única fonte de verdade dos dados
- Ainda recomendado fazer backups locais como segurança adicional

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

## 🚀 Flask-Migrate Implementado (2026-10-10)

### ✅ Sistema de Migrations Ativo
- Flask-Migrate está configurado e funcionando
- Diretório `migrations/` contém o histórico de mudanças
- Use migrations para TODAS as mudanças estruturais no banco

### 📝 Como usar migrations:

**1. Após alterar models:**
```bash
source .venv/bin/activate
flask db migrate -m "Descrição da mudança"
```

**2. Aplicar migration:**
```bash
flask db upgrade
```

**3. Verificar status:**
```bash
flask db current
flask db history
```

**4. Reverter migration (se necessário):**
```bash
flask db downgrade
```

### ✅ NUNCA mais deletar o banco para mudanças estruturais
- Use `flask db migrate` e `flask db upgrade`
- Isso preserva todos os dados existentes
- Se precisar começar do zero, THEN pode deletar o banco

### ⚠️ Regras Atualizadas:
- Ao alterar models: SEMPRE usar migrations
- Backup automático ainda é boa prática antes de migrations complexas
- Commits de migrations devem ir para o Git (versionam o esquema)

## 🚀 Melhorias Futuras

1. ✅ Flask-Migrate ou Alembic para migrations (IMPLEMENTADO)
2. Adicionar script de backup automático
3. Considerar PostgreSQL/MySQL para produção (com backups automáticos)
4. Adicionar sistema de snapshots do banco
