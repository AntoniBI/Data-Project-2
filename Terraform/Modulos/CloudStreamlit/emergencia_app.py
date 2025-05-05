# import streamlit as st
# from streamlit_js_eval import streamlit_js_eval
# import requests
# import json
# import os


# API_URL = "https://str-service-puifiielba-no.a.run.app"


# st.title("Emergencias 112 📞")

# lat= None
# lon= None

# servicio = st.selectbox(
#     "🛠️ ¿Qué servicio necesitas?",
#     ("Policía", "Bomberos", "Ambulancia"),
#     index=None,
#     placeholder="Selecciona un servicio",
# )
# st.write("Has seleccionado:", servicio)

# tipo = st.selectbox(
#     "👥 ¿La afectación es individual o colectiva?",
#     ("Individual", "Colectiva"),
#     index=None,
#     placeholder="Selecciona la afectación",
# )
# st.write("Has seleccionado:", tipo)

# if tipo == "Individual":
#     edad = st.number_input("¿Qué edad tiene la persona afectada?", min_value=0, max_value=120, value=0)
#     st.write("La persona afectada tiene:", edad, "años")

# disc = st.selectbox(
#     "♿ ¿Tiene algún tipo de discapacidad?",
#     ("Grado 1: Discapacidad nula", "Grado 2: Discapacidad leve", "Grado 3: Discapacidad moderada", "Grado 4: Discapacidad grave", "Grado 5: Discapacidad muy grave"),
#     index=None,
#     placeholder="Selecciona el grado de discapacidad",
# )
# st.write("Has seleccionado:", disc)

# nivel = st.selectbox(
#     "⚠️ ¿Cuál es el nivel de emergencia?",
#     ("Nivel 1: Emergencia leve", "Nivel 2: Emergencia moderada", "Nivel 3: Emergencia grave"),
#     index=None,
#     placeholder="Selecciona el nivel de emergencia",
# )
# st.write("Has seleccionado:", nivel)

# st.subheader("📍 Ubicación del incidente")

# boton = st.button("🌍 Obtener ubicación precisa")


# js_code = """
# new Promise((resolve, reject) => {
#     navigator.geolocation.getCurrentPosition(
#         (position) => {
#             resolve({
#                 coords: {
#                     latitude: position.coords.latitude,
#                     longitude: position.coords.longitude,
#                 }
#             });
#         },
#         (error) => {
#             reject(error.message);
#         }
#     );
# })
# """

# location = streamlit_js_eval(js_expressions=js_code, key="geoloc")
# if boton:
#     if location and "coords" in location:
#         lat = location["coords"]["latitude"]
#         lon = location["coords"]["longitude"]
#         st.success("📍 Ubicación detectada con éxito")
#         st.write(f"Latitud: {lat}")
#         st.write(f"Longitud: {lon}")
#         st.map(data={"lat": [lat], "lon": [lon]})
#         st.session_state.lat = lat
#         st.session_state.lon = lon
#     elif location is not None:
#         st.error(f"❌ Error al obtener la ubicación: {location}")
#     else:
#         st.info("⌛ Esperando permiso para acceder a tu ubicación...")

# def obtener_payload():
#     payload = {
#         "servicio": servicio,
#         "tipo": tipo,
#         "discapacidad": disc,
#         "nivel_emergencia": nivel,
#     }

    
#     if tipo == "Individual":
#         payload["edad"] = edad

    
#     if st.session_state.lat is not None and st.session_state.lon is not None:
#         payload["lat"] = st.session_state.lat
#         payload["lon"] = st.session_state.lon

#     return payload


# enviar = st.button("Enviar solicitud de ayuda")
# if enviar:
    
#     payload = obtener_payload()
    
    
#     try:
#         res = requests.post(f"{API_URL}/api/request-help", data=json.dumps(payload), headers={"Content-Type": "application/json"})
        
#         if res.status_code == 202:
#             st.success("Solicitud enviada con éxito!")
#         else:
#             st.error(f"Error al enviar la solicitud. Código de respuesta: {res.status_code}")
    
#     except Exception as e:
#         st.error(f"Error al enviar la solicitud: {e}")





