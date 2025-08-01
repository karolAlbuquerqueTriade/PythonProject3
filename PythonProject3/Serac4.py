from opcua import Client, ua
import psycopg2
from datetime import datetime
import time

conn = psycopg2.connect(
    dbname="new_bd1",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# Criar tabelas automaticamente
try:
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
    
    # Inserir linha de produção Serac4 se não existir
    cursor.execute("""
        INSERT INTO linhas_producao (nome) 
        VALUES ('Serac4') 
        ON CONFLICT (nome) DO NOTHING
    """)
    
    # Buscar o ID da linha Serac4
    cursor.execute("SELECT id FROM linhas_producao WHERE nome = 'Serac4'")
    linha_id = cursor.fetchone()[0]
    
    # Inserir máquina Palletizer se não existir
    cursor.execute("""
        INSERT INTO maquinas (nome, linha_producao_id) 
        VALUES ('Palletizer', %s) 
        ON CONFLICT (nome) DO NOTHING
    """, (linha_id,))
    
    conn.commit()
    print("Tabelas criadas/atualizadas com sucesso!")
    
except Exception as e:
    print(f"Erro ao criar tabelas: {e}")
    conn.rollback()

client = Client("opc.tcp://192.168.1.50:49320")

try:
    client.connect()
    print("Conectado ao OPC UA")

    matics_node = None
    for node in client.get_objects_node().get_children():
        if node.get_display_name().Text == "Matics":
            matics_node = node
            break

    linha_node = None
    for node in matics_node.get_children():
        if node.get_display_name().Text == "Serac4":
            linha_node = node
            break

    maquina_node = None
    for node in linha_node.get_children():
        if node.get_display_name().Text == "Palletizer":
            maquina_node = node
            break

    linha_name = "Serac4"
    maquina_name = "Palletizer"

    while True:
        for var_node in maquina_node.get_children():
            try:
                if var_node.get_node_class() != ua.NodeClass.Variable:
                    continue

                funcao = var_node.get_display_name().Text
                if funcao.startswith("_"):
                    continue

                valor = str(var_node.get_value())
                qualidade = var_node.get_data_value().StatusCode.name
                timestamp = datetime.now()

                cursor.execute("""
                    INSERT INTO dados_opcua (timestamp, linha, maquina, funcao, dado, qualidade)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (timestamp, linha_name, maquina_name, funcao, valor, qualidade))
                conn.commit()

            except Exception as e:
                print(f"Erro ao ler/salvar: {e}")
                conn.rollback()
        time.sleep(2)

except KeyboardInterrupt:
    print("Interrompido pelo usuário.")

finally:
    client.disconnect()
    cursor.close()
    conn.close()
    print("Desconectado do OPC UA e PostgreSQL.")
