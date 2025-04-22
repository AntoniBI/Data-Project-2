import apache_beam as beam

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

def decode_message(msg):

    output = msg.decode('utf-8')

    return json.loads(output)

class CalcularCoeficiente(beam.DoFn):
    def process(self, mensaje):
        import random
        clave, (vehiculos, emergencias) = mensaje

        for emergencia in emergencias:
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
            numero_posiciones=len(emergencias[0]["coeficientes"])
            for emergencia in emergencias:
                for i in range(numero_posiciones):
                    match_evento = max(emergencias, key=lambda x: x["coeficientes"][i])
                    yield beam.pvalue.TaggedOutput("Match", (vehiculos[i], match_evento))
                    id_asignados.add(id(match_evento))
                
                if id(emergencia) not in id_asignados:
                    yield beam.pvalue.TaggedOutput("No Match", (emergencia))

def run():
    with beam.Pipeline(options=PipelineOptions(streaming=True, save_main_session=True)) as p:
        
        emergencia_nueva = (
            p 
            | "ReadFromPubSubEvent1" >> beam.io.ReadFromPubSub(subscription=f'projects/splendid-strand-452918-e6/subscriptions/emergencias_events-sub')
            
        )

        no_match= (
            p
            | "ReadFromPubSubEvent3" >> beam.io.ReadFromPubSub(subscription=f'projects/splendid-strand-452918-e6/subscriptions/no_matched-sub')
        )

        evenetos_emergencias = (
            (emergencia_nueva, no_match)
            | "Flatten Emergencias" >> beam.Flatten()
            | "Decode msg 1" >> beam.Map(decode_message)
            | "Combine 1" >> beam.Map(lambda x: (x['servicio'], x))
            | "Filter Null Emergencias" >> beam.Filter(lambda x: x is not None)
            | "Fixed Window 1" >> beam.WindowInto(beam.window.SlidingWindows(60, 10))
        )

        eventos_vehiculo = ( 
            p 
            | "ReadFromPubSubEvent2" >> beam.io.ReadFromPubSub(subscription=f'projects/splendid-strand-452918-e6/subscriptions/emergencias_ubi_autos-sub')
            | "Decode msg 2" >> beam.Map(decode_message)
            | "Combine 2" >> beam.Map(lambda x: (x['servicio'], x))
            | "Filter Null vehículos" >> beam.Filter(lambda x: x is not None)
            | "Fixed Window 2" >> beam.WindowInto(beam.window.SlidingWindows(60, 10))
            
        )

        grouped_data = (
            eventos_vehiculo, evenetos_emergencias) | "Merge PCollections" >> beam.CoGroupByKey()
        
        
        processed_data = (grouped_data
            | "Calcular Coef y partir en 3 pcollections" >> beam.ParDo(CalcularCoeficiente()).with_outputs("Bomberos", "Policia", "Ambulancia"))
        
        bomberos = processed_data.Bomberos
        policias = processed_data.Policia
        ambulancias = processed_data.Ambulancia

        asignacion_bomb = (
            bomberos
            | "Asignación de Bomberos" >> beam.ParDo(Asignacion()).with_outputs("Match", "No Match")
            )
        asignacion_pol = (
            policias
            | "Asignación de Policias" >> beam.ParDo(Asignacion()).with_outputs("Match", "No Match")
            )
        asignacion_amb = (
            ambulancias
            | "Asignación de Ambulancias" >> beam.ParDo(Asignacion()).with_outputs("Match", "No Match")
            )

        all_no_matches = (
                (asignacion_bomb.NoMatch, asignacion_pol.NoMatch, asignacion_amb.NoMatch)
                | "Flatten No Matches" >> beam.Flatten()
            )

        all_no_matches | "Enviar a Topic de Reintento" >> beam.io.WriteToPubSub(topic="projects/splendid-strand-452918-e6/topics/no_matched")

        all_matches = (
                (asignacion_bomb.Match, asignacion_pol.Match, asignacion_amb.Match)
                | "Flatten Matches" >> beam.Flatten()
            )
        # Escribir en BigQuery los all matches. Pensar que hacer con los no matches.

run()