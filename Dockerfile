# 1. Imagen base ligera
FROM python:3.12-slim

# 2. No queremos prompts de instalación
ENV DEBIAN_FRONTEND=noninteractive

# 3. Directorio de trabajo
WORKDIR /app

# 4. Copia solo lo necesario
COPY requirements.txt .

# 5. Instalamos sin cache
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copiamos el resto de la app
COPY . .

# 7. Exponemos el puerto que usa Uvicorn
EXPOSE 8000

# 8. Comando de arranque
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
