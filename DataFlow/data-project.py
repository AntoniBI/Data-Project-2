import apache_beam as beam
from datetime import datetime, timedelta, timezone
from apache_beam.runners.interactive.interactive_runner import InteractiveRunner
import apache_beam.runners.interactive.interactive_beam as ib
from apache_beam.options.pipeline_options import PipelineOptions
import json
import math
from google.cloud.sql.connector import Connector
from zoneinfo import ZoneInfo



# Set Logs

import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")

logging.getLogger("apache_beam").setLevel(logging.WARNING)


DB_CONFIG = {
    'dbname': 'recursos-emergencia',
    'user': 'vehiculos',
    'password': 'admin123',
    'port': '5432',
}

def incrementar_no_matched(x):
    x["no_matched"] = x.get("no_matched", 0) + 1
    return x

def decode_and_timestamp_event(msg):
    data = decode_message(msg)
    if 'timestamp_evento' in data:
        ts = datetime.strptime(data['timestamp_evento'], "%Y-%m-%d %H:%M:%S")
        return beam.window.TimestampedValue((data['servicio'], data), ts.timestamp())
    else:
        return None

def decode_and_timestamp_vehicle(msg):
    data = decode_message(msg)
    if 'timestamp_ubicacion' in data:
        ts = datetime.strptime(data['timestamp_ubicacion'], "%Y-%m-%d %H:%M:%S")
        return beam.window.TimestampedValue((data['servicio'], data), ts.timestamp())
    else:
        return None

def decode_message(msg):

    output = msg.decode('utf-8')

    return json.loads(output)
def encode_message(msg):
    return json.dumps(msg).encode('utf-8')

def calculo_coeficiente(vehiculo, emergencia):
    servicio = emergencia["servicio"]
    tipo_emergencia = emergencia["tipo"]
    edad=emergencia.get("edad", 0)
    discapacidad=emergencia["discapacidad"]
    nivel_emergencia=emergencia["nivel_emergencia"]
    latitud_emergencia=emergencia["lat"]
    longitud_emergencia=emergencia["lon"]
    latitud_vehiculo=vehiculo["latitud"]
    longitud_vehiculo=vehiculo["longitud"]

    if tipo_emergencia == "Individual":
        tipo_score = 0
        if edad < 10:
            tipo_score = 0.5
        elif edad > 70:
            tipo_score = 0.5
    elif tipo_emergencia == "Colectiva":
        tipo_score = 1.0
    
    if discapacidad == "Grado 1: Discapacidad nula":
        disc_score= 0.0
    elif discapacidad == "Grado 2: Discapacidad leve":
        disc_score= 0.2
    elif discapacidad == "Grado 3: Discapacidad moderada":
        disc_score= 0.4
    elif discapacidad == "Grado 4: Discapacidad grave":
        disc_score= 0.6
    elif discapacidad == "Grado 5: Discapacidad muy grave":
        disc_score= 0.8

    if nivel_emergencia == "Nivel 1: Emergencia leve":
        nivel_score= 0.2
        tiempo_total= 30
    elif nivel_emergencia == "Nivel 2: Emergencia moderada":
        nivel_score= 0.5
        tiempo_total= 60
    elif nivel_emergencia == "Nivel 3: Emergencia grave":
        nivel_score= 0.8
        tiempo_total= 120

    delta_lat = latitud_emergencia - latitud_vehiculo
    delta_lon = longitud_emergencia - longitud_vehiculo
    lat_prom = (latitud_vehiculo + latitud_emergencia) / 2

    # Aprox. metros por grado
    metros_lat = delta_lat * 111_000
    metros_lon = delta_lon * 111_000 * math.cos(math.radians(lat_prom))

    distancia_metros = (metros_lat**2 + metros_lon**2) ** 0.5        
    distancia_score = 1 / (1 + distancia_metros)
    
    if servicio == "Policia":
        tiempo_respuesta =  distancia_metros / (15*60)  # Velocidad promedio de un vehículo de policia en m/s, pasado a minutos
    else:
        tiempo_respuesta =  distancia_metros / (11*60)  # Velocidad promedio de un vehículo de bomberos o ambulancia en m/s, pasado a minutos

    tiempo_total+=tiempo_respuesta
    

    pesos = {
        "tipo": 0.2,
        "discapacidad": 0.25,
        "nivel": 0.4,
        "distancia": 0.25
    }

    # --- Cálculo del coeficiente ponderado ---
    coeficiente = (
        tipo_score * pesos["tipo"] +
        disc_score * pesos["discapacidad"] +
        nivel_score * pesos["nivel"] +
        distancia_score * pesos["distancia"]
    )

    return round(coeficiente, 4), tiempo_respuesta, tiempo_total, distancia_metros

