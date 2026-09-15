#!/bin/bash

# 1. Iniciar FastAPI en segundo plano (puerto interno 8000)
echo "🚀 Iniciando FastAPI..."
uvicorn src.main:app --host 0.0.0.0 --port 8000 &
FASTAPI_PID=$!

# 2. Esperar a que FastAPI esté listo
sleep 3

# 3. Iniciar Reflex (Frontend) configurado para el puerto 7860 que exige Hugging Face
echo "📊 Iniciando interfaz Reflex en puerto 7860..."
cd ticket_triage_ui

# Ejecutar reflex especificando el puerto principal 7860
reflex run --env prod --port 7860 --backend-port 8002 &
REFLEX_PID=$!

# Mantener el contenedor vivo esperando a los procesos
wait $FASTAPI_PID $REFLEX_PID