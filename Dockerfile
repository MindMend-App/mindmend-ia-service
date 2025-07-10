# 1) Imagen base ligera
FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# 2) Copiamos solo requirements
COPY requirements.txt .

# 3) Primero instalamos torch CPU-only
RUN pip install --no-cache-dir \
      torch==2.7.1+cpu \
      -f https://download.pytorch.org/whl/cpu/torch_stable.html

# 4) Luego el resto de dependencias
RUN pip install --no-cache-dir -r requirements.txt

# 5) Copiamos el resto de la app
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
