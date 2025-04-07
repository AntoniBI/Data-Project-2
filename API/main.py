import os
import json
from flask import Flask, request, jsonify
from google.cloud import pubsub_v1

app = Flask(__name__)

# Set up Google Cloud Pub/Sub

PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "splendid-strand-452918-e6")
PUBSUB_TOPIC_ID = os.environ.get("PUBSUB_TOPIC_ID", "poc_data2")

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, PUBSUB_TOPIC_ID)

@app.route('/api/request-help', methods=['POST'])
def request_help():
    """Recibe una solicitud de ayuda y la publica en Pub/Sub."""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # --- Validación Básica ---
    required_fields = ['servicio', 'telefono', 'emergencia']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # Codificar los datos a bytes para Pub/Sub
        message_data = json.dumps(data).encode("utf-8")

        # Publicar el mensaje
        future = publisher.publish(topic_path, data=message_data)
        message_id = future.result() # Espera confirmación (opcional, puede ralentizar)

        print(f"Published message {message_id} to {topic_path}")
        # print(f"Simulación: Publicaría en {topic_path} los datos: {message_data.decode('utf-8')}")
        # message_id = "simulated-local-id-123"

        # print(f"Simulated publish for message {message_id} to {topic_path}")

        # Responder al cliente que la solicitud fue aceptada
        return jsonify({"status": "received", "message_id": message_id}), 202

    except Exception as e:
        print(f"Error publishing message: {e}")
        return jsonify({"error": "Failed to process request"}), 500

if __name__ == '__main__':
    # Cloud Run proporciona la variable de entorno PORT
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host='0.0.0.0', port=port)