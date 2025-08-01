import psycopg2
from datetime import datetime

def conectar_banco():
    """Conecta ao banco de dados PostgreSQL"""
    return psycopg2.connect(
        dbname="new_bd1",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432"
    )

def criar_tabelas():
    """Cria todas as tabelas necessárias"""
    conn = conectar_banco()
    cursor = conn.cursor()
    
    try:
        # Criar tabela linhas_producao
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS linhas_producao (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) NOT NULL UNIQUE
            )
        """)
        print("✓ Tabela 'linhas_producao' criada/verificada")
        
        # Criar tabela maquinas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS maquinas (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) NOT NULL UNIQUE,
                contador_produtos_ruins INTEGER DEFAULT 0,
                linha_producao_id INTEGER REFERENCES linhas_producao(id)
            )
        """)
        print("✓ Tabela 'maquinas' criada/verificada")
        
        # Criar tabela dados_opcua
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dados_opcua (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL,
                linha VARCHAR(100) NOT NULL,
                maquina VARCHAR(100) NOT NULL,
                funcao VARCHAR(100) NOT NULL,
                dado TEXT NOT NULL,
                qualidade VARCHAR(50) NOT NULL
            )
        """)
        print("✓ Tabela 'dados_opcua' criada/verificada")
        
        conn.commit()
        print("\n🎉 Todas as tabelas foram criadas com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def inserir_dados_iniciais():
    """Insere dados iniciais nas tabelas"""
    conn = conectar_banco()
    cursor = conn.cursor()
    
    try:
        # Inserir linha de produção Serac4
        cursor.execute("""
            INSERT INTO linhas_producao (nome) 
            VALUES ('Serac4') 
            ON CONFLICT (nome) DO NOTHING
        """)
        
        # Buscar o ID da linha Serac4
        cursor.execute("SELECT id FROM linhas_producao WHERE nome = 'Serac4'")
        linha_id = cursor.fetchone()[0]
        
        # Inserir máquina Palletizer
        cursor.execute("""
            INSERT INTO maquinas (nome, linha_producao_id) 
            VALUES ('Palletizer', %s) 
            ON CONFLICT (nome) DO NOTHING
        """, (linha_id,))
        
        conn.commit()
        print("✓ Dados iniciais inseridos com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao inserir dados iniciais: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def visualizar_estrutura():
    """Mostra a estrutura das tabelas"""
    conn = conectar_banco()
    cursor = conn.cursor()
    
    try:
        print("\n📊 ESTRUTURA DAS TABELAS:")
        print("=" * 50)
        
        # Mostrar estrutura da tabela linhas_producao
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'linhas_producao'
            ORDER BY ordinal_position
        """)
        
        print("\n📋 TABELA: linhas_producao")
        print("-" * 30)
        for col in cursor.fetchall():
            print(f"  {col[0]}: {col[1]} {'(NULL)' if col[2] == 'YES' else '(NOT NULL)'}")
        
        # Mostrar estrutura da tabela maquinas
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'maquinas'
            ORDER BY ordinal_position
        """)
        
        print("\n📋 TABELA: maquinas")
        print("-" * 30)
        for col in cursor.fetchall():
            print(f"  {col[0]}: {col[1]} {'(NULL)' if col[2] == 'YES' else '(NOT NULL)'}")
        
        # Mostrar estrutura da tabela dados_opcua
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'dados_opcua'
            ORDER BY ordinal_position
        """)
        
        print("\n📋 TABELA: dados_opcua")
        print("-" * 30)
        for col in cursor.fetchall():
            print(f"  {col[0]}: {col[1]} {'(NULL)' if col[2] == 'YES' else '(NOT NULL)'}")
        
    except Exception as e:
        print(f"❌ Erro ao visualizar estrutura: {e}")
    finally:
        cursor.close()
        conn.close()

def mostrar_dados():
    """Mostra os dados atuais nas tabelas"""
    conn = conectar_banco()
    cursor = conn.cursor()
    
    try:
        print("\n📈 DADOS ATUAIS:")
        print("=" * 50)
        
        # Mostrar linhas de produção
        cursor.execute("SELECT * FROM linhas_producao")
        linhas = cursor.fetchall()
        print(f"\n🏭 Linhas de Produção ({len(linhas)} registros):")
        for linha in linhas:
            print(f"  ID: {linha[0]}, Nome: {linha[1]}")
        
        # Mostrar máquinas
        cursor.execute("""
            SELECT m.id, m.nome, m.contador_produtos_ruins, l.nome as linha
            FROM maquinas m
            JOIN linhas_producao l ON m.linha_producao_id = l.id
        """)
        maquinas = cursor.fetchall()
        print(f"\n⚙️ Máquinas ({len(maquinas)} registros):")
        for maquina in maquinas:
            print(f"  ID: {maquina[0]}, Nome: {maquina[1]}, Produtos Ruins: {maquina[2]}, Linha: {maquina[3]}")
        
        # Mostrar dados OPC UA
        cursor.execute("SELECT COUNT(*) FROM dados_opcua")
        count = cursor.fetchone()[0]
        print(f"\n📊 Dados OPC UA: {count} registros")
        
        if count > 0:
            cursor.execute("SELECT * FROM dados_opcua ORDER BY timestamp DESC LIMIT 5")
            dados = cursor.fetchall()
            print("Últimos 5 registros:")
            for dado in dados:
                print(f"  {dado[1]}: {dado[2]}/{dado[3]} - {dado[4]} = {dado[5]} ({dado[6]})")
        
    except Exception as e:
        print(f"❌ Erro ao mostrar dados: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("🔧 GERENCIADOR DE BANCO DE DADOS")
    print("=" * 40)
    
    while True:
        print("\nEscolha uma opção:")
        print("1. Criar tabelas")
        print("2. Inserir dados iniciais")
        print("3. Visualizar estrutura")
        print("4. Mostrar dados")
        print("5. Sair")
        
        opcao = input("\nOpção: ").strip()
        
        if opcao == "1":
            criar_tabelas()
        elif opcao == "2":
            inserir_dados_iniciais()
        elif opcao == "3":
            visualizar_estrutura()
        elif opcao == "4":
            mostrar_dados()
        elif opcao == "5":
            print("👋 Saindo...")
            break
        else:
            print("❌ Opção inválida!") 