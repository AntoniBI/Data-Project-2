import apache_beam as beam
from datetime import datetime, timedelta, timezone
from apache_beam.runners.interactive.interactive_runner import InteractiveRunner
import apache_beam.runners.interactive.interactive_beam as ib
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
import json
import math
from google.cloud.sql.connector import Connector
import time
from zoneinfo import ZoneInfo
import argparse
from apache_beam.coders import StrUtf8Coder
from apache_beam.transforms.timeutil import TimeDomain
import typing
import apache_beam.transforms.userstate as beam_state
from apache_beam import coders
import pytz


"""FALTEN ELS REQUIREMENTS Y CAMBIAR ELS TOPICS DE PUBSUB
APART DE FER MILLOR EL CÓDIG EN VARIABLES DE ENTORNO"""
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

def incrementar_no_matched(evento):
    evento['no_matched_count'] = evento.get('no_matched_count', 0) + 1

    return evento


def decode_and_timestamp_event(msg):
    data = decode_message(msg)
    logging.info(f"Mensaje decodificado emergencia: {data}")
    return (data['servicio'], data)


def decode_and_timestamp_vehicle(msg):
    data = decode_message(msg)
    logging.info(f"Mensaje decodificado vehiculo: {data}")
    return (data['servicio'], data)
    

def decode_message(msg):

    output = msg.decode('utf-8')

    return json.loads(output)

def encode_message(obj):
    def convert_datetime(o):
        if isinstance(o, datetime):
            return o.isoformat()
        raise TypeError(f'Object of type {o.__class__.__name__} is not JSON serializable')
    return json.dumps(obj, default=convert_datetime).encode("utf-8")

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
        tiempo_total= 1
    elif nivel_emergencia == "Nivel 3: Emergencia grave":
        nivel_score= 0.8
        tiempo_total= 1

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
    logging.info(f"Mensaje para formatear y enviar a BQ match: {vehiculo} {evento}")
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
        "edad": evento.get("edad"),
        "discapacidad": evento["discapacidad"],
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
    logging.info(f"Mensaje para formatear y enviar a BQ no match: {mensaje}")
    return {
        "evento_id": mensaje["evento_id"],
        "timestamp_evento": datetime.strptime(mensaje["timestamp_evento"], "%Y-%m-%d %H:%M:%S").isoformat(),
        "servicio_evento": mensaje["servicio"],
        "tipo": mensaje["tipo"],
        "edad": mensaje.get("edad"),
        "discapacidad": mensaje["discapacidad"],
        "nivel_emergencia": mensaje["nivel_emergencia"],
        "lat_evento": mensaje["lat"],
        "lon_evento": mensaje["lon"],
        "coeficientes": mensaje["coeficientes"],
        "no_matched_count": mensaje["no_matched_count"]

    }


class BussinesLogic(beam.DoFn):
    @staticmethod
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
    
    @staticmethod
    def asignar_vehiculo(vehiculos, emergencias):
        match_list_emergencias_id = []
        match_list_vehiculos_id = []
        asignaciones = []

        while True:
            max_total = -1
            match_evento = None
            mejor_vehiculo = None

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

            if match_evento is None or mejor_vehiculo is None:
                break

            # Añadir información al match
            match_evento["coeficiente_seleccionado"] = max_total
            tiempo_dist = calculo_coeficiente(mejor_vehiculo, match_evento)
            match_evento["tiempo_total"] = tiempo_dist[2]
            match_evento["tiempo_respuesta"] = tiempo_dist[1]
            match_evento["distancia_recorrida"] = tiempo_dist[3]
            match_evento["disponible_en"] = datetime.now() + timedelta(minutes=match_evento["tiempo_total"])

            match_list_emergencias_id.append(match_evento["evento_id"])
            match_list_vehiculos_id.append(mejor_vehiculo["recurso_id"])
            asignaciones.append((mejor_vehiculo, match_evento))

        for asignacion in asignaciones:
            yield asignacion

        for emergencia in emergencias:
            if emergencia["evento_id"] not in match_list_emergencias_id:
                yield emergencia


    def process(self, mensaje):
        """
        Calculo de coeficientes y asignacion de vehiculos a emergencias
        """
        if mensaje is None:
            return
        clave, (emergencias_nuevas, vehiculos, no_matched) = mensaje
        emergencias = emergencias_nuevas + (no_matched or [])
        for i, emergencia in enumerate(emergencias):
            coeficinetes_lista = []
            for vehiculo in vehiculos:
                coficiente = self.calculo_coeficiente(vehiculo, emergencia)[0]
                coeficinetes_lista.append(coficiente)
            emergencia["coeficientes"]=coeficinetes_lista
        
        asignaciones = list(self.asignar_vehiculo(vehiculos, emergencias))

        for asignacion in asignaciones:
            if isinstance(asignacion, tuple):
                logging.info(f"Asignando vehiculo {asignacion[0]['recurso_id']} a emergencia {asignacion[1]['evento_id']}")
                yield beam.pvalue.TaggedOutput("Match", asignacion)
            elif isinstance(asignacion, dict):
                asignacion["no_matched_count"] = len(vehiculos)
                yield beam.pvalue.TaggedOutput("NoMatch", asignacion)


