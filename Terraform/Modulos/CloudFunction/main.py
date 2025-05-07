# import json
# import base64
# import logging
# import functions_framework


# logging.getLogger().setLevel(logging.INFO)

# """ Code: Entry point """

# @functions_framework.cloud_event
# def get_pubsub_message(cloud_event):

#     """
#     Simulates receiving a PubSub message and processes it to send data to Firebase.

#     Parameters:
#         cloud_event (dict): The Cloud Event message containing the PubSub payload.

#     Returns:
#         dict: A message containing the processed message data that would be sent to Firebase.
#     """
    
 
#     pubsub_msg = base64.b64decode(cloud_event.data["message"]["data"])
#     msg = json.loads(pubsub_msg)

#     content = f"""
#         {msg['message']}
#     """

   
#     logging.info(content)


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
        # Decodificar el mensaje
        pubsub_message = base64.b64decode(cloud_event.data["message"]["data"])
        data = json.loads(pubsub_message)

        evento_id = data.get("evento_id", "desconocido")
        recurso_id = data.get("recurso_id", "no asignado")
        servicio = data.get("servicio_recurso", "desconocido")
        nivel_emergencia = data.get("nivel_emergencia", "no indicado")
        tiempo_respuesta = data.get("tiempo_respuesta", "N/A")
        distancia = data.get("distancia_recorrida", "N/A")

        # Log informativo
        logging.info(f"📢 Evento {evento_id} ha sido MACHEADO.")
        logging.info(f"🚨 Nivel de emergencia: {nivel_emergencia}")
        logging.info(f"🚑 Recurso asignado: {recurso_id} ({servicio})")
        logging.info(f"⏱ Tiempo respuesta: {tiempo_respuesta} segundos")
        logging.info(f"📏 Distancia recorrida: {distancia} km")

    except Exception as e:
        logging.error(f"❌ Error procesando mensaje: {e}")