# import streamlit as st
# from streamlit_js_eval import streamlit_js_eval
# import requests
# import json
# from google.cloud.sql.connector import Connector
# import pg8000
# import pandas as pd
# import pydeck as pdk

# # Configuración
# PROJECT_ID = "splendid-strand-452918-e6"
# REGION = "europe-southwest1"
# INSTANCE_NAME = "recursos"
# INSTANCE_CONNECTION_NAME = f"{PROJECT_ID}:{REGION}:{INSTANCE_NAME}"

# DB_USER = "vehiculos"
# DB_PASSWORD = "admin123"
# DB_NAME = "recursos-emergencia"

# API_URL = "https://str-service-puifiielba-no.a.run.app"

# # ----------------------------
# # CONEXIÓN A CLOUD SQL
# # ----------------------------
# @st.cache_resource
# def init_connection():
#     connector = Connector()
#     conn = connector.connect(
#         INSTANCE_CONNECTION_NAME,
#         "pg8000",
#         user=DB_USER,
#         password=DB_PASSWORD,
#         db=DB_NAME,
#     )
#     return conn

# def get_vehiculos_activos():
#     conn = init_connection()
#     df = pd.read_sql("SELECT * FROM recursos WHERE asignado = TRUE", conn)
#     return df


# st.title("Emergencias 112 📞")

# # Selector de servicio
# servicio = st.selectbox(
#     "🛠️ ¿Qué servicio necesitas?",
#     ("Policía", "Bomberos", "Ambulancia"),
#     index=None,
#     placeholder="Selecciona un servicio",
# )
# st.write("Has seleccionado:", servicio)

# # Afectación
# tipo = st.selectbox(
#     "👥 ¿La afectación es individual o colectiva?",
#     ("Individual", "Colectiva"),
#     index=None,
#     placeholder="Selecciona la afectación",
# )
# st.write("Has seleccionado:", tipo)

# # Edad
# if tipo == "Individual":
#     edad = st.number_input("¿Qué edad tiene la persona afectada?", min_value=0, max_value=120, value=0)
#     st.write("La persona afectada tiene:", edad, "años")

# # Discapacidad
# disc = st.selectbox(
#     "♿ ¿Tiene algún tipo de discapacidad?",
#     (
#         "Grado 1: Discapacidad nula",
#         "Grado 2: Discapacidad leve",
#         "Grado 3: Discapacidad moderada",
#         "Grado 4: Discapacidad grave",
#         "Grado 5: Discapacidad muy grave",
#     ),
#     index=None,
#     placeholder="Selecciona el grado de discapacidad",
# )
# st.write("Has seleccionado:", disc)


# nivel = st.selectbox(
#     "⚠️ ¿Cuál es el nivel de emergencia?",
#     (
#         "Nivel 1: Emergencia leve",
#         "Nivel 2: Emergencia moderada",
#         "Nivel 3: Emergencia grave",
#     ),
#     index=None,
#     placeholder="Selecciona el nivel de emergencia",
# )
# st.write("Has seleccionado:", nivel)


# st.subheader("📍 Ubicación del incidente")
# boton = st.button("🌍 Obtener ubicación precisa")

# js_code = """
# new Promise((resolve, reject) => {
#     navigator.geolocation.getCurrentPosition(
#         (position) => {
#             resolve({
#                 coords: {
#                     latitude: position.coords.latitude,
#                     longitude: position.coords.longitude,
#                 }
#             });
#         },
#         (error) => {
#             reject(error.message);
#         }
#     );
# })
# """

# location = streamlit_js_eval(js_expressions=js_code, key="geoloc")

# if boton:
#     if location and "coords" in location:
#         lat = location["coords"]["latitude"]
#         lon = location["coords"]["longitude"]
#         st.success("📍 Ubicación detectada con éxito")
#         st.write(f"Latitud: {lat}")
#         st.write(f"Longitud: {lon}")
#         st.map(data={"lat": [lat], "lon": [lon]})
#         st.session_state.lat = lat
#         st.session_state.lon = lon
#     elif location is not None:
#         st.error(f"❌ Error al obtener la ubicación: {location}")
#     else:
#         st.info("⌛ Esperando permiso para acceder a tu ubicación...")

