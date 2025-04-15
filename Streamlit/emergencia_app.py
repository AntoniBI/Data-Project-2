import streamlit as st
from streamlit_js_eval import streamlit_js_eval
import requests
import json
import uuid
from datetime import datetime

st.title("Emergencias 112 📞")

lat= None
lon= None

servicio = st.selectbox(
    "🛠️ ¿Qué servicio necesitas?",
    ("Policia", "Bombero", "Ambulancia"),
    index=None,
    placeholder="Selecciona un servicio",
)
st.write("Has seleccionado:", servicio)

tipo = st.selectbox(
    "👥 ¿La afectación es individual o colectiva?",
    ("Individual", "Colectiva"),
    index=None,
    placeholder="Selecciona la afectación",
)
st.write("Has seleccionado:", tipo)

if tipo == "Individual":
    edad = st.number_input("¿Qué edad tiene la persona afectada?", min_value=0, max_value=120, value=0)
    st.write("La persona afectada tiene:", edad, "años")

disc = st.selectbox(
    "♿ ¿Tiene algún tipo de discapacidad?",
    ("Grado 1: Discapacidad nula", "Grado 2: Discapacidad leve", "Grado 3: Discapacidad moderada", "Grado 4: Discapacidad grave", "Grado 5: Discapacidad muy grave"),
    index=None,
    placeholder="Selecciona el grado de discapacidad",
)
st.write("Has seleccionado:", disc)

nivel = st.selectbox(
    "⚠️ ¿Cuál es el nivel de emergencia?",
    ("Nivel 1: Emergencia leve", "Nivel 2: Emergencia moderada", "Nivel 3: Emergencia grave"),
    index=None,
    placeholder="Selecciona el nivel de emergencia",
)
st.write("Has seleccionado:", nivel)

st.subheader("📍 Ubicación del incidente")

boton = st.button("🌍 Obtener ubicación precisa")

js_code = """
new Promise((resolve, reject) => {
    navigator.geolocation.getCurrentPosition(
        (position) => {
            resolve({
                coords: {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                }
            });
        },
        (error) => {
            reject(error.message);
        }
    );
})
"""

location = streamlit_js_eval(js_expressions=js_code, key="geoloc")
if boton:
    if location and "coords" in location:
        lat = location["coords"]["latitude"]
        lon = location["coords"]["longitude"]
        st.success("📍 Ubicación detectada con éxito")
        st.write(f"Latitud: {lat}")
        st.write(f"Longitud: {lon}")
        st.map(data={"lat": [lat], "lon": [lon]})
        st.session_state.lat = lat
        st.session_state.lon = lon
    elif location is not None:
        st.error(f"❌ Error al obtener la ubicación: {location}")
    else:
        st.info("⌛ Esperando permiso para acceder a tu ubicación...")

def obtener_payload():
    payload = {
        "event_id": str(uuid.uuid4())[:8],
        "timestamp_evento": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "servicio": servicio,
        "tipo": tipo,
        "discapacidad": disc,
        "nivel_emergencia": nivel,
    }

    # Solo agregar "edad" si el tipo es "Individual"
    if tipo == "Individual":
        payload["edad"] = edad

    # Solo agregar latitud y longitud si se obtuvieron
    if st.session_state.lat is not None and st.session_state.lon is not None:
        payload["lat"] = st.session_state.lat
        payload["lon"] = st.session_state.lon

    return payload

enviar = st.button("Enviar solicitud de ayuda")
if enviar:
   
    payload = obtener_payload()
    
    # Realizamos el envío
    try:
        res = requests.post(url="http://127.0.0.1:8082/api/request-help", data=json.dumps(payload), headers={"Content-Type": "application/json"})
        
        if res.status_code == 202:
            st.success("Solicitud enviada con éxito!")
        else:
            st.error(f"Error al enviar la solicitud. Código de respuesta: {res.status_code}")
    
    except Exception as e:
        st.error(f"Error al enviar la solicitud: {e}")

