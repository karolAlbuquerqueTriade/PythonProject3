import psycopg2
from datetime import datetime

def test_insert():
    """Testa a inserção de dados na tabela dados_opcua"""
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
        
        print("🔧 Testando inserção de dados...")
        
        # Dados de teste
        timestamp = datetime.now()
        linha = "Serac4"
        maquina = "Palletizer"
        funcao = "Teste_Variavel"
        dado = "123.45"
        qualidade = "Good"
        
        # Testar inserção
        cursor.execute("""
            INSERT INTO dados_opcua (timestamp, linha, maquina, funcao, dado, qualidade)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (timestamp, linha, maquina, funcao, dado, qualidade))
        
        conn.commit()
        print("✅ Inserção realizada com sucesso!")
        
        # Verificar se foi inserido
        cursor.execute("SELECT * FROM dados_opcua ORDER BY timestamp DESC LIMIT 1")
        resultado = cursor.fetchone()
        
        if resultado:
            print(f"📊 Último registro inserido:")
            print(f"  ID: {resultado[0]}")
            print(f"  Timestamp: {resultado[1]}")
            print(f"  Linha: {resultado[2]}")
            print(f"  Máquina: {resultado[3]}")
            print(f"  Função: {resultado[4]}")
            print(f"  Dado: {resultado[5]}")
            print(f"  Qualidade: {resultado[6]}")
        
        # Contar total de registros
        cursor.execute("SELECT COUNT(*) FROM dados_opcua")
        total = cursor.fetchone()[0]
        print(f"\n📈 Total de registros na tabela: {total}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

def test_select():
    """Testa consultas SELECT na tabela dados_opcua"""
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
        
        print("\n🔍 Testando consultas SELECT...")
        
        # Teste 1: Contar registros
        cursor.execute("SELECT COUNT(*) FROM dados_opcua")
        count = cursor.fetchone()[0]
        print(f"✅ Total de registros: {count}")
        
        # Teste 2: Últimos 5 registros
        cursor.execute("""
            SELECT id, timestamp, linha, maquina, funcao, dado, qualidade 
            FROM dados_opcua 
            ORDER BY timestamp DESC 
            LIMIT 5
        """)
        registros = cursor.fetchall()
        print(f"✅ Últimos {len(registros)} registros:")
        for reg in registros:
            print(f"  {reg[1]}: {reg[2]}/{reg[3]} - {reg[4]} = {reg[5]} ({reg[6]})")
        
        # Teste 3: Filtrar por linha
        cursor.execute("""
            SELECT COUNT(*) 
            FROM dados_opcua 
            WHERE linha = 'Serac4'
        """)
        count_serac4 = cursor.fetchone()[0]
        print(f"✅ Registros da linha Serac4: {count_serac4}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro na consulta: {e}")
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🧪 TESTE DE INSERÇÃO E CONSULTA")
    print("=" * 40)
    
    test_insert()
    test_select() 