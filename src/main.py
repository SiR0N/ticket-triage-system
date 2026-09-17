# src/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
import requests

from src.database.connection import init_db
from src.core.logging_config import logger
from src.api.endpoints.tickets import router as tickets_router
from src.api.endpoints.auth import router as auth_router
from src.core.config import (
    GEMINI_API_KEY,
    HF_TOKEN,
    MODEL_GEMINI,
    MODEL_HF_API,
    MODEL_HF_LOCAL,
    MODEL_OLLAMA,
    OLLAMA_BASE_URL,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Inicializar la Base de Datos
    init_db()
    logger.info("💾 Base de datos inicializada correctamente.")

    # 2. Validar Credenciales de APIs Externas
    if GEMINI_API_KEY:
        logger.info(f"🔑 Gemini API Key configurada para modelo: {MODEL_GEMINI}")
    else:
        logger.warning("⚠️ GEMINI_API_KEY no detectada. Las solicitudes con Gemini fallarán.")

    if HF_TOKEN:
        logger.info(f"🔑 HF Token configurado para modelo API: {MODEL_HF_API}")
    else:
        logger.warning("⚠️ HF_TOKEN no detectado. Las solicitudes con HuggingFace API fallarán.")

    # 3. Comprobar Conectividad con Ollama Local
    try:
        res = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
        if res.status_code == 200:
            logger.info(f"🦙 Ollama local activo en {OLLAMA_BASE_URL} (Modelo configurado: {MODEL_OLLAMA})")
    except Exception:
        logger.warning(f"⚠️ No se pudo conectar con Ollama en {OLLAMA_BASE_URL}. Asegúrate de ejecutar `ollama serve`.")

    logger.info(f"🤗 Modelo HF Local configurado: {MODEL_HF_LOCAL}")
    logger.info("🚀 Aplicación iniciada con éxito.")

    yield

    logger.info("🛑 Apagando aplicación...")


app = FastAPI(
    title="Corporate Ticket Triage API",
    version="1.0.0",
    lifespan=lifespan,
)

# Incluir las rutas
app.include_router(tickets_router)
app.include_router(auth_router)