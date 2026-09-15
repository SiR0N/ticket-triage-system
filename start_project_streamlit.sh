#!/bin/bash

# Terminar todo el script limpiamente al presionar Ctrl+C o recibir una señal de corte
trap 'echo "🛑 Deteniendo servidores..."; kill $FASTAPI_PID 2>/dev/null; exit' INT TERM EXIT

# Activar el entorno virtual (si existe)
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Añadir la raíz del proyecto al PYTHONPATH
export PYTHONPATH=.

echo "🚀 Iniciando FastAPI..."
uvicorn src.main:app --reload &
FASTAPI_PID=$!

# Esperar unos segundos a que FastAPI inicialice la base de datos y los endpoints
echo "⏳ Esperando a que FastAPI esté disponible..."
sleep 3

echo "📊 Iniciando interfaz Streamlit..."
streamlit run dashboard/app.py --server.headless true

# Esperar a que el proceso de Streamlit termine antes de cerrar
wait $FASTAPI_PID