def formatear_para_bigquery_matched(vehiculo, evento):
    return {
        "recurso_id": vehiculo["recurso_id"],
        "servicio_recurso": vehiculo["servicio"],
        "lat_recurso": vehiculo["latitud"],
        "lon_recurso": vehiculo["longitud"],
        "timestamp_ubicacion": vehiculo["timestamp_ubicacion"],

        "evento_id": evento["evento_id"],
        "timestamp_evento": evento["timestamp_evento"],
        "servicio_evento": evento["servicio"],
        "tipo": evento["tipo"],
        "descapacidad": evento["discapacidad"],
        "nivel_emergencia": evento["nivel_emergencia"],
        "lat_evento": evento["lat"],
        "lon_evento": evento["lon"],
        "coeficiente_seleccionado": evento["coeficiente_seleccionado"],
        "tiempo_total": evento["tiempo_total"],
        "tiempo_respuesta": evento["tiempo_respuesta"],
        "distancia_recorrida": evento["distancia_recorrida"],
        "disponible_en": evento["disponible_en"].astimezone(ZoneInfo("Europe/Madrid")).isoformat()

    }

def formatear_para_bigquery_no_matched(mensaje):
    return {
        "evento_id": mensaje["evento_id"],
        "timestamp_evento": datetime.strptime(mensaje["timestamp_evento"], "%Y-%m-%d %H:%M:%S").isoformat(),
        "servicio": mensaje["servicio"],
        "tipo": mensaje["tipo"],
        "discapacidad": mensaje["discapacidad"],
        "nivel_emergencia": mensaje["nivel_emergencia"],
        "lat": mensaje["lat"],
        "lon": mensaje["lon"],
        "edad": mensaje["edad"],
        "coeficientes": mensaje["coeficientes"],
        "no_matched_count": mensaje["no_matched_count"]

    }


class CalcularCoeficiente(beam.DoFn):
    def process(self, mensaje):
        if mensaje is None:
            return
        clave, (emergencias, vehiculos) = mensaje
        for i, emergencia in enumerate(emergencias):
            coeficinetes_lista = []
            for vehiculo in vehiculos:
                coficiente = calculo_coeficiente(vehiculo, emergencia)[0]
                coeficinetes_lista.append(coficiente)
            emergencia["coeficientes"]=coeficinetes_lista

        if clave == "Bombero":
            yield beam.pvalue.TaggedOutput("Bomberos", (vehiculos, emergencias))
        elif clave == "Policia":
            yield beam.pvalue.TaggedOutput("Policia", (vehiculos, emergencias))
        elif clave == "Ambulancia":
            yield beam.pvalue.TaggedOutput("Ambulancia", (vehiculos, emergencias))

