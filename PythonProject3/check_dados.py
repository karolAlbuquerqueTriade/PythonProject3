import psycopg2
from datetime import datetime, timedelta

def verificar_dados_opcua():
    """Verifica os dados na tabela dados_opcua"""
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
        
        print("🔍 VERIFICAÇÃO DOS DADOS OPC UA")
        print("=" * 50)
        
        # 1. Contar total de registros
        cursor.execute("SELECT COUNT(*) FROM dados_opcua")
        total = cursor.fetchone()[0]
        print(f"📊 Total de registros: {total}")
        
        if total == 0:
            print("❌ Nenhum registro encontrado!")
            return
        
        # 2. Ver últimos 10 registros
        cursor.execute("""
            SELECT id, timestamp, linha, maquina, funcao, dado, qualidade 
            FROM dados_opcua 
            ORDER BY timestamp DESC 
            LIMIT 10
        """)
        registros = cursor.fetchall()
        
        print(f"\n📋 Últimos {len(registros)} registros:")
        for reg in registros:
            print(f"  ID: {reg[0]}, {reg[1]} - {reg[2]}/{reg[3]} - {reg[4]} = {reg[5]} ({reg[6]})")
        
        # 3. Verificar se há dados recentes (últimos 5 minutos)
        cursor.execute("""
            SELECT COUNT(*) 
            FROM dados_opcua 
            WHERE timestamp >= NOW() - INTERVAL '5 minutes'
        """)
        recentes = cursor.fetchone()[0]
        print(f"\n⏰ Registros dos últimos 5 minutos: {recentes}")
        
        # 4. Verificar dados por linha
        cursor.execute("""
            SELECT linha, COUNT(*) as total 
            FROM dados_opcua 
            GROUP BY linha
        """)
        linhas = cursor.fetchall()
        print(f"\n🏭 Dados por linha:")
        for linha in linhas:
            print(f"  {linha[0]}: {linha[1]} registros")
        
        # 5. Verificar dados por máquina
        cursor.execute("""
            SELECT maquina, COUNT(*) as total 
            FROM dados_opcua 
            GROUP BY maquina
        """)
        maquinas = cursor.fetchall()
        print(f"\n⚙️ Dados por máquina:")
        for maquina in maquinas:
            print(f"  {maquina[0]}: {maquina[1]} registros")
        
        # 6. Verificar dados por função
        cursor.execute("""
            SELECT funcao, COUNT(*) as total 
            FROM dados_opcua 
            GROUP BY funcao
            ORDER BY total DESC
        """)
        funcoes = cursor.fetchall()
        print(f"\n🔧 Dados por função:")
        for funcao in funcoes:
            print(f"  {funcao[0]}: {funcao[1]} registros")
        
        # 7. Verificar qualidade dos dados
        cursor.execute("""
            SELECT qualidade, COUNT(*) as total 
            FROM dados_opcua 
            GROUP BY qualidade
        """)
        qualidades = cursor.fetchall()
        print(f"\n📈 Qualidade dos dados:")
        for qualidade in qualidades:
            print(f"  {qualidade[0]}: {qualidade[1]} registros")
        
        # 8. Verificar se há dados duplicados
        cursor.execute("""
            SELECT timestamp, linha, maquina, funcao, COUNT(*) as total
            FROM dados_opcua 
            GROUP BY timestamp, linha, maquina, funcao
            HAVING COUNT(*) > 1
            ORDER BY total DESC
            LIMIT 5
        """)
        duplicados = cursor.fetchall()
        print(f"\n🔄 Possíveis duplicados:")
        for dup in duplicados:
            print(f"  {dup[0]} - {dup[1]}/{dup[2]} - {dup[3]}: {dup[4]} vezes")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

def testar_scraping_manual():
    """Testa o scraping manual para verificar se está funcionando"""
    try:
        from opcua import Client, ua
        
        print("\n🧪 TESTE DE SCRAPING MANUAL")
        print("=" * 50)
        
        # Conectar ao KepServer
        client = Client("opc.tcp://127.0.0.1:49320")
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
        
        # Ler variáveis
        print("\n📊 Lendo variáveis do Palletizer:")
        for node in palletizer_node.get_children():
            try:
                if node.get_node_class() == ua.NodeClass.Variable:
                    display_name = node.get_display_name().Text
                    if not display_name.startswith("_"):
                        value = node.get_value()
                        quality = node.get_data_value().StatusCode.name
                        print(f"  {display_name} = {value} ({quality})")
            except Exception as e:
                print(f"  ❌ Erro ao ler variável: {e}")
        
        client.disconnect()
        
    except Exception as e:
        print(f"❌ Erro no teste manual: {e}")

if __name__ == "__main__":
    verificar_dados_opcua()
    testar_scraping_manual() 