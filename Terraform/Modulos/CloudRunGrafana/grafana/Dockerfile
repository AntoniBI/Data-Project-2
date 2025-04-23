FROM grafana/grafana:latest

USER root

# Instalar el plugin oficial de BigQuery
RUN grafana-cli plugins install grafana-bigquery-datasource

# Copiar configuración de provisioning
COPY provisioning /etc/grafana/provisioning

