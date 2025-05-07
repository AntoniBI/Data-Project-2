
import random
import time
from datetime import datetime
import requests

API_URL = "https://str-service-puifiielba-no.a.run.app"

def generar_nueva_ubicacion(base_lat, base_lon):
    """Generar una nueva ubicación aleatoria dentro de un rango cercano a la ubicación base"""
    delta_lat = random.uniform(-0.0005, 0.0005)
    delta_lon = random.uniform(-0.0005, 0.0005)
    return round(base_lat + delta_lat, 6), round(base_lon + delta_lon, 6)

def obtener_recursos_asignados():
    """Consultar la API para obtener recursos actualmente asignados"""
    try:
        response = requests.get(f"{API_URL}/api/recursos-asignados")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al consultar recursos asignados: {e}")
        return []

def enviar_a_api(mensaje_dict):
    """Enviar los datos de ubicación a la API"""
    try:
        response = requests.post(f"{API_URL}/api/update-location", json=mensaje_dict)
        response.raise_for_status()
        print(f"✔️ Enviado a API: {mensaje_dict}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al enviar a la API: {e}")

def simular_movimiento(intervalo=1):
    """Simular el movimiento de los recursos asignados y enviar sus nuevas ubicaciones"""
    while True:
        recursos = obtener_recursos_asignados()
        print(f"🔄 Moviendo {len(recursos)} recursos...")

        for recurso in recursos:
            nueva_lat, nueva_lon = generar_nueva_ubicacion(recurso["latitud"], recurso["longitud"])
            mensaje = {
                "recurso_id": recurso["recurso_id"],
                "servicio": recurso["servicio"],
                "latitud": nueva_lat,
                "longitud": nueva_lon,
                "timestamp_ubicacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            enviar_a_api(mensaje)

        time.sleep(intervalo)

if __name__ == "__main__":
    simular_movimiento()
