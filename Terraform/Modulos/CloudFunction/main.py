import json
import base64
import logging
import functions_framework

logging.getLogger().setLevel(logging.INFO)

@functions_framework.cloud_event
def get_pubsub_message(cloud_event):
    """
    Función Cloud Function para procesar mensajes Pub/Sub provenientes de Dataflow,
    indicando que un evento ha sido macheado con éxito.
    """

    try:
        
        pubsub_message = base64.b64decode(cloud_event.data["message"]["data"])
        data = json.loads(pubsub_message)

        evento_id = data.get("evento_id", "desconocido")
        recurso_id = data.get("recurso_id", "no asignado")
        servicio = data.get("servicio_recurso", "desconocido")
        nivel_emergencia = data.get("nivel_emergencia", "no indicado")
        tiempo_respuesta = data.get("tiempo_respuesta", "N/A")
        distancia = data.get("distancia_recorrida", "N/A")
        timestamp_evento = data.get("timestamp_evento", "no indicado")

        # Log informativo
        logging.info(f"📢 El evento {evento_id} ha sido MACHEADO. Recurso asignado: {recurso_id} ({servicio}). Llegará en {tiempo_respuesta} segundos ⏱. Este evento se genero en {timestamp_evento}, recorrerá uns distancia de {distancia} km hasta el evento. Nivel de emergencia: {nivel_emergencia}.")

    except Exception as e:
        logging.error(f"❌ Error procesando mensaje: {e}")