# # ----------------------------
# # ENVIAR SOLICITUD
# # ----------------------------
# def obtener_payload():
#     payload = {
#         "servicio": servicio,
#         "tipo": tipo,
#         "discapacidad": disc,
#         "nivel_emergencia": nivel,
#     }

#     if tipo == "Individual":
#         payload["edad"] = edad

#     if st.session_state.get("lat") and st.session_state.get("lon"):
#         payload["lat"] = st.session_state.lat
#         payload["lon"] = st.session_state.lon

#     return payload

# if st.button("Enviar solicitud de ayuda"):
#     payload = obtener_payload()

#     try:
#         res = requests.post(
#             f"{API_URL}/api/request-help",
#             data=json.dumps(payload),
#             headers={"Content-Type": "application/json"},
#         )
#         if res.status_code == 202:
#             st.success("✅ Solicitud enviada con éxito")
#         else:
#             st.error(f"Error al enviar la solicitud. Código: {res.status_code}")
#     except Exception as e:
#         st.error(f"Error al enviar la solicitud: {e}")

# # ----------------------------
# # MAPA DE VEHÍCULOS ACTIVOS
# # ----------------------------
# st.subheader("🚓🚒🚑 Vehículos activos")

# df_vehiculos = get_vehiculos_activos()

# if not df_vehiculos.empty:
#     iconos = {
#         "Policía": "https://cdn-icons-png.flaticon.com/512/3048/3048122.png",
#         "Bomberos": "https://cdn-icons-png.flaticon.com/512/2965/2965567.png",
#         "Ambulancia": "https://cdn-icons-png.flaticon.com/512/2965/2965568.png",
#     }

#     df_vehiculos["icon_data"] = df_vehiculos["servicio"].apply(lambda s: {
#         "url": iconos.get(s, "https://cdn-icons-png.flaticon.com/512/565/565547.png"),
#         "width": 50,
#         "height": 50,
#         "anchorY": 50
#     })

#     icon_layer = pdk.Layer(
#         type="IconLayer",
#         data=df_vehiculos,
#         get_icon="icon_data",
#         get_position="[longitud, latitud]",
#         get_size=4,
#         size_scale=10,
#         pickable=True,
#     )

#     view_state = pdk.ViewState(
#         latitude=df_vehiculos["latitud"].mean(),
#         longitude=df_vehiculos["longitud"].mean(),
#         zoom=11,
#         pitch=0,
#     )

#     deck = pdk.Deck(
#         map_style="mapbox://styles/mapbox/streets-v11",
#         initial_view_state=view_state,
#         layers=[icon_layer],
#         tooltip={"text": "{servicio}"}
#     )

#     st.pydeck_chart(deck)
# else:
#     st.info("No hay vehículos activos en este momento.")


















import streamlit as st
from streamlit_js_eval import streamlit_js_eval
import requests
import json
from google.cloud.sql.connector import Connector
import pg8000
import pandas as pd
import pydeck as pdk

# Configuración
PROJECT_ID = "splendid-strand-452918-e6"
REGION = "europe-southwest1"
INSTANCE_NAME = "recursos"
INSTANCE_CONNECTION_NAME = f"{PROJECT_ID}:{REGION}:{INSTANCE_NAME}"

DB_USER = "vehiculos"
DB_PASSWORD = "admin123"
DB_NAME = "recursos-emergencia"

API_URL = "https://str-service-puifiielba-no.a.run.app"  # URL de la API de tu servicio

# ----------------------------
# CONEXIÓN A CLOUD SQL
# ----------------------------
@st.cache_resource
def init_connection():
    connector = Connector()
    conn = connector.connect(
        INSTANCE_CONNECTION_NAME,
        "pg8000",
        user=DB_USER,
        password=DB_PASSWORD,
        db=DB_NAME,
    )
    return conn

def get_vehiculos_activos():
    conn = init_connection()
    df = pd.read_sql("SELECT * FROM recursos WHERE asignado = TRUE", conn)
    return df

# ----------------------------
# FUNCIONES PARA CONSULTAR EL ESTADO DEL EVENTO
# ----------------------------
def consultar_evento(evento_id):
    try:
        response = requests.get(f"{API_URL}/api/status-evento/{evento_id}")
        if response.status_code == 200:
            return response.json()['mensaje']
        elif response.status_code == 404:
            return "Evento no encontrado."
        else:
            return "Error al consultar el evento."
    except Exception as e:
        return f"Error de conexión con la API: {e}"

