import random
import json
import requests
import time
from datetime import datetime
import uuid
import os

API_URL = "https://str-service-puifiielba-no.a.run.app"

servicios = ["Policia", "Bombero", "Ambulancia"]
 
tipos = ["Individual", "Colectiva"]
 
discapacidades = [
    "Grado 1: Discapacidad nula",
    "Grado 2: Discapacidad leve",
    "Grado 3: Discapacidad moderada",
    "Grado 4: Discapacidad grave",
    "Grado 5: Discapacidad muy grave"
]
 
niveles = [
    "Nivel 1: Emergencia leve",
    "Nivel 2: Emergencia moderada",
    "Nivel 3: Emergencia grave"
]
 
def generar_dato():

    tipo = random.choice(tipos)
    payload = {
        "evento_id": str(uuid.uuid4())[:8],
        "timestamp_evento": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "servicio": random.choice(servicios),
        "tipo": tipo,
        "discapacidad": random.choice(discapacidades),
        "nivel_emergencia": random.choice(niveles),
        "lat": round(random.uniform(39.4300, 39.5100), 6),
        "lon": round(random.uniform(-0.4200, -0.3400), 6),
    }
 
    if tipo == "Individual":
        payload["edad"] = random.randint(1, 100)
    return payload
 
def enviar_solicitudes(delay=5):

    i = 1
    while True:
        payload = generar_dato()
        try:

            res = requests.post(
                url=f"{API_URL}/api/request-help",
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
            )

            print(f"[{i}] Enviado -> Status {res.status_code} | {payload}")

        except Exception as e:

            print(f"[{i}] Error al enviar: {e}")

        i += 1

        time.sleep(delay)
 
if __name__ == "__main__":

    enviar_solicitudes(delay=50)  
 