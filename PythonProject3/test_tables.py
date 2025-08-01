import psycopg2
from datetime import datetime

def test_criar_tabelas():
    """Testa a criação das tabelas"""
    try:
        # Conectar ao banco
        conn = psycopg2.connect(
            dbname="new_bd1",
            user="postgres",
            password="postgres",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        
        print("🔧 Criando tabelas automaticamente...")
        
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
        
        # Inserir dados iniciais
        cursor.execute("""
            INSERT INTO linhas_producao (nome) 
            VALUES ('Serac4') 
            ON CONFLICT (nome) DO NOTHING
        """)
        
        cursor.execute("SELECT id FROM linhas_producao WHERE nome = 'Serac4'")
        linha_id = cursor.fetchone()[0]
        
        cursor.execute("""
            INSERT INTO maquinas (nome, linha_producao_id) 
            VALUES ('Palletizer', %s) 
            ON CONFLICT (nome) DO NOTHING
        """, (linha_id,))
        
        conn.commit()
        print("🎉 Todas as tabelas foram criadas e dados iniciais inseridos!")
        
        # Verificar se as tabelas foram criadas
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('linhas_producao', 'maquinas', 'dados_opcua')
        """)
        
        tabelas = cursor.fetchall()
        print(f"\n📋 Tabelas criadas: {len(tabelas)}")
        for tabela in tabelas:
            print(f"  - {tabela[0]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_criar_tabelas() 