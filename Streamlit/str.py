import streamlit as st
from streamlit_js_eval import streamlit_js_eval
import requests
import json

st.title("Emergencias 112 📞")

servicio = st.selectbox(
    "¿Qué servicio necesitas?",
    ("Policía", "Bomberos", "Ambulancia"),
    index=None,
    placeholder="Selecciona un servicio",
)
st.write("Has seleccionado:", servicio)

tipo = st.selectbox(
    "¿La afectación es individual o colectiva?",
    ("Individual", "Colectiva"),
    index=None,
    placeholder="Selecciona la afectación",
)
st.write("Has seleccionado:", tipo)

if tipo == "Individual":
    edad = st.number_input("¿Qué edad tiene la persona afectada?", min_value=0, max_value=120, value=0)
    st.write("La persona afectada tiene:", edad, "años")

disc = st.selectbox(
    "¿Tiene algún tipo de discapacidad?",
    ("Grado 1: Discapacidad nula", "Grado 2: Discapacidad leve", "Grado 3: Discapacidad moderada", "Grado 4: Discapacidad grave", "Grado 5: Discapacidad muy grave"),
    index=None,
    placeholder="Selecciona el grado de discapacidad",
)
st.write("Has seleccionado:", disc)

nivel = st.selectbox(
    "¿Cuál es el nivel de emergencia?",
    ("Nivel 1: Emergencia leve", "Nivel 2: Emergencia moderada", "Nivel 3: Emergencia grave"),
    index=None,
    placeholder="Selecciona el nivel de emergencia",
)
st.write("Has seleccionado:", nivel)

boton = st.button("🌍 Obtener ubicación precisa")

# Esta es la forma correcta de obtener la ubicación con promesa
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

# Evaluar la expresión JS
location = streamlit_js_eval(js_expressions=js_code, key="geoloc")
if boton:
    if location and "coords" in location:
        lat = location["coords"]["latitude"]
        lon = location["coords"]["longitude"]
        st.success("Ubicación detectada con éxito")
        st.write(f"Latitud: {lat}")
        st.write(f"Longitud: {lon}")
        st.map(data={"lat": [lat], "lon": [lon]})
        st.session_state.lat = lat
        st.session_state.lon = lon
    elif location is not None:
        st.error(f"Error al obtener la ubicación: {location}")
    else:
        st.info("Esperando permiso para acceder a tu ubicación...")



enviar = st.button("Enviar solicitud de ayuda")
if enviar:
    res = requests.post(url="http://127.0.0.1:8080/api/request-help", data=json.dumps({
        "servicio": servicio,
        "tipo": tipo,
        "edad": edad,
        "discapacidad": disc,
        "nivel": nivel,
        "latitud": st.session_state.lat,
        "longitud": st.session_state.lon        
    }))

    st.stop()