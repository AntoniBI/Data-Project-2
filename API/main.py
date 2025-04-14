#Codig Original

# import os
# import json
# from flask import Flask, request, jsonify
# from google.cloud import pubsub_v1
# # from google.cloud import bigquery

# app = Flask(__name__)

# PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "splendid-strand-452918-e6")
# PUBSUB_TOPIC_ID = os.environ.get("PUBSUB_TOPIC_ID", "emergencias_events")

# publisher = pubsub_v1.PublisherClient()
# topic_path = publisher.topic_path(PROJECT_ID, PUBSUB_TOPIC_ID)

# @app.route('/api/request-help', methods=['POST'])
# def request_help():
#     if not request.is_json:
#         return jsonify({"error": "Request must be JSON"}), 400

#     data = request.get_json()

#     required_fields = ['servicio', 'tipo', 'discapacidad', 'nivel_emergencia']
#     missing_fields = [f for f in required_fields if f not in data]

#     if missing_fields:
#         return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

#     # Si tipo es "Individual", la edad es obligatoria
#     if data.get("tipo") == "Individual" and "edad" not in data:
#         return jsonify({"error": "Edad es obligatoria para tipo 'Individual'"}), 400

#     try:
#         message_data = json.dumps(data).encode("utf-8")
#         future = publisher.publish(topic_path, data=message_data)
#         message_id = future.result()

#         print(f"Published message {message_id} to {topic_path}")
#         return jsonify({"status": "received", "message_id": message_id}), 202

#     except Exception as e:
#         print(f"Error publishing message: {e}")
#         return jsonify({"error": "Failed to process request"}), 500

# if __name__ == '__main__':
#     port = int(os.environ.get("PORT", 8082))
#     app.run(debug=True, host='0.0.0.0', port=port)



import os
import json
from flask import Flask, request, jsonify
from google.cloud import pubsub_v1

app = Flask(__name__)

PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "splendid-strand-452918-e6")
HELP_TOPIC_ID = os.environ.get("PUBSUB_TOPIC_ID", "emergencias_events")
LOCATION_TOPIC_ID = os.environ.get("PUBSUB_LOCATION_TOPIC_ID", "emergencias_ubi_autos")

publisher = pubsub_v1.PublisherClient()
help_topic_path = publisher.topic_path(PROJECT_ID, HELP_TOPIC_ID)
location_topic_path = publisher.topic_path(PROJECT_ID, LOCATION_TOPIC_ID)

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
    required_fields = ['recurso_id', 'servicio', 'latitud', 'longitud', 'timestamp']

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


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8082))
    app.run(debug=True, host='0.0.0.0', port=port)




























































# ## API para recibir solicitudes de ayuda y almacenarlas en BigQuery

# import os
# import json
# from flask import Flask, request, jsonify
# from google.cloud import bigquery

# app = Flask(__name__)

# PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "splendid-strand-452918-e6")
# DATASET_ID = "emergencia_eventos"
# TABLE_ID = "emergencias"

# # Cliente de BigQuery
# bq_client = bigquery.Client(project=PROJECT_ID)

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

#     # Preparar fila a insertar
#     row = {
#         "servicio": data["servicio"],
#         "tipo": data["tipo"],
#         "disc": data["discapacidad"],
#         "nivel": data["nivel_emergencia"],
#         "edad": data.get("edad", ""),  # Puede no venir si no es "Individual"
#         "lat": data.get("lat"),
#         "lon": data.get("lon"),
#     }

#     # Insertar en BigQuery
#     table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
#     errors = bq_client.insert_rows_json(table_ref, [row])

#     if errors:
#         print("Errores al insertar en BigQuery:", errors)
#         return jsonify({"error": "Error al guardar los datos en BigQuery"}), 500

#     return jsonify({"status": "received", "data": row}), 202

# if __name__ == '__main__':
#     port = int(os.environ.get("PORT", 8082))
#     app.run(debug=True, host='0.0.0.0', port=port)
