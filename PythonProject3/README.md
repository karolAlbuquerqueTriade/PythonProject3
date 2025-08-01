# Projeto OPC UA - Serac4

Este projeto implementa um cliente OPC UA que coleta dados de uma máquina Palletizer na linha de produção Serac4 e armazena os dados em um banco PostgreSQL.

## 📋 Estrutura do Projeto

### Arquivos Principais:
- `Serac4.py` - Script principal que conecta ao OPC UA e salva dados no PostgreSQL
- `database_manager.py` - Gerenciador de banco de dados com interface interativa
- `test_tables.py` - Script de teste para criação das tabelas
- `Serac3.py` - Script adicional (versão anterior)

## 🗄️ Estrutura do Banco de Dados

### Tabela: `linhas_producao`
- `id` (SERIAL PRIMARY KEY) - Identificador único
- `nome` (VARCHAR(100) UNIQUE) - Nome da linha de produção

### Tabela: `maquinas`
- `id` (SERIAL PRIMARY KEY) - Identificador único
- `nome` (VARCHAR(100) UNIQUE) - Nome da máquina
- `contador_produtos_ruins` (INTEGER DEFAULT 0) - Contador de produtos defeituosos
- `linha_producao_id` (INTEGER) - Foreign key para `linhas_producao`

### Tabela: `dados_opcua`
- `id` (SERIAL PRIMARY KEY) - Identificador único
- `timestamp` (TIMESTAMP) - Data e hora da leitura
- `linha` (VARCHAR(100)) - Nome da linha de produção
- `maquina` (VARCHAR(100)) - Nome da máquina
- `funcao` (VARCHAR(100)) - Nome da variável OPC UA
- `dado` (TEXT) - Valor lido
- `qualidade` (VARCHAR(50)) - Status da qualidade do dado

## 🚀 Como Usar

### 1. Configuração Inicial
Certifique-se de que o PostgreSQL está rodando e o banco `new_bd1` existe.

### 2. Criar Tabelas Automaticamente
```bash
python test_tables.py
```

### 3. Usar o Gerenciador de Banco
```bash
python database_manager.py
```

Opções disponíveis:
- **1** - Criar tabelas
- **2** - Inserir dados iniciais
- **3** - Visualizar estrutura das tabelas
- **4** - Mostrar dados atuais
- **5** - Sair

### 4. Executar o Cliente OPC UA
```bash
python Serac4.py
```

## ⚙️ Configurações

### Conexão PostgreSQL:
- **Host:** localhost
- **Porta:** 5432
- **Banco:** new_bd1
- **Usuário:** postgres
- **Senha:** postgres

### Conexão OPC UA:
- **Endereço:** opc.tcp://127.0.0.1:49320
- **Estrutura:** Matics → Serac4 → Palletizer

## 📊 Funcionalidades

### Criação Automática de Tabelas
O script `Serac4.py` cria automaticamente as tabelas necessárias na primeira execução.

### Coleta de Dados
- Conecta ao servidor OPC UA
- Navega pela estrutura: Matics → Serac4 → Palletizer
- Lê todas as variáveis disponíveis
- Salva dados no PostgreSQL a cada 2 segundos

### Tratamento de Erros
- Tratamento de exceções para falhas de conexão
- Rollback automático em caso de erro no banco
- Desconexão segura do OPC UA

## 🔧 Dependências

```bash
pip install opcua psycopg2-binary
```

## 📝 Logs

O sistema exibe mensagens informativas:
- ✅ "Conectado ao OPC UA"
- ✅ "Tabelas criadas/atualizadas com sucesso!"
- ❌ "Erro ao ler/salvar: [detalhes]"
- 👋 "Desconectado do OPC UA e PostgreSQL"

## 🛠️ Troubleshooting

### Erro de Conexão OPC UA
- Verifique se o servidor OPC UA está rodando
- Confirme o endereço e porta corretos
- Verifique se não há firewall bloqueando

### Erro de Banco de Dados
- Verifique se o PostgreSQL está rodando
- Confirme as credenciais de acesso
- Verifique se o banco `new_bd1` existe

### Erro de Dependências
- Instale as dependências: `pip install opcua psycopg2-binary`
- Use Python 3.7+ para compatibilidade 