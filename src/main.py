# src/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.database.connection import init_db
from src.core.logging_config import logger
from src.api.endpoints.tickets import router as tickets_router
from src.api.endpoints.auth import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("Base de datos inicializada correctamente.")
    yield
    logger.info("Apagando aplicación...")

app = FastAPI(
    title="Corporate Ticket Triage API", 
    version="1.0.0",
    lifespan=lifespan
)

# Incluir las rutas
app.include_router(tickets_router)
app.include_router(auth_router)