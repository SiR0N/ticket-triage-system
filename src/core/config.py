# src/core/config.py
import os
from dotenv import load_dotenv
from src.models.schemas import DepartmentEnum, ProviderEnum, UrgencyEnum

load_dotenv()

# API Backend & Auth
API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")
SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_key_change_me")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# Opciones para la UI (Reflex)
PROVIDER_OPTIONS = [p.value if hasattr(p, "value") else str(p) for p in ProviderEnum]
DEPT_OPTIONS = [d.value if hasattr(d, "value") else str(d) for d in DepartmentEnum]
URGENCY_OPTIONS = [u.value if hasattr(u, "value") else str(u) for u in UrgencyEnum]

# --- PROVEEDORES Y MODELOS DE IA ---
# Modelos Locales
MODEL_OLLAMA = os.getenv("MODEL_OLLAMA", "qwen2.5-coder:1.5b")
MODEL_HF_LOCAL = os.getenv("MODEL_HF_LOCAL", "Qwen/Qwen2.5-0.5B-Instruct")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Modelos en la Nube
MODEL_GEMINI = os.getenv("MODEL_GEMINI", "gemini-2.5-flash")
MODEL_HF_API = os.getenv("MODEL_HF_API", "Qwen/Qwen2.5-Coder-32B-Instruct")

# Credenciales de API (AQUÍ ESTÁ LA VARIABLE FALTANTE)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
HF_TOKEN = os.getenv("HF_TOKEN", "")