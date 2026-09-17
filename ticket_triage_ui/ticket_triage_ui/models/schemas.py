from datetime import datetime 
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field

# 1. Definición de Enums
class CategoryEnum(str, Enum):
    IT = "IT"
    RRHH = "RRHH"
    LEGAL = "Legal"
    FINANZAS = "Finanzas"
    OPERATIONS = "Operaciones"
    COMERCIAL = "Comercial"

class UrgencyEnum(str, Enum):
    HIGH = "Alta"
    MEDIUM = "Media"
    LOW = "Baja"

class DepartmentEnum(str, Enum):
    IT_SUPPORT = "Soporte TI"
    HUMAN_RESOURCES = "Recursos Humanos"
    LEGAL_DEPT = "Legal y Cumplimiento"
    FINANCE_DEPT = "Contabilidad y Finanzas"
    LOGISTICS = "Operaciones y Logística"
    COMERCIAL = "Ventas y Desarrollo de Negocio"

class ProviderEnum(str, Enum):
    LOCAL = "local"
    GEMINI = "gemini"
    HF_API = "hf_api"
    HF_TRANSFORMERS = "hf_local"


# 2. Modelo de entrada para la Petición (CORREGIDO)
class TicketRequest(BaseModel):
    description: str = Field(..., description="Descripción del ticket enviada por el usuario")
    provider: ProviderEnum = Field(
        default=ProviderEnum.LOCAL, 
        description="Proveedor a utilizar: 'local', 'gemini', 'hf_api' o 'hf_local'"
    )


# 3. Modelo de parseo del JSON devuelto por el LLM
class TicketTriageOutput(BaseModel):
    category: CategoryEnum = Field(..., description="Categoría asignada")
    urgency: UrgencyEnum = Field(..., description="Nivel de urgencia")
    summary: str = Field(..., description="Resumen breve del incidente")
    department: DepartmentEnum = Field(..., description="Departamento asignado")
    thought_process: str = Field(..., description="Razonamiento paso a paso del modelo")


# 4. Modelo final devuelto por FastAPI (CORREGIDO)
class TicketResponse(BaseModel):
    category: CategoryEnum
    urgency: UrgencyEnum
    summary: str
    department: DepartmentEnum
    thought_process: str
    latency: float
    tokens_consumed: int
    provider: ProviderEnum


class TicketResponseDB(BaseModel):
    id: int
    description: str
    provider: ProviderEnum
    urgency: UrgencyEnum
    summary: str
    department_name: str
    thought_process: str
    latency: float
    tokens_consumed: int
    created_at: datetime
    user_email: str = "Anónimo"

    model_config = ConfigDict(from_attributes=True)

class StatsResponse(BaseModel):
    total_tickets: int
    avg_latency: float
    avg_tokens: int
    top_urgency: str
    top_department: str
    tickets_by_department: dict[str, int]
    tickets_by_urgency: dict[str, int]

class TicketUpdate(BaseModel):
    urgency: Optional[UrgencyEnum] = None
    department_name: Optional[str] = None

class RoleEnum(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: RoleEnum = RoleEnum.USER

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: RoleEnum

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: RoleEnum
    first_name: str | None = None
    last_name: str | None = None