# ----------------------------
# INTERFAZ DE USUARIO
# ----------------------------
st.title("Emergencias 112 📞")

# Selector de servicio
servicio = st.selectbox(
    "🛠️ ¿Qué servicio necesitas?",
    ("Policía", "Bomberos", "Ambulancia"),
    index=None,
    placeholder="Selecciona un servicio",
)
st.write("Has seleccionado:", servicio)

# Afectación
tipo = st.selectbox(
    "👥 ¿La afectación es individual o colectiva?",
    ("Individual", "Colectiva"),
    index=None,
    placeholder="Selecciona la afectación",
)
st.write("Has seleccionado:", tipo)

# Edad
if tipo == "Individual":
    edad = st.number_input("¿Qué edad tiene la persona afectada?", min_value=0, max_value=120, value=0)
    st.write("La persona afectada tiene:", edad, "años")

# Discapacidad
disc = st.selectbox(
    "♿ ¿Tiene algún tipo de discapacidad?",
    (
        "Grado 1: Discapacidad nula",
        "Grado 2: Discapacidad leve",
        "Grado 3: Discapacidad moderada",
        "Grado 4: Discapacidad grave",
        "Grado 5: Discapacidad muy grave",
    ),
    index=None,
    placeholder="Selecciona el grado de discapacidad",
)
st.write("Has seleccionado:", disc)


nivel = st.selectbox(
    "⚠️ ¿Cuál es el nivel de emergencia?",
    (
        "Nivel 1: Emergencia leve",
        "Nivel 2: Emergencia moderada",
        "Nivel 3: Emergencia grave",
    ),
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

# ----------------------------
# ENVIAR SOLICITUD
# ----------------------------
def obtener_payload():
    payload = {
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

if st.button("Enviar solicitud de ayuda"):
    payload = obtener_payload()

    try:
        res = requests.post(
            f"{API_URL}/api/request-help",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )
        if res.status_code == 202:
            st.success("✅ Solicitud enviada con éxito")
            
            # Consultar el estado del evento y mostrar el mensaje
            evento_id = res.json().get("evento_id")  # Asume que el evento_id se obtiene como respuesta
            if evento_id:
                mensaje_estado = consultar_evento(evento_id)
                st.write(f"Estado del evento: {mensaje_estado}")
            else:
                st.error("No se pudo obtener el ID del evento.")
                
        else:
            st.error(f"Error al enviar la solicitud. Código: {res.status_code}")
    except Exception as e:
        st.error(f"Error al enviar la solicitud: {e}")

# ----------------------------
# MAPA DE VEHÍCULOS ACTIVOS
# ----------------------------
st.subheader("🚓🚒🚑 Vehículos activos")

df_vehiculos = get_vehiculos_activos()

if not df_vehiculos.empty:
    iconos = {
        "Policia": "https://cdn-icons-png.flaticon.com/512/3048/3048122.png",
        "Bombero": "https://cdn-icons-png.flaticon.com/512/2965/2965567.png",
        "Ambulancia": "https://cdn-icons-png.flaticon.com/512/2965/2965568.png",
    }

    df_vehiculos["icon_data"] = df_vehiculos["servicio"].apply(lambda s: {
        "url": iconos.get(s, "https://cdn-icons-png.flaticon.com/512/565/565547.png"),
        "width": 50,
        "height": 50,
        "anchorY": 50
    })

    icon_layer = pdk.Layer(
        type="IconLayer",
        data=df_vehiculos,
        get_icon="icon_data",
        get_position="[longitud, latitud]",
        get_size=4,
        size_scale=10,
        pickable=True,
    )

    view_state = pdk.ViewState(
        latitude=df_vehiculos["latitud"].mean(),
        longitude=df_vehiculos["longitud"].mean(),
        zoom=11,
        pitch=0,
    )

    deck = pdk.Deck(
        map_style="mapbox://styles/mapbox/streets-v11",
        initial_view_state=view_state,
        layers=[icon_layer],
        tooltip={"text": "{servicio}"}
    )

    st.pydeck_chart(deck)
else:
    st.info("No hay vehículos activos en este momento.")
