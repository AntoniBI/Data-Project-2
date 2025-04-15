# import random
# import time
# from datetime import datetime
# from google.cloud.sql.connector import Connector
# import os
# import requests

# DB_CONFIG = {
#     'dbname': 'recursos-emergencia',
#     'user': 'vehiculos',
#     'password': 'admin123',
#     'port': '5432',
# }

# API_URL = 'http://localhost:8082/api/update-location'


# def conectar_db():
#     """Establecer conexión con la base de datos de Cloud SQL"""
#     connector = Connector()
    
#     conn = connector.connect(
#         "splendid-strand-452918-e6:europe-southwest1:recursos",  
#         "pg8000",  
#         user=DB_CONFIG['user'],
#         password=DB_CONFIG['password'],
#         db=DB_CONFIG['dbname'],
#     )
    
#     return conn

# def obtener_recursos_disponibles():
#     """Obtener los recursos disponibles de la base de datos"""
#     conn = conectar_db()
#     cur = conn.cursor()
#     cur.execute("""
#         SELECT recurso_id, servicio FROM recursos WHERE asignado = FALSE
#     """)
#     recursos = cur.fetchall()
#     cur.close()
#     conn.close()
#     return recursos

# def obtener_ubicacion_base(servicio):
#     """Obtener la ubicación base de un servicio desde la base de datos"""
#     conn = conectar_db()
#     cur = conn.cursor()
#     cur.execute("""
#         SELECT latitud, longitud FROM recursos WHERE servicio = %s AND asignado = false LIMIT 1
#     """, (servicio,))
#     resultado = cur.fetchone()
#     cur.close()
#     conn.close()
    
#     if resultado:
#         return resultado[0], resultado[1]  # latitud, longitud
#     else:
#         # Si no se encuentra, devolver una ubicación por defecto
#         return 39.4699, -0.3763

# def generar_nueva_ubicacion(base_lat, base_lon):
#     """Generar una nueva ubicación aleatoria dentro de un rango cercano a la ubicación base"""
#     delta_lat = random.uniform(-0.0005, 0.0005)
#     delta_lon = random.uniform(-0.0005, 0.0005)
#     return round(base_lat + delta_lat, 6), round(base_lon + delta_lon, 6)

# def enviar_a_api(mensaje_dict):
#     """Enviar los datos de ubicación a la API"""
#     try:
#         response = requests.post(API_URL, json=mensaje_dict)
#         response.raise_for_status()
#         print(f"✔️ Enviado a API: {mensaje_dict}")
#     except requests.exceptions.RequestException as e:
#         print(f"❌ Error al enviar a la API: {e}")

# def simular_movimiento(intervalo=5):
#     """Simular el movimiento de los vehículos asignados y actualizar su ubicación cada cierto tiempo"""
#     while True:
#         recursos = obtener_recursos_disponibles()
#         print(f"🔍 Movimiento asignado: {recursos}")
#         for recurso_id, servicio in recursos:
#             # Obtener la ubicación base de la base de datos
#             base_lat, base_lon = obtener_ubicacion_base(servicio)
#             nueva_lat, nueva_lon = generar_nueva_ubicacion(base_lat, base_lon)
#             mensaje = {
#                 'recurso_id': recurso_id,
#                 'servicio': servicio,
#                 'latitud': nueva_lat,
#                 'longitud': nueva_lon,
#                 'timestamp_ubicacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             }
#             enviar_a_api(mensaje)
#         time.sleep(intervalo)

# if __name__ == "__main__":
#     simular_movimiento()





import random
import time
from datetime import datetime
from google.cloud.sql.connector import Connector
import os
import requests

DB_CONFIG = {
    'dbname': 'recursos-emergencia',
    'user': 'vehiculos',
    'password': 'admin123',
    'port': '5432',
}

API_URL = 'http://localhost:8082/api/update-location'


def conectar_db():
    """Establecer conexión con la base de datos de Cloud SQL"""
    connector = Connector()
    
    conn = connector.connect(
        "splendid-strand-452918-e6:europe-southwest1:recursos",  
        "pg8000",  
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        db=DB_CONFIG['dbname'],
    )
    
    return conn

def obtener_recursos_disponibles():
    """Obtener los recursos disponibles de la base de datos"""
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT recurso_id, servicio FROM recursos WHERE asignado = FALSE
    """)
    recursos = cur.fetchall()
    cur.close()
    conn.close()
    return recursos

def obtener_ubicacion_base(servicio):
    """Obtener la ubicación base de un servicio desde la base de datos"""
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT latitud, longitud FROM recursos WHERE servicio = %s AND asignado = false LIMIT 1
    """, (servicio,))
    resultado = cur.fetchone()
    cur.close()
    conn.close()
    
    if resultado:
        return resultado[0], resultado[1]  # latitud, longitud
    else:
        return 39.4699, -0.3763  # ubicación por defecto

def generar_nueva_ubicacion(base_lat, base_lon):
    """Generar una nueva ubicación aleatoria dentro de un rango cercano a la ubicación base"""
    delta_lat = random.uniform(-0.0005, 0.0005)
    delta_lon = random.uniform(-0.0005, 0.0005)
    return round(base_lat + delta_lat, 6), round(base_lon + delta_lon, 6)

def enviar_a_api(mensaje_dict):
    """Enviar los datos de ubicación a la API"""
    try:
        response = requests.post(API_URL, json=mensaje_dict)
        response.raise_for_status()
        print(f"✔️ Enviado a API: {mensaje_dict}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al enviar a la API: {e}")

def simular_movimiento(intervalo=5):
    """Simular el movimiento de los vehículos disponibles y actualizar su ubicación cada X segundos"""
    while True:
        recursos = obtener_recursos_disponibles()
        print(f"🔄 Moviendo {len(recursos)} recursos...")

        mensajes = []
        for recurso_id, servicio in recursos:
            base_lat, base_lon = obtener_ubicacion_base(servicio)
            nueva_lat, nueva_lon = generar_nueva_ubicacion(base_lat, base_lon)
            mensaje = {
                'recurso_id': recurso_id,
                'servicio': servicio,
                'latitud': nueva_lat,
                'longitud': nueva_lon,
                'timestamp_ubicacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            mensajes.append(mensaje)

        # Enviar todos los mensajes seguidos
        for mensaje in mensajes:
            enviar_a_api(mensaje)

        time.sleep(intervalo)

if __name__ == "__main__":
    simular_movimiento()