class Asignacion(beam.DoFn):
    def process(self, mensaje):
        vehiculos, emergencias = mensaje
        match_list_emergencias_id = []
        match_list_vehiculos_id = []

        while True:
            max_total = -1
            match_evento = None
            mejor_vehiculo = None
            i_emergencia = -1
            i_vehiculo = -1

            for idx_e, emergencia in enumerate(emergencias):
                if emergencia["evento_id"] in match_list_emergencias_id:
                    continue

                for idx_v, vehiculo in enumerate(vehiculos):
                    if vehiculo["recurso_id"] in match_list_vehiculos_id:
                        continue

                    coef = emergencia["coeficientes"][idx_v]
                    if coef > max_total:
                        max_total = coef
                        match_evento = emergencia
                        mejor_vehiculo = vehiculo
                        i_emergencia = idx_e
                        i_vehiculo = idx_v

            if match_evento is None or mejor_vehiculo is None:
                break  

            # Añadir información al match
            match_evento["coeficiente_seleccionado"] = max_total
            tiempo_dist = calculo_coeficiente(mejor_vehiculo, match_evento)
            match_evento["tiempo_total"] = tiempo_dist[2]
            match_evento["tiempo_respuesta"] = tiempo_dist[1]
            match_evento["distancia_recorrida"] = tiempo_dist[3]
            match_evento["disponible_en"] = datetime.now(ZoneInfo("Europe/Madrid")) + timedelta(minutes=match_evento["tiempo_total"])
        
            match_list_emergencias_id.append(match_evento["evento_id"])
            match_list_vehiculos_id.append(mejor_vehiculo["recurso_id"])

            yield beam.pvalue.TaggedOutput("Match", (mejor_vehiculo, match_evento))

        # Emitir emergencias sin emparejar
        for emergencia in emergencias:
            if emergencia["evento_id"] not in match_list_emergencias_id:
                yield beam.pvalue.TaggedOutput("NoMatch", emergencia)


class ActualizarSQL(beam.DoFn):
    def process(self, match):
        vehiculo, emergencia = match
        try:
            connector = Connector()
            
            conn = connector.connect(
                "splendid-strand-452918-e6:europe-southwest1:recursos",  
                "pg8000",  
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                db=DB_CONFIG['dbname'],
            )
            cur = conn.cursor()
            cur.execute("UPDATE recursos SET asignado = TRUE, longitud= %s, latitud = %s WHERE recurso_id = %s;", (emergencia["lon"], emergencia["lat"], vehiculo["recurso_id"]))
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            logging.error(f"Error al actualizar la ubicación para recurso_id {vehiculo["recurso_id"]}: {e}")

class LiberarRecurso(beam.DoFn):
    from apache_beam.coders import StrUtf8Coder
    from apache_beam.transforms.timeutil import TimeDomain
    import typing
    import apache_beam.transforms.userstate as beam_state
    from apache_beam import coders

    TEST_STATE = beam_state.BagStateSpec('test_events', coders.StrUtf8Coder())        
    TIMER = beam_state.TimerSpec('timer', beam_state.TimeDomain.REAL_TIME)

    def process(self,
                element: typing.Tuple[int, datetime],
                stored_test_state=beam.DoFn.StateParam(TEST_STATE),
                timer = beam.DoFn.TimerParam(TIMER)):
        recurso_id, tiempo = element
        stored_test_state.add(str(recurso_id))
        tiempo_float=tiempo.timestamp()
        timer.set(tiempo_float)
        logging.info(f"Recurso_id {recurso_id} almacenado para liberar en {tiempo}")

    @beam_state.on_timer(TIMER)
    def expiry(self, buffer = beam.DoFn.StateParam(TEST_STATE), timer = beam.DoFn.TimerParam(TIMER)):
        vehiculos_ids = list(buffer.read())
        for vehiculo_id in vehiculos_ids:
            self.liberar_recurso(int(vehiculo_id))
        buffer.clear()
        timer.clear()



    def liberar_recurso(self, vehiculo_id: str):
        try:
            connector = Connector()
            conn = connector.connect(
                "splendid-strand-452918-e6:europe-southwest1:recursos",
                "pg8000",
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                db=DB_CONFIG['dbname'],
            )
            logging.info(f"Recurso_id {vehiculo_id} liberado")
            cur = conn.cursor()
            cur.execute("UPDATE recursos SET asignado = FALSE WHERE recurso_id = %s;", (vehiculo_id,))
            conn.commit() 
            cur.close()
            conn.close()
        except Exception as e:
            logging.error(f"Error al liberar el recurso_id {vehiculo_id}: {e}")


