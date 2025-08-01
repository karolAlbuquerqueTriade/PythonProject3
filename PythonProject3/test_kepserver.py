from opcua import Client, ua
from datetime import datetime
import time

def test_kepserver_connection():
    """Testa a conexão com o KepServer"""
    print("🔍 TESTE DE CONEXÃO COM KEPSERVER")
    print("=" * 50)
    
    try:
        # Tentar conectar ao KepServer
        print("1️⃣ Tentando conectar ao KepServer...")
        client = Client("opc.tcp://127.0.0.1:49320")
        client.connect()
        print("✅ Conectado ao KepServer!")
        
        # Verificar se consegue acessar os nós
        print("\n2️⃣ Verificando estrutura do KepServer...")
        objects_node = client.get_objects_node()
        print(f"✅ Nó Objects acessado: {objects_node}")
        
        # Listar todos os nós filhos
        children = objects_node.get_children()
        print(f"✅ Número de nós filhos: {len(children)}")
        
        # Procurar pelo nó Matics
        print("\n3️⃣ Procurando pelo nó 'Matics'...")
        matics_node = None
        for node in children:
            try:
                display_name = node.get_display_name().Text
                print(f"   Nó encontrado: {display_name}")
                if display_name == "Matics":
                    matics_node = node
                    print(f"✅ Nó 'Matics' encontrado!")
                    break
            except Exception as e:
                print(f"   Erro ao ler nó: {e}")
        
        if not matics_node:
            print("❌ Nó 'Matics' NÃO encontrado!")
            print("   Nós disponíveis:")
            for node in children:
                try:
                    print(f"   - {node.get_display_name().Text}")
                except:
                    print(f"   - {node}")
            return False
        
        # Procurar pelo nó Serac4
        print("\n4️⃣ Procurando pelo nó 'Serac4'...")
        serac4_node = None
        for node in matics_node.get_children():
            try:
                display_name = node.get_display_name().Text
                print(f"   Nó encontrado: {display_name}")
                if display_name == "Serac4":
                    serac4_node = node
                    print(f"✅ Nó 'Serac4' encontrado!")
                    break
            except Exception as e:
                print(f"   Erro ao ler nó: {e}")
        
        if not serac4_node:
            print("❌ Nó 'Serac4' NÃO encontrado!")
            print("   Nós disponíveis em Matics:")
            for node in matics_node.get_children():
                try:
                    print(f"   - {node.get_display_name().Text}")
                except:
                    print(f"   - {node}")
            return False
        
        # Procurar pelo nó Palletizer
        print("\n5️⃣ Procurando pelo nó 'Palletizer'...")
        palletizer_node = None
        for node in serac4_node.get_children():
            try:
                display_name = node.get_display_name().Text
                print(f"   Nó encontrado: {display_name}")
                if display_name == "Palletizer":
                    palletizer_node = node
                    print(f"✅ Nó 'Palletizer' encontrado!")
                    break
            except Exception as e:
                print(f"   Erro ao ler nó: {e}")
        
        if not palletizer_node:
            print("❌ Nó 'Palletizer' NÃO encontrado!")
            print("   Nós disponíveis em Serac4:")
            for node in serac4_node.get_children():
                try:
                    print(f"   - {node.get_display_name().Text}")
                except:
                    print(f"   - {node}")
            return False
        
        # Listar variáveis do Palletizer
        print("\n6️⃣ Listando variáveis do Palletizer...")
        variables = []
        for node in palletizer_node.get_children():
            try:
                if node.get_node_class() == ua.NodeClass.Variable:
                    display_name = node.get_display_name().Text
                    if not display_name.startswith("_"):
                        variables.append(node)
                        print(f"   ✅ Variável: {display_name}")
            except Exception as e:
                print(f"   ❌ Erro ao ler variável: {e}")
        
        print(f"\n📊 Total de variáveis encontradas: {len(variables)}")
        
        if len(variables) == 0:
            print("❌ Nenhuma variável encontrada!")
            return False
        
        # Testar leitura de valores
        print("\n7️⃣ Testando leitura de valores...")
        for i, var in enumerate(variables[:5]):  # Testar apenas as primeiras 5
            try:
                display_name = var.get_display_name().Text
                value = var.get_value()
                quality = var.get_data_value().StatusCode.name
                print(f"   {display_name} = {value} ({quality})")
            except Exception as e:
                print(f"   ❌ Erro ao ler {display_name}: {e}")
        
        # Testar loop de leitura
        print("\n8️⃣ Testando loop de leitura (5 segundos)...")
        start_time = time.time()
        readings = 0
        
        while time.time() - start_time < 5:
            for var in variables[:3]:  # Ler apenas 3 variáveis
                try:
                    display_name = var.get_display_name().Text
                    value = var.get_value()
                    quality = var.get_data_value().StatusCode.name
                    print(f"   {datetime.now().strftime('%H:%M:%S')} - {display_name} = {value}")
                    readings += 1
                except Exception as e:
                    print(f"   ❌ Erro: {e}")
            time.sleep(1)
        
        print(f"\n📈 Total de leituras realizadas: {readings}")
        
        client.disconnect()
        print("\n✅ Teste concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False

def test_alternative_addresses():
    """Testa endereços alternativos do KepServer"""
    print("\n🔍 TESTANDO ENDEREÇOS ALTERNATIVOS")
    print("=" * 50)
    
    addresses = [
        "opc.tcp://127.0.0.1:49320",
        "opc.tcp://localhost:49320",
        "opc.tcp://127.0.0.1:49320",
        "opc.tcp://127.0.0.1:4840",
        "opc.tcp://localhost:4840"
    ]
    
    for addr in addresses:
        print(f"\n🔧 Testando: {addr}")
        try:
            client = Client(addr)
            client.connect()
            print(f"✅ Conectado em: {addr}")
            
            # Testar se consegue acessar os objetos
            objects = client.get_objects_node()
            children = objects.get_children()
            print(f"   Nós disponíveis: {len(children)}")
            
            client.disconnect()
            return addr
            
        except Exception as e:
            print(f"❌ Falhou: {e}")
    
    return None

if __name__ == "__main__":
    print("🧪 TESTE DE CONEXÃO COM KEPSERVER")
    print("=" * 50)
    
    # Testar conexão principal
    success = test_kepserver_connection()
    
    if not success:
        print("\n🔄 Tentando endereços alternativos...")
        working_addr = test_alternative_addresses()
        
        if working_addr:
            print(f"\n✅ Endereço funcionando: {working_addr}")
            print("   Atualize o endereço no Serac4.py")
        else:
            print("\n❌ Nenhum endereço funcionou!")
            print("   Verifique se o KepServer está rodando")
            print("   Verifique se a porta está correta")
            print("   Verifique se o firewall não está bloqueando") 