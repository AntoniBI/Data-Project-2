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
        for dict in emergencias:
            dict['coeficiente'] = random.random()

        if clave == "Bomberos":
            yield beam.pvalue.TaggedOutput("Bomberos", (vehiculos, emergencias))
        elif clave == "Policia":
            yield beam.pvalue.TaggedOutput("Policia", (vehiculos, emergencias))
        elif clave == "Ambulancia":
            yield beam.pvalue.TaggedOutput("Ambulancia", (vehiculos, emergencias))

class Asignacion(beam.DoFn):
    def process(self, mensaje):
        vehiculos, emergencias = mensaje
        if emergencias:
            match_evento=max(emergencias, key=lambda x: x['coeficiente'])
            yield beam.pvalue.TaggedOutput("Match", (vehiculos, match_evento))
        

            

def run():
    with beam.Pipeline(options=PipelineOptions(streaming=True, save_main_session=True)) as p:
        
        evenetos_emergencias = (
            p 
            | "ReadFromPubSubEvent1" >> beam.io.ReadFromPubSub(subscription=f'projects/splendid-strand-452918-e6/subscriptions/emergencias_events-sub')
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
        
        # grouped_data | "Imprimir" >> beam.Map(print)
        
        processed_data = (grouped_data
            | "Calcular Coef y partir en 3 pcollections" >> beam.ParDo(CalcularCoeficiente()).with_outputs("Bomberos", "Policia", "Ambulancia"))
        
        bomberos = processed_data.Bomberos
        policias = processed_data.Policia
        ambulancias = processed_data.Ambulancia

        asignacion = (
            bomberos
            | "Asignación de Bomberos" >> beam.ParDo(Asignacion()).with_outputs("Match", "No Match")
            )

        Match = asignacion.Match

        Match | "Imprimir Match" >> beam.Map(print)
        

       

run()