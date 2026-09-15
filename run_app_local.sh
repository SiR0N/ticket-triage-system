#!/bin/bash

# Terminar todo el script limpiamente al presionar Ctrl+C o recibir una señal de corte
trap 'echo "🛑 Deteniendo servidores..."; kill $FASTAPI_PID 2>/dev/null; exit' INT TERM EXIT

# Activar el entorno virtual (si existe)
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Añadir la raíz del proyecto al PYTHONPATH (Soluciona los errores de importación en src)
export PYTHONPATH=.

echo "🚀 Iniciando FastAPI en puerto 8000..."
uvicorn src.main:app --reload --port 8000 &
FASTAPI_PID=$!

# Esperar unos segundos a que FastAPI inicialice
echo "⏳ Esperando a que FastAPI esté disponible..."
sleep 3

echo "📊 Iniciando interfaz Reflex (Frontend)..."
cd ticket_triage_ui

# Arrancar Reflex cambiando su puerto interno para evitar conflicto con FastAPI
reflex run --backend-port 8002