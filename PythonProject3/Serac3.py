from opcua import Client, ua
import psycopg2
from datetime import datetime
import time

conn = psycopg2.connect(
    dbname="new_bd",
    user="postgres",
    password=" ",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

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
        if node.get_display_name().Text == "Serac3":
            linha_node = node
            break

    maquina_node = None
    for node in linha_node.get_children():
        if node.get_display_name().Text == "Palletizer":
            maquina_node = node
            break

    linha_name = "Serac3"
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
