# 📊 Guia de Consultas PostgreSQL

## ✅ Consultas Corretas para PostgreSQL

### 1. **Contar total de registros**
```sql
SELECT COUNT(*) FROM dados_opcua;
```

### 2. **Ver todos os registros**
```sql
SELECT * FROM dados_opcua ORDER BY timestamp DESC;
```

### 3. **Ver últimos 10 registros**
```sql
SELECT * FROM dados_opcua ORDER BY timestamp DESC LIMIT 10;
```

### 4. **Filtrar por linha de produção**
```sql
SELECT * FROM dados_opcua WHERE linha = 'Serac4';
```

### 5. **Filtrar por máquina**
```sql
SELECT * FROM dados_opcua WHERE maquina = 'Palletizer';
```

### 6. **Filtrar por função/variável**
```sql
SELECT * FROM dados_opcua WHERE funcao = 'NomeDaVariavel';
```

### 7. **Filtrar por data/hora**
```sql
SELECT * FROM dados_opcua 
WHERE timestamp >= '2025-08-01 00:00:00' 
AND timestamp <= '2025-08-01 23:59:59';
```

### 8. **Agrupar por linha e contar**
```sql
SELECT linha, COUNT(*) as total_registros 
FROM dados_opcua 
GROUP BY linha;
```

### 9. **Agrupar por máquina e contar**
```sql
SELECT maquina, COUNT(*) as total_registros 
FROM dados_opcua 
GROUP BY maquina;
```

### 10. **Ver dados de hoje**
```sql
SELECT * FROM dados_opcua 
WHERE DATE(timestamp) = CURRENT_DATE;
```

### 11. **Ver dados da última hora**
```sql
SELECT * FROM dados_opcua 
WHERE timestamp >= NOW() - INTERVAL '1 hour';
```

### 12. **Ver dados da última hora da linha Serac4**
```sql
SELECT * FROM dados_opcua 
WHERE linha = 'Serac4' 
AND timestamp >= NOW() - INTERVAL '1 hour';
```

### 13. **Contar registros por qualidade**
```sql
SELECT qualidade, COUNT(*) as total 
FROM dados_opcua 
GROUP BY qualidade;
```

### 14. **Ver estrutura da tabela**
```sql
\d dados_opcua
```

### 15. **Ver todas as tabelas**
```sql
\dt
```

## ❌ **Consultas INCORRETAS (que causam erro)**

### ❌ Errado - usar `?` como placeholder
```sql
INSERT INTO dados_opcua VALUES (?, ?, ?, ?, ?, ?, ?);
```

### ❌ Errado - usar aspas simples em nomes de colunas
```sql
SELECT 'timestamp', 'linha' FROM dados_opcua;
```

### ❌ Errado - usar `LIMIT` sem `ORDER BY`
```sql
SELECT * FROM dados_opcua LIMIT 10;
```

## 🔧 **Comandos úteis do PostgreSQL**

### Conectar ao banco
```bash
psql -h localhost -U postgres -d new_bd1
```

### Verificar conexão
```sql
SELECT version();
```

### Verificar tabelas
```sql
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';
```

### Verificar estrutura de uma tabela
```sql
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'dados_opcua';
```

## 📝 **Exemplos de Consultas Avançadas**

### 1. **Dados das últimas 24 horas agrupados por hora**
```sql
SELECT 
    DATE_TRUNC('hour', timestamp) as hora,
    COUNT(*) as total_registros
FROM dados_opcua 
WHERE timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY DATE_TRUNC('hour', timestamp)
ORDER BY hora DESC;
```

### 2. **Top 5 funções mais frequentes**
```sql
SELECT 
    funcao, 
    COUNT(*) as total
FROM dados_opcua 
GROUP BY funcao 
ORDER BY total DESC 
LIMIT 5;
```

### 3. **Dados com qualidade diferente de 'Good'**
```sql
SELECT * FROM dados_opcua 
WHERE qualidade != 'Good';
```

### 4. **Último valor de cada função**
```sql
SELECT DISTINCT ON (funcao) 
    funcao, 
    dado, 
    timestamp
FROM dados_opcua 
ORDER BY funcao, timestamp DESC;
```

## 🚨 **Solução para o erro que você encontrou**

O erro `erro de sintaxe em ou próximo a ","` acontece quando você usa `?` como placeholder. No PostgreSQL, use `%s`:

### ✅ Correto
```sql
-- No Python com psycopg2
cursor.execute("""
    INSERT INTO dados_opcua (timestamp, linha, maquina, funcao, dado, qualidade)
    VALUES (%s, %s, %s, %s, %s, %s)
""", (timestamp, linha, maquina, funcao, valor, qualidade))
```

### ❌ Incorreto
```sql
-- Isso causa erro no PostgreSQL
INSERT INTO dados_opcua VALUES (?, ?, ?, ?, ?, ?, ?);
``` 