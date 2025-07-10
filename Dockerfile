# Dockerfile
FROM python:3.12-slim

# Evitamos instalar paquetes extras de sistema innecesarios
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiamos solo requisitos y los instalamos
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código después, para cache de Docker
COPY . .

# Exponemos el puerto y arrancamos
ENV PORT 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
