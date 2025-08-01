import psycopg2
import time
from datetime import datetime

def monitor_dados():
    """Monitora se novos dados estão sendo inseridos"""
    try:
        print("📊 MONITOR DE DADOS OPC UA")
        print("=" * 50)
        
        conn = psycopg2.connect(
            dbname="new_bd1",
            user="postgres",
            password="postgres",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        
        # Contar registros iniciais
        cursor.execute("SELECT COUNT(*) FROM dados_opcua")
        total_inicial = cursor.fetchone()[0]
        print(f"📊 Total inicial: {total_inicial} registros")
        
        print("\n🔄 Monitorando novos dados... (Pressione Ctrl+C para parar)")
        print("=" * 50)
        
        while True:
            # Contar registros atuais
            cursor.execute("SELECT COUNT(*) FROM dados_opcua")
            total_atual = cursor.fetchone()[0]
            
            # Verificar novos registros
            novos = total_atual - total_inicial
            
            if novos > 0:
                print(f"✅ {datetime.now().strftime('%H:%M:%S')} - Novos registros: +{novos} (Total: {total_atual})")
                
                # Mostrar último registro
                cursor.execute("""
                    SELECT timestamp, linha, maquina, funcao, dado, qualidade 
                    FROM dados_opcua 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                """)
                ultimo = cursor.fetchone()
                if ultimo:
                    print(f"   📋 Último: {ultimo[0]} - {ultimo[1]}/{ultimo[2]} - {ultimo[3]} = {ultimo[4]} ({ultimo[5]})")
                
                total_inicial = total_atual
            else:
                print(f"⏳ {datetime.now().strftime('%H:%M:%S')} - Aguardando novos dados...")
            
            time.sleep(5)  # Verificar a cada 5 segundos
            
    except KeyboardInterrupt:
        print("\n👋 Monitoramento interrompido pelo usuário.")
    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    monitor_dados() 