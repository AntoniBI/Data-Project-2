import apache_beam as beam
from datetime import datetime
from apache_beam.runners.interactive.interactive_runner import InteractiveRunner
import apache_beam.runners.interactive.interactive_beam as ib
from apache_beam.options.pipeline_options import PipelineOptions
import json

# Set Logs

import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")

# Suppress Apache Beam logs
logging.getLogger("apache_beam").setLevel(logging.WARNING)

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
        id_asignados = set()
        if emergencias and vehiculos:
            print(emergencias)
            numero_posiciones=len(emergencias[0]["coeficientes"])
            for emergencia in emergencias:
                for i in range(numero_posiciones):
                    match_evento = max(emergencias, key=lambda x: x["coeficientes"][i])
                    match_evento["coeficiente_seleccionado"] = match_evento["coeficientes"][i]
                    match_evento.pop("coeficientes", None)
                    yield beam.pvalue.TaggedOutput("Match", (vehiculos[i], match_evento))
                    id_asignados.add(id(match_evento))
                
                if id(emergencia) not in id_asignados:
                    yield beam.pvalue.TaggedOutput("NoMatch", (emergencia))

def run():
    with beam.Pipeline(options=PipelineOptions(streaming=True, save_main_session=True)) as p:
        fixed_window = beam.window.FixedWindows(60)
        
        emergencia_nueva = (
            p 
            | "ReadFromPubSubEvent1" >> beam.io.ReadFromPubSub(subscription=f'projects/splendid-strand-452918-e6/subscriptions/emergencias_events-sub')
            
        )
       
        no_match= (
            p
            | "ReadFromPubSubEvent3" >> beam.io.ReadFromPubSub(subscription=f'projects/splendid-strand-452918-e6/subscriptions/no_matched-sub')
        )

        eventos_emergencias = (
            (emergencia_nueva, no_match)
            | "Flatten Emergencias" >> beam.Flatten()
            | "Decode + Timestamp Emergencias" >> beam.Map(decode_and_timestamp_event)
            # | "Combine 1" >> beam.Map(lambda x: (x['servicio'], x))
            | "Map to Key-Value Emergencias" >> beam.Map(lambda x: (x[0], x[1]))
            | "Filter Null Emergencias" >> beam.Filter(lambda x: x[0] or x[1] is not None) 
            | "Fixed Window 1" >> beam.WindowInto(fixed_window)
            )
            
           
        

        eventos_vehiculo = ( 
            p 
            | "ReadFromPubSubEvent2" >> beam.io.ReadFromPubSub(subscription=f'projects/splendid-strand-452918-e6/subscriptions/emergencias_ubi_autos-sub')
            | "Decode + Timestamp Vehículos" >> beam.Map(decode_and_timestamp_vehicle)
            # | "Combine 2" >> beam.Map(lambda x: (x['servicio'], x))
            | "Map to Key-Value vehiculos" >> beam.Map(lambda x: (x[0], x[1]))
            | "Filter Null vehículos" >> beam.Filter(lambda x: x[0] or x[1] is not None)
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

        # all_no_matches = (
        #         (asignacion_bomb.NoMatch, asignacion_pol.NoMatch, asignacion_amb.NoMatch)
        #         | "Flatten No Matches" >> beam.Flatten()
        #     )

        # all_no_matches | "Enviar a Topic de Reintento" >> beam.io.WriteToPubSub(topic="projects/splendid-strand-452918-e6/topics/no_matched")

        all_matches = (
                (asignacion_bomb.Match, asignacion_pol.Match, asignacion_amb.Match)
                | "Flatten Matches" >> beam.Flatten()
            )
        
        all_matches | "Print Matches" >> beam.Map(lambda x: logging.info(f"Match: {x}"))
       # Escribir en BigQuery los all matches. Pensar que hacer con los no matches.

run()