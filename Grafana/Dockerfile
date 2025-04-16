FROM grafana:latest

# Instalar el plugin de BigQuery
RUN grafana-cli plugins install marcusolsson-bigquery-datasource

# Copiar la configuración del datasource y dashboards
COPY provisioning /etc/grafana/provisioning

# Copiar credenciales de GCP
COPY credentials/key.json /etc/grafana/credentials/key.json

# Configurar la variable de entorno para las credenciales
ENV GOOGLE_APPLICATION_CREDENTIALS=/etc/grafana/credentials/key.json

# Exponer el puerto 3000
EXPOSE 3000
