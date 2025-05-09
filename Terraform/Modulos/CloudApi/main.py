# import os
# import json
# from flask import Flask, request, jsonify
# from google.cloud import pubsub_v1
# from google.cloud.sql.connector import Connector
# import pg8000

# app = Flask(__name__)

# # bq_client = bigquery.Client()

# # BQ_DATASET = os.environ.get("BQ_DATASET", "emergencias_eventos")
# # BQ_TABLE = os.environ.get("BQ_TABLE", "emergencias-macheadas")

# PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "splendid-strand-452918-e6")
# HELP_TOPIC_ID = os.environ.get("PUBSUB_TOPIC_ID", "emergencias_events")
# LOCATION_TOPIC_ID = os.environ.get("PUBSUB_LOCATION_TOPIC_ID", "emergencias_ubi_autos")

# publisher = pubsub_v1.PublisherClient()
# help_topic_path = publisher.topic_path(PROJECT_ID, HELP_TOPIC_ID)
# location_topic_path = publisher.topic_path(PROJECT_ID, LOCATION_TOPIC_ID)


# @app.route('/api/request-help', methods=['POST'])
# def request_help():
#     if not request.is_json:
#         return jsonify({"error": "Request must be JSON"}), 400

#     data = request.get_json()

#     required_fields = ['servicio', 'tipo', 'discapacidad', 'nivel_emergencia']
#     missing_fields = [f for f in required_fields if f not in data]

#     if missing_fields:
#         return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

#     if data.get("tipo") == "Individual" and "edad" not in data:
#         return jsonify({"error": "Edad es obligatoria para tipo 'Individual'"}), 400

#     try:
#         message_data = json.dumps(data).encode("utf-8")
#         future = publisher.publish(help_topic_path, data=message_data)
#         message_id = future.result()

#         print(f"[HELP] Published message {message_id} to {help_topic_path}")
#         return jsonify({"status": "received", "message_id": message_id}), 202

#     except Exception as e:
#         print(f"Error publishing help message: {e}")
#         return jsonify({"error": "Failed to process request"}), 500


# @app.route('/api/update-location', methods=['POST'])
# def update_location():
#     if not request.is_json:
#         return jsonify({"error": "Request must be JSON"}), 400

#     data = request.get_json()
#     required_fields = ['recurso_id', 'servicio', 'latitud', 'longitud', 'timestamp_ubicacion']

#     missing_fields = [f for f in required_fields if f not in data]
#     if missing_fields:
#         return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

#     try:
#         message_data = json.dumps(data).encode("utf-8")
#         future = publisher.publish(location_topic_path, data=message_data)
#         message_id = future.result()

#         print(f"[LOCATION] Published message {message_id} to {location_topic_path}")
#         return jsonify({"status": "location updated", "message_id": message_id}), 202

#     except Exception as e:
#         print(f"Error publishing location message: {e}")
#         return jsonify({"error": "Failed to publish location"}), 500
    

# if __name__ == '__main__':
#     port = int(os.environ.get("PORT", 8080))
#     app.run(debug=True, host='0.0.0.0', port=port)


























import os
import json
from flask import Flask, request, jsonify
from google.cloud import pubsub_v1, bigquery
from google.cloud.sql.connector import Connector
import pg8000


app = Flask(__name__)

PROJECT_ID = "splendid-strand-452918-e6"
HELP_TOPIC_ID = "emergencias_events"
LOCATION_TOPIC_ID = "emergencias_ubi_autos"
INSTANCE_CONNECTION_NAME = "splendid-strand-452918-e6:europe-southwest1:recursos"

DB_CONFIG = {
    'dbname': 'recursos-emergencia',
    'user': 'vehiculos',
    'password': 'admin123',
    'port': '5432',
}


publisher = pubsub_v1.PublisherClient()
help_topic_path = publisher.topic_path(PROJECT_ID, HELP_TOPIC_ID)
location_topic_path = publisher.topic_path(PROJECT_ID, LOCATION_TOPIC_ID)


connector = Connector()

def get_db_connection():
    """Conexión a PostgreSQL usando Cloud SQL Connector"""
    conn = connector.connect(
        INSTANCE_CONNECTION_NAME,
        "pg8000",
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        db=DB_CONFIG['dbname'],
        port=int(DB_CONFIG['port']),
    )
    return conn

