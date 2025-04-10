import random
import json
import requests
import time
 
servicios = ["Policía", "Bomberos", "Ambulancia"]
 
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
        "servicio": random.choice(servicios),
        "tipo": tipo,
        "discapacidad": random.choice(discapacidades),
        "nivel_emergencia": random.choice(niveles),
        "lat": round(random.uniform(36.0, 43.0), 6),
        "lon": round(random.uniform(-9.0, 3.5), 6),
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
                url="http://127.0.0.1:8082/api/request-help",
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
            )

            print(f"[{i}] Enviado -> Status {res.status_code} | {payload}")

        except Exception as e:

            print(f"[{i}] Error al enviar: {e}")

        i += 1

        time.sleep(delay)
 
if __name__ == "__main__":

    enviar_solicitudes(delay=5)  
 