def run():
    with beam.Pipeline(options=PipelineOptions(streaming=True, save_main_session=True)) as p:
        fixed_window = beam.window.FixedWindows(90)
        
        emergencia_nueva = (
            p 
            | "ReadFromPubSubEvent1" >> beam.io.ReadFromPubSub(subscription=f'projects/splendid-strand-452918-e6/subscriptions/emergencias_events2-sub')
            
        )
       
        no_match= (
            p
            | "ReadFromPubSubEvent3" >> beam.io.ReadFromPubSub(subscription=f'projects/splendid-strand-452918-e6/subscriptions/no_matched2-sub')
        )

        eventos_emergencias = (
            (emergencia_nueva, no_match)
            | "Flatten Emergencias" >> beam.Flatten()
            | "Filter Null Emergencias" >> beam.Filter(lambda x: x is not None) 
            | "Decode + Timestamp Emergencias" >> beam.Map(decode_and_timestamp_event)
            # | "Combine 1" >> beam.Map(lambda x: (x['servicio'], x))
            | "Fixed Window 1" >> beam.WindowInto(fixed_window)
            )

           
        

        eventos_vehiculo = ( 
            p 
            | "ReadFromPubSubEvent2" >> beam.io.ReadFromPubSub(subscription=f'projects/splendid-strand-452918-e6/subscriptions/emergencias_ubi_autos2-sub')
            | "Filter Null vehículos" >> beam.Filter(lambda x: x is not None)
            | "Decode + Timestamp Vehículos" >> beam.Map(decode_and_timestamp_vehicle)
            # | "Combine 2" >> beam.Map(lambda x: (x['servicio'], x))
            | "Fixed Window 2" >> beam.WindowInto(fixed_window)

        )

        # eventos_vehiculo | "Print Vehiculos" >> beam.Map(lambda x: logging.info(f"Vehiculo: {x}"))
        # eventos_emergencias | "Print Emergencias" >> beam.Map(lambda x: logging.info(f"Emergencia: {x}"))

        grouped_data = ((eventos_emergencias, eventos_vehiculo) 
                        | "Agrupacion PCollections" >> beam.CoGroupByKey()
                        )
        # grouped_data | "Print Grouped Data" >> beam.Map(lambda x: logging.info(f"Grouped Data: {x}"))
                          
        processed_data = (grouped_data
            | "Calcular Coef y partir en 3 pcollections" >> beam.ParDo(CalcularCoeficiente()).with_outputs("Bomberos", "Policia", "Ambulancia"))

        bomberos = processed_data.Bomberos
        # bomberos | "Print Bomberos" >> beam.Map(lambda x: logging.info(f"Bomberos: {x}"))
        policias = processed_data.Policia
        # policias | "Print Policias" >> beam.Map(lambda x: logging.info(f"Policias: {x}"))
        ambulancias = processed_data.Ambulancia
        # ambulancias | "Print Ambulancias" >> beam.Map(lambda x: logging.info(f"Ambulancias: {x}"))
        

        asignacion_bomb = (
            bomberos
            | "Asignación de Bomberos" >> beam.ParDo(Asignacion()).with_outputs("Match", "NoMatch")
            )
        asignacion_pol = (
            policias
            | "Asignación de Policias" >> beam.ParDo(Asignacion()).with_outputs("Match", "NoMatch")
            )
        asignacion_amb = (
            ambulancias
            | "Asignación de Ambulancias" >> beam.ParDo(Asignacion()).with_outputs("Match", "NoMatch")
            )

        all_no_matches = (
                (asignacion_bomb.NoMatch, asignacion_pol.NoMatch, asignacion_amb.NoMatch)
                | "Flatten No Matches" >> beam.Flatten()
                | "Times no_matched" >> beam.Map(incrementar_no_matched)
                | "Encode No Matches" >> beam.Map(encode_message)
            )

        all_no_matches | "Enviar a Topic de Reintento" >> beam.io.WriteToPubSub(topic="projects/splendid-strand-452918-e6/topics/no_matched2")
        all_no_matches | "Print No Matches" >> beam.Map(lambda x: logging.info(f"No Match: {x}"))

        all_matches = (
                (asignacion_bomb.Match, asignacion_pol.Match, asignacion_amb.Match)
                | "Flatten Matches" >> beam.Flatten()
            )
        all_matches | "print matches" >> beam.Map(lambda x: logging.info(f"Match: {x}"))
        all_matches | "Asignar recurso" >> beam.ParDo(ActualizarSQL())


        formatear_match = all_matches | "Formatear a BQ" >> beam.Map(lambda x: formatear_para_bigquery_matched(*x))
        formatear_match | "Write to BigQuery" >> beam.io.WriteToBigQuery(
                table=f"splendid-strand-452918-e6:emergencia_eventos.emergencias-macheadas",
                schema= (
                        "recurso_id:STRING,"
                        "servicio_recurso:STRING,"
                        "lat_recurso:FLOAT,"
                        "lon_recurso:FLOAT,"
                        "timestamp_ubicacion:TIMESTAMP,"
                        "evento_id:STRING,"
                        "timestamp_evento:TIMESTAMP,"
                        "servicio_evento:STRING,"
                        "tipo:STRING,"
                        "descapacidad:STRING,"
                        "nivel_emergencia:STRING,"
                        "lat_evento:FLOAT,"
                        "lon_evento:FLOAT,"
                        "coeficiente_seleccionado:FLOAT,"
                        "tiempo_total:FLOAT,"
                        "tiempo_respuesta:FLOAT,"
                        "distancia_recorrida:FLOAT,"
                        "disponible_en:TIMESTAMP"
                ),
                    
                
                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND
            )
        
        # formatear_no_match = all_no_matches | "Formatear a BQ" >> beam.Map(lambda x: formatear_para_bigquery_no_matched(*x))
        # formatear_no_match | "Write to BigQuery" >> beam.io.WriteToBigQuery(
        #         table=f"splendid-strand-452918-e6:emergencia_eventos.emergencias-no-macheadas",
        #         schema= {
        #             "fields": [
        #                 {"name": "evento_id", "type": "STRING", "mode": "REQUIRED"},
        #                 {"name": "timestamp_evento", "type": "TIMESTAMP", "mode": "REQUIRED"},
        #                 {"name": "servicio", "type": "STRING", "mode": "REQUIRED"},
        #                 {"name": "tipo", "type": "STRING", "mode": "REQUIRED"},
        #                 {"name": "discapacidad", "type": "STRING", "mode": "REQUIRED"},
        #                 {"name": "nivel_emergencia", "type": "STRING", "mode": "REQUIRED"},
        #                 {"name": "lat", "type": "FLOAT", "mode": "REQUIRED"},
        #                 {"name": "lon", "type": "FLOAT", "mode": "REQUIRED"},
        #                 {"name": "edad", "type": "INTEGER", "mode": "REQUIRED"},
        #                 {"name": "coeficientes", "type": "FLOAT", "mode": "REPEATED"},
        #                 {"name": "no_matched_count", "type": "INTEGER", "mode": "REQUIRED"},
        #             ]
        #         },
                    
                
        #         create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
        #         write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND
        #     )
        

        matches_clave = all_matches | "Con clave" >> beam.Map(lambda x: (x[0]["recurso_id"], x[1]["disponible_en"]))
        matches_clave | "Liberar tras tiempo" >> beam.ParDo(LiberarRecurso())



run()