@app.route('/api/request-help', methods=['POST'])
def request_help():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    required_fields = ['servicio', 'tipo', 'discapacidad', 'nivel_emergencia']
    missing_fields = [f for f in required_fields if f not in data]

    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    if data.get("tipo") == "Individual" and "edad" not in data:
        return jsonify({"error": "Edad es obligatoria para tipo 'Individual'"}), 400

    try:
        message_data = json.dumps(data).encode("utf-8")
        future = publisher.publish(help_topic_path, data=message_data)
        message_id = future.result()

        print(f"[HELP] Published message {message_id} to {help_topic_path}")
        return jsonify({"status": "received", "message_id": message_id}), 202

    except Exception as e:
        print(f"Error publishing help message: {e}")
        return jsonify({"error": "Failed to process request"}), 500

@app.route('/api/update-location', methods=['POST'])
def update_location():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    required_fields = ['recurso_id', 'servicio', 'latitud', 'longitud', 'timestamp_ubicacion']
    missing_fields = [f for f in required_fields if f not in data]

    if missing_fields:
        return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

    try:
        message_data = json.dumps(data).encode("utf-8")
        future = publisher.publish(location_topic_path, data=message_data)
        message_id = future.result()

        print(f"[LOCATION] Published message {message_id} to {location_topic_path}")
        return jsonify({"status": "location updated", "message_id": message_id}), 202

    except Exception as e:
        print(f"Error publishing location message: {e}")
        return jsonify({"error": "Failed to publish location"}), 500

@app.route('/api/recursos-asignados', methods=['GET'])
def get_recursos_asignados():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT recurso_id, servicio, latitud, longitud FROM recursos WHERE asignado = FALSE;")
        recursos = cursor.fetchall()
        cursor.close()
        conn.close()

        recursos_list = [
            {
                "recurso_id": r[0],
                "servicio": r[1],
                "latitud": r[2],
                "longitud": r[3]
            }
            for r in recursos
        ]
        return jsonify(recursos_list), 200

    except Exception as e:
        print(f"Error retrieving assigned resources: {e}")
        return jsonify({"error": "Could not retrieve assigned resources"}), 500
    

# @app.route('/api/estado-evento', methods=['GET'])
# def estado_evento():
#     evento_id = request.args.get('evento_id')
#     if not evento_id:
#         return jsonify({"error": "Parámetro 'evento_id' es obligatorio"}), 400

#     client = bigquery.Client(project=PROJECT_ID)

#     dataset = "emergencia_eventos"
#     tabla_macheadas = f"`{PROJECT_ID}.{dataset}.emergencias-macheadas`"
#     tabla_no_macheadas = f"`{PROJECT_ID}.{dataset}.emergencias-no-macheadas`"

#     try:
#         query_macheado = f"""
#         SELECT evento_id FROM {tabla_macheadas}
#         WHERE evento_id = @evento_id
#         LIMIT 1
#         """
#         job_macheado = client.query(
#             query_macheado,
#             job_config=bigquery.QueryJobConfig(
#                 query_parameters=[
#                     bigquery.ScalarQueryParameter("evento_id", "STRING", evento_id)
#                 ]
#             )
#         )
#         macheado_result = list(job_macheado.result())

#         if macheado_result:
#             return jsonify({"evento_id": evento_id, "estado": "macheado"}), 200

        
#         query_no_macheado = f"""
#         SELECT evento_id FROM {tabla_no_macheadas}
#         WHERE evento_id = @evento_id
#         LIMIT 1
#         """
#         job_no_macheado = client.query(
#             query_no_macheado,
#             job_config=bigquery.QueryJobConfig(
#                 query_parameters=[
#                     bigquery.ScalarQueryParameter("evento_id", "STRING", evento_id)
#                 ]
#             )
#         )
#         no_macheado_result = list(job_no_macheado.result())

#         if no_macheado_result:
#             return jsonify({"evento_id": evento_id, "estado": "no macheado"}), 200

#         return jsonify({"evento_id": evento_id, "estado": "no encontrado"}), 404

#     except Exception as e:
#         print(f"Error al consultar estado del evento: {e}")
#         return jsonify({"error": "Error al consultar BigQuery"}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)









