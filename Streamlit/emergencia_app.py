

import streamlit as st
from streamlit_js_eval import streamlit_js_eval
import requests
import json
import uuid
from datetime import datetime


API_URL = "https://str-service-puifiielba-no.a.run.app"

st.set_page_config(page_title="Emergencias 112", page_icon="📞", layout="centered")

st.markdown("<h1 style='text-align: center;'>🚨 Emergencias 112</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Por favor, rellena la información para solicitar ayuda</p>", unsafe_allow_html=True)
st.divider()

lat = None
lon = None

with st.container():
    col1, col2 = st.columns(2)

    with col1:
        servicio = st.selectbox(
            "🛠️ Servicio necesario",
            ("Policia", "Bombero", "Ambulancia"),
            index=None,
            placeholder="Selecciona uno",
        )
    with col2:
        tipo = st.selectbox(
            "👥 Afectación",
            ("Individual", "Colectiva"),
            index=None,
            placeholder="Selecciona una opción",
        )

if servicio:
    st.info(f"🔔 Servicio seleccionado: **{servicio}**")

if tipo:
    st.info(f"👤 Tipo de afectación: **{tipo}**")

if tipo == "Individual":
    edad = st.slider("🎂 Edad de la persona afectada", 0, 120, 30)
    st.write(f"Edad seleccionada: {edad} años")

disc = st.selectbox(
    "♿ Grado de discapacidad",
    (
        "Grado 1: Discapacidad nula", 
        "Grado 2: Discapacidad leve", 
        "Grado 3: Discapacidad moderada", 
        "Grado 4: Discapacidad grave", 
        "Grado 5: Discapacidad muy grave"
    ),
    index=None,
    placeholder="Selecciona el grado",
)

nivel = st.selectbox(
    "⚠️ Nivel de emergencia",
    ("Nivel 1: Emergencia leve", "Nivel 2: Emergencia moderada", "Nivel 3: Emergencia grave"),
    index=None,
    placeholder="Selecciona el nivel",
)

st.divider()
st.subheader("📍 Ubicación del incidente")
boton = st.button("📡 Obtener ubicación actual")

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
        st.map(data={"lat": [lat], "lon": [lon]})
        st.session_state.lat = lat
        st.session_state.lon = lon
    elif location is not None:
        st.error(f"❌ Error: {location}")
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

    if tipo == "Individual":
        payload["edad"] = edad

    if st.session_state.get("lat") and st.session_state.get("lon"):
        payload["lat"] = st.session_state.lat
        payload["lon"] = st.session_state.lon

    return payload

st.divider()
if st.button("🚀 Enviar solicitud de ayuda", type="primary"):
    payload = obtener_payload()

    try:
        res = requests.post(
            url=(f"{API_URL}/api/request-help"),
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"}
        )

        if res.status_code == 202:
            st.success("✅ ¡Solicitud enviada con éxito!. La ayuda llegará pronto!")
        else:
            st.error(f"❌ Error: Código de respuesta {res.status_code}")
    except Exception as e:
        st.error(f"❌ Error al enviar la solicitud: {e}")









