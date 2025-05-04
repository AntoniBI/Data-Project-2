import os
import json
from flask import Flask, request, jsonify
from google.cloud import pubsub_v1
# from google.cloud import bigquery

app = Flask(__name__)

# bq_client = bigquery.Client()

# BQ_DATASET = os.environ.get("BQ_DATASET", "emergencias_eventos")
# BQ_TABLE = os.environ.get("BQ_TABLE", "emergencias-macheadas")

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


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host='0.0.0.0', port=port)


