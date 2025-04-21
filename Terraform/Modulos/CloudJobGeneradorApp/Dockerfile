FROM python:3.10-slim

WORKDIR /app

COPY events-generator.py .
COPY requirements.txt .

RUN pip install -r requirements.txt

RUN chmod +x events-generator.py

# Comando para ejecutar el script
CMD ["python3", "events-generator.py"]