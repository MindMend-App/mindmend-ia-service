# 1) Usa Python 3.11-slim para que pip encuentre el wheel cpu-only
FROM python:3.11-slim

WORKDIR /app

# 2) Copiamos sólo requirements.txt para cachear bien
COPY requirements.txt .

# 3) Instalamos primero torch cpu-only (compatible con py3.11)
RUN pip install --no-cache-dir \
      torch==2.7.1+cpu \
      -f https://download.pytorch.org/whl/cpu/torch_stable.html

# 4) Luego el resto de dependencias
RUN pip install --no-cache-dir -r requirements.txt

# 5) Copiamos el código de la app
COPY . .

EXPOSE 8000

# 6) Arranque leyendo $PORT que pone Railway
ENTRYPOINT ["sh","-c","uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
