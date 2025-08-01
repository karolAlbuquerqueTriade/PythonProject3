from opcua import Client, ua
import psycopg2
from datetime import datetime
import time
import sys

def conectar_banco():
    """Conecta ao banco de dados"""
    try:
        conn = psycopg2.connect(
            dbname="new_bd1",
            user="postgres",
            password="postgres",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        
        # Criar tabelas automaticamente
        print("🔧 Criando tabelas...")
        
        # Criar tabela linhas_producao
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS linhas_producao (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) NOT NULL UNIQUE
            )
        """)
        
        # Criar tabela maquinas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS maquinas (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) NOT NULL UNIQUE,
                contador_produtos_ruins INTEGER DEFAULT 0,
                linha_producao_id INTEGER REFERENCES linhas_producao(id)
            )
        """)
        
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
        print("✅ Tabelas criadas/atualizadas com sucesso!")
        
        return conn, cursor
        
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return None, None

def conectar_kepserver():
    """Conecta ao KepServer"""
    try:
        print("🔌 Conectando ao KepServer...")
        client = Client("opc.tcp://192.168.1.50:49320")
        client.connect()
        print("✅ Conectado ao KepServer!")
        return client
    except Exception as e:
        print(f"❌ Erro ao conectar ao KepServer: {e}")
        return None

def navegar_estrutura(client):
    """Navega pela estrutura do KepServer"""
    try:
        print("🗂️ Navegando pela estrutura...")
        
        # Procurar Matics
        matics_node = None
        for node in client.get_objects_node().get_children():
            if node.get_display_name().Text == "Matics":
                matics_node = node
                break
        
        if not matics_node:
            print("❌ Nó 'Matics' não encontrado!")
            return None, None, None
        
        # Procurar Serac4
        serac4_node = None
        for node in matics_node.get_children():
            if node.get_display_name().Text == "Serac4":
                serac4_node = node
                break
        
        if not serac4_node:
            print("❌ Nó 'Serac4' não encontrado!")
            return None, None, None
        
        # Procurar Palletizer
        palletizer_node = None
        for node in serac4_node.get_children():
            if node.get_display_name().Text == "Palletizer":
                palletizer_node = node
                break
        
        if not palletizer_node:
            print("❌ Nó 'Palletizer' não encontrado!")
            return None, None, None
        
        print("✅ Estrutura navegada com sucesso!")
        return matics_node, serac4_node, palletizer_node
        
    except Exception as e:
        print(f"❌ Erro ao navegar pela estrutura: {e}")
        return None, None, None

def fazer_scraping(client, palletizer_node, conn, cursor):
    """Faz o scraping dos dados"""
    try:
        print("🔄 Iniciando scraping...")
        print("   Pressione Ctrl+C para parar")
        print("=" * 50)
        
        leituras = 0
        erros = 0
        
        while True:
            try:
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
                        
                        print(f"✅ {timestamp.strftime('%H:%M:%S')} - {display_name} = {value}")
                        
                    except Exception as e:
                        erros += 1
                        print(f"❌ Erro ao ler/salvar {display_name}: {e}")
                        conn.rollback()
                
                time.sleep(2)  # Pausa de 2 segundos
                
                # Mostrar estatísticas a cada 10 leituras
                if leituras % 10 == 0:
                    print(f"\n📊 Estatísticas: {leituras} leituras, {erros} erros")
                
            except KeyboardInterrupt:
                print("\n👋 Interrompido pelo usuário.")
                break
            except Exception as e:
                erros += 1
                print(f"❌ Erro geral: {e}")
                time.sleep(5)  # Pausa antes de tentar novamente
        
        return leituras, erros
        
    except Exception as e:
        print(f"❌ Erro no scraping: {e}")
        return 0, 0

def main():
    """Função principal"""
    print("🚀 INICIANDO SCRAPING OPC UA")
    print("=" * 50)
    
    # Conectar ao banco
    conn, cursor = conectar_banco()
    if not conn or not cursor:
        print("❌ Falha ao conectar ao banco. Saindo...")
        return
    
    # Conectar ao KepServer
    client = conectar_kepserver()
    if not client:
        print("❌ Falha ao conectar ao KepServer. Saindo...")
        return
    
    try:
        # Navegar pela estrutura
        matics_node, serac4_node, palletizer_node = navegar_estrutura(client)
        if not palletizer_node:
            print("❌ Falha ao navegar pela estrutura. Saindo...")
            return
        
        # Fazer scraping
        leituras, erros = fazer_scraping(client, palletizer_node, conn, cursor)
        
        print(f"\n📈 RESUMO FINAL:")
        print(f"   Leituras realizadas: {leituras}")
        print(f"   Erros encontrados: {erros}")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
    
    finally:
        # Fechar conexões
        try:
            client.disconnect()
            print("✅ Desconectado do KepServer")
        except:
            pass
        
        try:
            cursor.close()
            conn.close()
            print("✅ Desconectado do PostgreSQL")
        except:
            pass
        
        print("👋 Programa finalizado.")

if __name__ == "__main__":
    main() 