# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# 1) Copiamos sólo requirements.txt
COPY requirements.txt .

# 2) Instalamos torch CPU primero (para que no tire la versión CUDA),
#    y justo después el resto de las deps
RUN pip install --no-cache-dir \
      torch==2.7.1+cpu \
      -f https://download.pytorch.org/whl/cpu/torch_stable.html \
    && pip install --no-cache-dir -r requirements.txt

# 3) Copiamos el resto del código
COPY . .

# 4) Comando de arranque
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
