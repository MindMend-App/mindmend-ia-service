# 1) Base ligera
FROM python:3.12-slim

# 2) Directorio de trabajo
WORKDIR /app

# 3) Copiamos sólo requirements
COPY requirements.txt .

# 4) Instalamos torch-CPU + resto de deps
RUN pip install --no-cache-dir \
      torch==2.7.1+cpu \
      -f https://download.pytorch.org/whl/cpu/torch_stable.html \
    && pip install --no-cache-dir -r requirements.txt

# 5) Copiamos el código
COPY . .

# 6) Exponemos el puerto
EXPOSE 8000

# 7) Comando de arranque, usa la variable $PORT de Railway
ENTRYPOINT ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
