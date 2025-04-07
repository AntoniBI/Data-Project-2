import requests
import Streamlit.streamlit as st
import json


# --- Configuración ---
# !! IMPORTANTE: Usa la URL donde tu API Flask se está ejecutando LOCALMENTE !!
# Por defecto, Flask corre en el puerto 8080 si usaste el ejemplo.
# Asegúrate de que la ruta (/api/request-help) coincida con tu @app.route
API_BASE_URL = "http://127.0.0.1:8080" # O el puerto que esté usando tu Flask local
API_ENDPOINT = "/api/request-help"
API_URL = f"{API_BASE_URL}{API_ENDPOINT}"

st.set_page_config(layout="centered") # Opcional: Centra el contenido
st.title("Simulador de Petición de Ayuda (Local)")

st.write(f"Este formulario enviará datos a tu API local en: `{API_URL}`")
st.markdown("---") # Línea separadora

# --- Formulario Streamlit ---
with st.form("request_form"):
    st.subheader("Detalles del Incidente:")

    # Campos del formulario (¡Asegúrate que coincidan con lo que espera tu API!)
    servicio_input = st.selectbox(
        "Servicio Requerido:",
        ("Bombero", "Policía", "Médica", "Otro"),
        key="servicio" # La clave 'key' debe coincidir con el nombre esperado en el JSON
    )
    telefono_input = st.text_input(
        "Número de Teléfono de Contacto:",
        key="telefono"
    )
    emergencia_input = st.text_area(
        "Descripción de la Emergencia:",
        key="emergencia"
    )

    # Botón de envío dentro del formulario
    submitted = st.form_submit_button("Enviar a API Local")

# --- Lógica de Envío (Cuando se presiona el botón) ---
if submitted:
    # Validar entradas básicas (opcional pero bueno)
    if not telefono_input or not emergencia_input:
        st.warning("Por favor, completa todos los campos.")
    else:
        # 1. Crear el diccionario de datos (payload) para enviar
        #    Las claves DEBEN coincidir con las que espera tu API Flask
        payload = {
            "servicio": servicio_input,
            "telefono": telefono_input,
            "emergencia": emergencia_input
            # Añade más campos aquí si tu API los requiere
        }

        st.write("Enviando datos a la API...")
        st.json(payload) # Muestra el JSON que se va a enviar (para depuración)

        try:
            # 2. Definir las cabeceras (importante para que la API sepa que es JSON)
            headers = {'Content-Type': 'application/json'}

            # 3. Hacer la llamada POST a la API local usando 'requests'
            response = requests.post(API_URL, headers=headers, data=json.dumps(payload))

            # 4. Analizar la respuesta de la API
            st.markdown("---")
            st.subheader("Respuesta de la API:")

            # Mostrar el código de estado HTTP devuelto por la API
            st.write(f"Código de Estado HTTP: `{response.status_code}`")

            # Intentar mostrar la respuesta JSON (si la hay)
            try:
                response_data = response.json()
                st.json(response_data)
                if 200 <= response.status_code < 300: # Típicamente 200, 201, 202 indican éxito
                     st.success("¡API contactada y respondió exitosamente!")
                else:
                    st.error("La API respondió, pero indicó un error (ver código/mensaje arriba).")

            except json.JSONDecodeError:
                # Si la respuesta no es JSON válido
                st.warning("La API no devolvió una respuesta JSON válida.")
                st.text(response.text) # Muestra la respuesta como texto plano

        except requests.exceptions.ConnectionError as e:
            st.error(f"**Error de Conexión:** No se pudo conectar a la API en `{API_URL}`.")
            st.error("¿Está tu API Flask corriendo en una terminal separada?")
            st.error(f"Detalle del error: {e}")
        except Exception as e:
            st.error(f"Ocurrió un error inesperado al llamar a la API: {e}")