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

    logging.info("New PubSub Message: %s", output)

    return json.loads(output)

def run():
    with beam.Pipeline(options=PipelineOptions(streaming=True, save_main_session=True)) as p:
        
        evenetos_emergencias = (
            p 
            | "ReadFromPubSubEvent1" >> beam.io.ReadFromPubSub(subscription=f'projects/splendid-strand-452918-e6/subscriptions/emergencias_events-sub')
            | "Decode msg 1" >> beam.Map(decode_message)
            | "Combine" >> beam.Map(lambda x: (x['servicio'], x))
            | "Fixed Window" >> beam.WindowInto(beam.window.FixedWindows(10))
            
        )

        # evenetos_vehiculo = ( 
        #     p 
        #     | "ReadFromPubSubEvent2" >> beam.io.ReadFromPubSub(subscription=f'projects/splendid-strand-452918-e6/subscriptions/emergencias_events-sub')
        #     | "Decode msg 2" >> beam.Map(decode_message)
        #     | "Combine" >> beam.Map(lambda x: (x['servicio'], x))
        #     | "Fixed Window" >> beam.WindowInto(beam.window.FixedWindows(10))
        #     
        # )
    filtro_servicio = ((evenetos_emergencias, eventos_vehiculo) | beam.CoGroupByKey())
       
logging.info("The process started")
run()