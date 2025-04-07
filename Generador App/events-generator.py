import requests
import json
import time
import random
from datetime import datetime

API_URL = "http://127.0.0.1:8080/api/request-help"
# Si desplegaste tu API en Cloud Run, usa esa URL pública:
# API_URL = "https://tu-api-en-cloud-run-url.a.run.app/api/request-help"

# Intervalo (en segundos) entre envío de eventos (aleatorio para simular mejor)
tiempo_minimo = 3
tiempo_maximo = 10

# Datos base
servicios = ["Bombero", "Policía", "Ambulancia"]

emergencia_ambulancia = [
    "Paro cardíaco",
    "Accidente de tráfico con heridos",
    "Persona inconsciente",
    "Dificultad respiratoria",
    "Dolor torácico agudo",
    "Reacción alérgica grave (anafilaxia)",
    "Hemorragia grave",
    "Convulsiones",
    "Caída con posible fractura",
    "Intoxicación por medicamentos o drogas"
]

emergencia_bomberos = [ 
    "Incendio en vivienda",
    "Incendio forestal",
    "Incendio en vehículo",
    "Fuga de gas",
    "Derrumbe de estructura",
    "Rescate en altura",
    "Accidente químico",
    "Inundación urbana",
    "Persona atrapada en ascensor",
    "Corte de energía por incendio"
]

emergencia_policia = [
    "Robo en curso",
    "Violencia doméstica",
    "Persona desaparecida",
    "Pelea en la vía pública",
    "Conducción temeraria",
    "Amenaza con arma blanca",
    "Allanamiento de morada",
    "Disturbios o altercados",
    "Intento de suicidio",
    "Secuestro o retención ilegal"
]

POSIBLES_LUGARES = [
    "Calle Principal 123", "Parque Central", "Centro Comercial Sur",
    "Urbanización Las Lomas", "Carretera Vieja KM 5", "Edificio Antiguo",
    "Plaza Mayor", "Río Seco"
]

# --- Funciones para generar partes del evento ---
def generar_servicio():
    return random.choice(servicios)

def generar_lugar():
    return random.choice(POSIBLES_LUGARES)

def generar_telefono():
    return random.choice(['6', '7']) + ''.join([str(random.randint(0, 9)) for _ in range(8)])

def generar_timestamp():
    return datetime.now().isoformat()

def generar_emergencia(servicio):
    if servicio == "Ambulancia":
        return random.choice(emergencia_ambulancia)
    elif servicio == "Bombero":
        return random.choice(emergencia_bomberos)
    elif servicio == "Policía":
        return random.choice(emergencia_policia)
    else:
        return "Emergencia no especificada"

# --- Construcción del evento completo ---
def generar_evento_aleatorio():
    servicio = generar_servicio()
    emergencia_base = generar_emergencia(servicio)
    lugar = generar_lugar()
    telefono = generar_telefono()
    timestamp = generar_timestamp()

    payload = {
        "servicio": servicio,
        "telefono": telefono,
        "emergencia": f"{emergencia_base} en {lugar}",
        "timestamp_generacion": timestamp
    }
    return payload

# --- Envío del evento ---
def enviar_evento_api(evento_payload):
    headers = {'Content-Type': 'application/json'}
    try:
        print(f"Enviando a API: {json.dumps(evento_payload)}")
        response = requests.post(API_URL, headers=headers, data=json.dumps(evento_payload), timeout=10)

        print(f"Respuesta de API: Código {response.status_code}")
        try:
            print(f"   Respuesta Body: {response.json()}")
        except json.JSONDecodeError:
            print(f"   Respuesta Body (no JSON): {response.text}")

        if not 200 <= response.status_code < 300:
            print("¡ALERTA! La API devolvió un código de error.")
    except requests.exceptions.ConnectionError:
        print(f"¡ERROR DE CONEXIÓN! No se pudo conectar a la API en {API_URL}. ¿Está corriendo?")
    except requests.exceptions.Timeout:
        print(f"¡ERROR DE TIMEOUT! La API no respondió a tiempo.")
    except Exception as e:
        print(f"¡ERROR INESPERADO al enviar el evento!: {e}")

# --- Bucle Principal ---
if __name__ == "__main__":
    print(f"--- Iniciando Generador Automático de Eventos ---")
    print(f"Enviando eventos a la API: {API_URL}")
    print(f"Presiona Ctrl+C para detener.")

    event_counter = 0
    try:
        while True:
            event_counter += 1
            print(f"\n--- Generando Evento #{event_counter} ---")
            evento = generar_evento_aleatorio()
            enviar_evento_api(evento)

            wait_time = random.uniform(tiempo_minimo, tiempo_maximo)
            print(f"Esperando {wait_time:.2f} segundos...")
            time.sleep(wait_time)

    except KeyboardInterrupt:
        print("\n--- Generador de eventos detenido por el usuario ---")
