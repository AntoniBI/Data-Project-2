# Usar una imagen base de Python
FROM python:3.10-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar el archivo de requisitos (si existe) y el script de Streamlit
COPY requirements.txt ./
COPY emergencia_app.py ./

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt 

EXPOSE 8502

# Comando para ejecutar Streamlit
CMD ["streamlit", "run", "emergencia_app.py", "--server.port=8502", "--server.address=0.0.0.0"]




