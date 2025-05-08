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

        print(f"📢 Mensaje recibido: {data}")
        
        evento_id = data[1]["evento_id"]
        recurso_id = data[0]["recurso_id"]
        servicio = data[0]["servicio_recurso"]
        nivel_emergencia = data[1]["nivel_emergencia"]
        tiempo_respuesta = data[1]["tiempo_respuesta"]
        distancia = data[1]["distancia_recorrida"]
        timestamp_evento = data[1]["timestamp_evento"]

        

     
        logging.info(f"📢 El evento {evento_id} ha sido MACHEADO. Recurso asignado: {recurso_id} ({servicio}). Llegará en {tiempo_respuesta} segundos ⏱. Este evento se genero en {timestamp_evento}, recorrerá uns distancia de {distancia} km hasta el evento. Nivel de emergencia: {nivel_emergencia}.")

    except Exception as e:
        logging.error(f"❌ Error procesando mensaje: {e}")

