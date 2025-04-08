import os
import json
from flask import Flask, request, jsonify
from google.cloud import pubsub_v1

app = Flask(__name__)

PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "splendid-strand-452918-e6")
PUBSUB_TOPIC_ID = os.environ.get("PUBSUB_TOPIC_ID", "emergencias_events")

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, PUBSUB_TOPIC_ID)

@app.route('/api/request-help', methods=['POST'])
def request_help():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    required_fields = ['servicio', 'tipo', 'discapacidad', 'nivel_emergencia']
    missing_fields = [f for f in required_fields if f not in data]

    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    # Si tipo es "Individual", la edad es obligatoria
    if data.get("tipo") == "Individual" and "edad" not in data:
        return jsonify({"error": "Edad es obligatoria para tipo 'Individual'"}), 400

    try:
        message_data = json.dumps(data).encode("utf-8")
        future = publisher.publish(topic_path, data=message_data)
        message_id = future.result()

        print(f"Published message {message_id} to {topic_path}")
        return jsonify({"status": "received", "message_id": message_id}), 202

    except Exception as e:
        print(f"Error publishing message: {e}")
        return jsonify({"error": "Failed to process request"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
