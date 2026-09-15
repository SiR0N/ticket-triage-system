FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código del proyecto
COPY . .

# Dar permisos al script de entrada
RUN chmod +x entrypoint.sh

# Hugging Face Spaces exige obligatoriamente el puerto 7860
EXPOSE 7860

# Ejecutar mediante el script
ENTRYPOINT ["./entrypoint.sh"]