class ActualizarSQL(beam.DoFn):

    def __init__(self, project_id, table_sql):
        self.mode = "europe-southwest1"
        self.project_id = project_id
        self.table_sql = table_sql

    def setup(self):
        connector = Connector()
        conn = connector.connect(
            f"{self.project_id}:{self.mode}:{self.table_sql}",
            "pg8000",
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            db=DB_CONFIG['dbname'],
        )
        logging.info(f"Conectado a la base de datos {self.table_sql} en {self.project_id}")
        return conn
                    
    def process(self, match):
        vehiculo, emergencia = match
        try:
            conn= self.setup()
            cur = conn.cursor()
            cur.execute("UPDATE recursos SET asignado = TRUE, longitud= %s, latitud = %s WHERE recurso_id = %s;", (emergencia["lon"], emergencia["lat"], vehiculo["recurso_id"]))
            logging.info(f"Vehiculo {vehiculo['recurso_id']} actualizado en la base de datos")
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            logging.error(f"Error al actualizar la ubicación para recurso_id {vehiculo["recurso_id"]}: {e}")

class LiberarRecurso(beam.DoFn):

    TEST_STATE = beam_state.BagStateSpec('test_events', coders.StrUtf8Coder())
    TIMER = beam_state.TimerSpec('timer', TimeDomain.REAL_TIME)

    def __init__(self, project_id, table_sql):
        self.zone = "europe-southwest1"
        self.project_id = project_id
        self.table_sql = table_sql

    def setup(self):
        connector = Connector()
        conn = connector.connect(
            f"{self.project_id}:{self.zone}:{self.table_sql}",
            "pg8000",
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            db=DB_CONFIG['dbname'],
        )
        logging.info(f"Conectado a la base de datos para liberar {self.table_sql} en {self.project_id}")
        return conn
        
        

    def process(self,
                element: typing.Tuple[int, datetime],
                stored_test_state=beam.DoFn.StateParam(TEST_STATE),
                timer = beam.DoFn.TimerParam(TIMER)):
        recurso_id, tiempo = element

        stored_test_state.add(str(recurso_id))
        tiempo_float=tiempo.astimezone(pytz.UTC).timestamp()
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
            conn= self.setup()
            cur = conn.cursor()
            cur.execute("UPDATE recursos SET asignado = FALSE WHERE recurso_id = %s;", (vehiculo_id,))
            logging.info(f"Vehiculo {vehiculo_id} liberado en la base de datos")
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            logging.error(f"Error al liberar el recurso_id {vehiculo_id}: {e}")


