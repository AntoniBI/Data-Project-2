FROM python:3.10-slim

WORKDIR /app

COPY main.py .
COPY requirements.txt .

RUN pip install -r requirements.txt

RUN chmod +x main.py

CMD ["python3", "main.py"]