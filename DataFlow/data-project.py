import apache_beam as beam
from datetime import datetime
from apache_beam.runners.interactive.interactive_runner import InteractiveRunner
import apache_beam.runners.interactive.interactive_beam as ib
from apache_beam.options.pipeline_options import PipelineOptions
import json
from google.cloud.sql.connector import Connector

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

class CalcularCoeficiente(beam.DoFn):
    def process(self, mensaje):
        import random
        if mensaje is None:
            return
        clave, (emergencias, vehiculos) = mensaje
        for i, emergencia in enumerate(emergencias):
            coeficinetes_lista = []
            for vehiculo in vehiculos:
                coficiente = random.random()
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
        match_list_emergencias_id=[]
        match_list_vehiculos_id=[]
        # if emergencias and vehiculos:
        #     numero_posiciones=len(emergencias[0]["coeficientes"])
        #     for i in range(numero_posiciones):
        #         candidatos = [] 
        #         for emergencia in emergencias:
        #             if emergencia["evento_id"] not in match_list_id:
        #                 candidatos.append(emergencia)
                # if candidatos:
                #     match_evento = max(candidatos, key=lambda x: x["coeficientes"][i])
                #     match_evento["coeficiente_seleccionado"] = match_evento["coeficientes"][i]
                #     match_list_id.append(match_evento["evento_id"])
                #     yield beam.pvalue.TaggedOutput("Match", (vehiculos[i], match_evento))
        while True:
            max_total=0
            indice_max=0
            i_max=0
            recursos_disp=[]
            candidatos = []
            for emergencia in emergencias:
                if emergencia["evento_id"] not in match_list_emergencias_id:
                    candidatos.append(emergencia)
            for vehiculo in vehiculos:
                if vehiculo["recurso_id"] not in match_list_vehiculos_id:
                    recursos_disp.append(vehiculo)
            if not candidatos or not recursos_disp:
                break
            for i, emergencia in enumerate(candidatos):
                max_list=max(emergencia["coeficientes"])
                indice=emergencia["coeficientes"].index(max_list)
                if max_total < max_list and vehiculos[indice] in recursos_disp:
                    max_total=max_list
                    indice_max=indice
                    i_max=i
            match_evento=emergencias[i_max]
            match_evento["coeficiente_seleccionado"] = max_total
            match_list_emergencias_id.append(match_evento["evento_id"])
            match_list_vehiculos_id.append(vehiculos[indice_max]["recurso_id"])
            yield beam.pvalue.TaggedOutput("Match", (vehiculos[indice_max], match_evento))
                     
        for emergencia in emergencias:
            if emergencia["evento_id"] not in match_list_emergencias_id:
                yield beam.pvalue.TaggedOutput("NoMatch", (emergencia))

class ActualizarUbicacion(beam.DoFn):
    def process(self, recurso):

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
            cur.execute("UPDATE recursos SET asignado = TRUE WHERE recurso_id = %s;", (recurso["recurso_id"],))
            cur.execute("UPDATE recursos SET longitud = %s WHERE recurso_id = %s;", (recurso["lon"], recurso["recurso_id"],))
            cur.execute("UPDATE recursos SET latitud = %s WHERE recurso_id = %s;", (recurso["lat"], recurso["recurso_id"],))
            cur.close()
            conn.close()
        except Exception as e:
            logging.error(f"Error al actualizar la ubicación para recurso_id {recurso["recurso_id"]}: {e}")
        

def run():
    with beam.Pipeline(options=PipelineOptions(streaming=True, save_main_session=True)) as p:
        fixed_window = beam.window.FixedWindows(60)
        
        emergencia_nueva = (
            p 
            | "ReadFromPubSubEvent1" >> beam.io.ReadFromPubSub(subscription=f'projects/splendid-strand-452918-e6/subscriptions/emergencias_events-sub'
            
        ))
       
        no_match= (
            p
            | "ReadFromPubSubEvent3" >> beam.io.ReadFromPubSub(subscription=f'projects/splendid-strand-452918-e6/subscriptions/no_matched-sub')
            | "Print Emergencias" >> beam.Map(lambda x: logging.info(f"No match Emergencia: {x}"))
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
            | "ReadFromPubSubEvent2" >> beam.io.ReadFromPubSub(subscription=f'projects/splendid-strand-452918-e6/subscriptions/emergencias_ubi_autos-sub')
            | "Filter Null vehículos" >> beam.Filter(lambda x: x is not None)
            | "Decode + Timestamp Vehículos" >> beam.Map(decode_and_timestamp_vehicle)
            # | "Combine 2" >> beam.Map(lambda x: (x['servicio'], x))
            | "Fixed Window 2" >> beam.WindowInto(fixed_window)

        )

        # eventos_emergencias | "Print Emergencias" >> beam.Map(lambda x: logging.info(f"Emergencia: {x}"))
        # eventos_vehiculo | "Print Vehiculos" >> beam.Map(lambda x: logging.info(f"Vehiculo: {x}"))
        grouped_data = ((eventos_emergencias, eventos_vehiculo) 
                        | "Agrupacion PCollections" >> beam.CoGroupByKey()
                        )
                          
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
                | "Encode No Matches" >> beam.Map(encode_message)
            )

        all_no_matches | "Enviar a Topic de Reintento" >> beam.io.WriteToPubSub(topic="projects/splendid-strand-452918-e6/topics/no_matched")
        all_no_matches | "Print No Matches" >> beam.Map(lambda x: logging.info(f"No Match: {x}"))

        all_matches = (
                (asignacion_bomb.Match, asignacion_pol.Match, asignacion_amb.Match)
                | "Flatten Matches" >> beam.Flatten()
            )
        all_matches | "print matches" >> beam.Map(lambda x: logging.info(f"Match: {x}"))
        # all_matches | "Write to BigQuery" >> beam.io.WriteToBigQuery(
        #         table=f"{project_id}:{dataset_id}.{table_id}",
        #         schema= (
        #                 "servicio:STRING,"
        #                 "tipo:STRING,"
        #                 "discapacidad:STRING,"
        #                 "nivel_emergencia:STRING,"
        #                 "lat:STRING,"
        #                 "lon:STRING"
        #         ),
                    
                
        #         create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
        #         write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND
        #     )
        
        recurso_ids = all_matches | "Obtener emergencia match" >> beam.Map(lambda x: x[0])
        recurso_ids | "Actualizar asignado" >> beam.ParDo(ActualizarUbicacion())


run()