def run():
    """ Input Arguments """

    parser = argparse.ArgumentParser(description=('Input arguments for the Dataflow Streaming Pipeline.'))

    parser.add_argument(
                '--project_id',
                required=True,
                help='GCP cloud project name.')
    
    parser.add_argument(
                '--emergency_events_subscription',
                required=True,
                help='PubSub subscription used for reading emergency events data.')
    
    parser.add_argument(
                '--vehicle_subscription',
                required=True,
                help='PubSub subscription used for reading vehicles data.')
    
    parser.add_argument(
                '--big_query_dataset',
                required=True,
                help='The BQ dataset where the tables will be located.')
    
    parser.add_argument(
                '--big_query_table_matched',
                required=True,
                help='The BQ table for the matched data.')
    
    parser.add_argument(
                '--big_query_table_no_matched',
                required=True,
                help='The BQ table for the no matched data.')
    
    parser.add_argument(
                '--no_matched_topic',
                required=False,
                help='PubSub Topic for sending no_match emergencies.')
    
    parser.add_argument(
            '--table_sql',
            required=False,
            help='SQL table where the vehicles are located.')
    
    parser.add_argument(
        '--streamlit_topic',
        required=False,
        help='topic to streamlit')
    

    args, pipeline_opts = parser.parse_known_args()

    options = PipelineOptions(pipeline_opts,
        save_main_session=True, streaming=True, project=args.project_id)

    """Pipeline"""

    with beam.Pipeline(argv=pipeline_opts,options=options) as p:
        fixed_window = beam.window.FixedWindows(90)

        emergencia_nueva = (
            p
            | "ReadFromPubSubEvent1" >> beam.io.ReadFromPubSub(subscription=f'projects/{args.project_id}/subscriptions/{args.emergency_events_subscription}')
            | "Decode + Timestamp Emergencias" >> beam.Map(decode_and_timestamp_event)
            | "Fixed Window 1" >> beam.WindowInto(fixed_window)
        )

        no_match= (
            p
            | "ReadFromPubSubEvent3" >> beam.io.ReadFromPubSub(subscription=f'projects/{args.project_id}/subscriptions/{args.no_matched_topic}-sub')
            | "Decode no_match" >> beam.Map(decode_and_timestamp_event)
            | "Fixed Window 2" >> beam.WindowInto(fixed_window)


        )

        eventos_vehiculo = (
            p
            | "ReadFromPubSubEvent2" >> beam.io.ReadFromPubSub(subscription=f'projects/{args.project_id}/subscriptions/{args.vehicle_subscription}')
            | "Decode + Timestamp Vehículos" >> beam.Map(decode_and_timestamp_vehicle)
            | "Fixed Window 3" >> beam.WindowInto(fixed_window)
        )

        grouped_data = ((no_match, eventos_vehiculo, emergencia_nueva)
                        | "Group PCollections" >> beam.CoGroupByKey()
                        )

        processed_data = (grouped_data
            | "Bussines Logic" >> beam.ParDo(BussinesLogic()).with_outputs("Match", "NoMatch"))

        all_no_matches = (
                (processed_data.NoMatch)
                | "Times no_matched" >> beam.Map(incrementar_no_matched)
            )
        write_no_match = (
            (all_no_matches) 
            | "Encode No Matches" >> beam.Map(encode_message)
            | "Send message to Topic" >> beam.io.WriteToPubSub(topic=f"projects/{args.project_id}/topics/{args.no_matched_topic}")
        )

        write_to_firebase = (
            (processed_data.Match) 
            | "Encode Matches" >> beam.Map(encode_message)
            | "Send message to Topic streamlit" >> beam.io.WriteToPubSub(topic=f"projects/{args.project_id}/topics/{args.streamlit_topic}")
        )

        all_matches = (
                (processed_data.Match)
                | "Update SQL" >> beam.ParDo(ActualizarSQL(project_id=args.project_id, table_sql=args.table_sql))
            )
        
        liberar_recursos = (
            (processed_data.Match) 
            | "Format update SQL" >> beam.Map(lambda x: (x[0]["recurso_id"], x[1]["disponible_en"]))
            | "Update SQL asignado=false" >> beam.ParDo(LiberarRecurso(project_id=args.project_id, table_sql=args.table_sql))
        )

        formatear_match= processed_data.Match | "Format BQ Matches" >> beam.Map(lambda x: formatear_para_bigquery_matched(*x))
        Big_Query_match = (
            (formatear_match) 

            | "Write to BigQuery" >> beam.io.WriteToBigQuery(
                table=f"{args.project_id}:{args.big_query_dataset}.{args.big_query_table_matched}",
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
                        "discapacidad:STRING,"
                        "nivel_emergencia:STRING,"
                        "lat_evento:FLOAT,"
                        "edad:FLOAT,"
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
        )

        formater_no_match= (
            (all_no_matches)
            # | "Decode" >> beam.Map(decode_message)
            | "Format BQ No match" >> beam.Map(lambda x: formatear_para_bigquery_no_matched(x))
        )

        Big_Query_no_match =( 
            (formater_no_match) 
            | "Write to BigQuery no match" >> beam.io.WriteToBigQuery(
                table=f"{args.project_id}:{args.big_query_dataset}.{args.big_query_table_no_matched}",
                schema= (
                        "evento_id:STRING,"
                        "timestamp_evento:TIMESTAMP,"
                        "servicio_evento:STRING,"
                        "tipo:STRING,"
                        "edad:INTEGER,"
                        "discapacidad:STRING,"
                        "nivel_emergencia:STRING,"
                        "lat_evento:FLOAT,"
                        "lon_evento:FLOAT,"
                        "coeficientes:FLOAT REPEATED,"
                        "no_matched_count:INTEGER"
                ),


                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND
            )
        )



if __name__ == '__main__':

    logging.info("The process started")

    run()