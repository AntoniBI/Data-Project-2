import random
import time
from datetime import datetime
from google.cloud.sql.connector import Connector
from google.auth.transport.requests import Request
import os
import requests

DB_CONFIG = {
    'dbname': 'recursos-emergencia',
    'user': 'vehiculos',
    'password': 'admin123',
    'port': '5432',
}

API_URL = 'http://localhost:8082/api/update-location'

UBICACIONES_BASE = {
    'Policia': (39.4699, -0.3763),
    'Bombero': (39.4801, -0.3702),
    'Ambulancia': (39.4602, -0.3681),
}


def conectar_db():
   
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
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT recurso_id, servicio FROM recursos WHERE asignado = false
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
        print(f"🔍 Movimiento asignado: {recursos}")
        for recurso_id, servicio in recursos:
            base_lat, base_lon = UBICACIONES_BASE.get(servicio, (39.4699, -0.3763))
            nueva_lat, nueva_lon = generar_nueva_ubicacion(base_lat, base_lon)
            mensaje = {
                'recurso_id': recurso_id,
                'servicio': servicio,
                'latitud': nueva_lat,
                'longitud': nueva_lon,
                'timestamp_ubicacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            enviar_a_api(mensaje)
        time.sleep(intervalo)

if __name__ == "__main__":
    simular_movimiento()
