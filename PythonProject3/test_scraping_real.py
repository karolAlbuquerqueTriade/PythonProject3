from opcua import Client, ua
import psycopg2
from datetime import datetime
import time

def test_scraping_real():
    """Testa o scraping real e salva dados no banco"""
    try:
        print("🧪 TESTE DE SCRAPING REAL")
        print("=" * 50)
        
        # Conectar ao banco
        conn = psycopg2.connect(
            dbname="new_bd1",
            user="postgres",
            password="postgres",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        
        # Conectar ao KepServer
        client = Client("opc.tcp://192.168.1.50:49320")
        client.connect()
        print("✅ Conectado ao KepServer")
        
        # Navegar pela estrutura
        matics_node = None
        for node in client.get_objects_node().get_children():
            if node.get_display_name().Text == "Matics":
                matics_node = node
                break
        
        serac4_node = None
        for node in matics_node.get_children():
            if node.get_display_name().Text == "Serac4":
                serac4_node = node
                break
        
        palletizer_node = None
        for node in serac4_node.get_children():
            if node.get_display_name().Text == "Palletizer":
                palletizer_node = node
                break
        
        print("✅ Estrutura navegada com sucesso")
        
        # Contar registros antes
        cursor.execute("SELECT COUNT(*) FROM dados_opcua")
        antes = cursor.fetchone()[0]
        print(f"📊 Registros antes: {antes}")
        
        # Fazer scraping por 10 segundos
        print("\n🔄 Iniciando scraping por 10 segundos...")
        start_time = time.time()
        leituras = 0
        
        while time.time() - start_time < 10:
            for node in palletizer_node.get_children():
                try:
                    if node.get_node_class() != ua.NodeClass.Variable:
                        continue
                    
                    display_name = node.get_display_name().Text
                    if display_name.startswith("_"):
                        continue
                    
                    value = str(node.get_value())
                    quality = node.get_data_value().StatusCode.name
                    timestamp = datetime.now()
                    
                    # Salvar no banco
                    cursor.execute("""
                        INSERT INTO dados_opcua (timestamp, linha, maquina, funcao, dado, qualidade)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (timestamp, "Serac4", "Palletizer", display_name, value, quality))
                    
                    conn.commit()
                    leituras += 1
                    print(f"  {timestamp.strftime('%H:%M:%S')} - {display_name} = {value}")
                    
                except Exception as e:
                    print(f"  ❌ Erro ao ler/salvar {display_name}: {e}")
                    conn.rollback()
            
            time.sleep(2)  # Pausa de 2 segundos
        
        # Contar registros depois
        cursor.execute("SELECT COUNT(*) FROM dados_opcua")
        depois = cursor.fetchone()[0]
        print(f"\n📊 Registros depois: {depois}")
        print(f"📈 Novos registros inseridos: {depois - antes}")
        print(f"🔄 Total de leituras realizadas: {leituras}")
        
        # Verificar últimos registros
        cursor.execute("""
            SELECT id, timestamp, linha, maquina, funcao, dado, qualidade 
            FROM dados_opcua 
            ORDER BY timestamp DESC 
            LIMIT 5
        """)
        registros = cursor.fetchall()
        
        print(f"\n📋 Últimos {len(registros)} registros:")
        for reg in registros:
            print(f"  ID: {reg[0]}, {reg[1]} - {reg[2]}/{reg[3]} - {reg[4]} = {reg[5]} ({reg[6]})")
        
        client.disconnect()
        cursor.close()
        conn.close()
        
        print("\n✅ Teste concluído!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_scraping_real() 