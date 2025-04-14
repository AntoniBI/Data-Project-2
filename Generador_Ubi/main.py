import random
import time
import psycopg2
import requests
import json

# Configuración de conexión a Cloud SQL
DB_CONFIG = {
    'dbname': 'recursos-emergencia',
    'user': 'vehiculos',
    'password': 'admin123',
    'host': '34.123.45.67',
    'port': '5432',
}

# Configuración del endpoint de la API
API_URL = 'http://localhost:8082/api/update-location'  # Asegúrate de ajustar si la API está en otro host o puerto

# Ubicación base por tipo de recurso
UBICACIONES_BASE = {
    'Policía': (39.4699, -0.3763),
    'Bomberos': (39.4801, -0.3702),
    'Ambulancia': (39.4602, -0.3681),
}

def conectar_db():
    return psycopg2.connect(**DB_CONFIG)

def obtener_recursos_disponibles():
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, tipo FROM recursos WHERE asignado = true
    """)
    recursos = cur.fetchall()
    cur.close()
    conn.close()
    return recursos

def generar_nueva_ubicacion(base_lat, base_lon):
    delta_lat = random.uniform(-0.0005, 0.0005)
    delta_lon = random.uniform(-0.0005, 0.0005)
    return round(base_lat + delta_lat, 6), round(base_lon + delta_lon, 6)

def enviar_a_api(mensaje_dict):
    try:
        response = requests.post(API_URL, json=mensaje_dict)
        response.raise_for_status()
        print(f"✔️ Enviado a API: {mensaje_dict}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al enviar a la API: {e}")

def simular_movimiento(intervalo=5):
    while True:
        recursos = obtener_recursos_disponibles()
        for recurso_id, tipo in recursos:
            base_lat, base_lon = UBICACIONES_BASE.get(tipo, (39.4699, -0.3763))
            nueva_lat, nueva_lon = generar_nueva_ubicacion(base_lat, base_lon)
            mensaje = {
                'recurso_id': recurso_id,
                'tipo': tipo,
                'latitud': nueva_lat,
                'longitud': nueva_lon,
                'timestamp': time.time(),
            }
            enviar_a_api(mensaje)
        time.sleep(intervalo)

if __name__ == "__main__":
    simular_movimiento()
